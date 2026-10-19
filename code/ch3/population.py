"""第三章的人群 Monte Carlo：闭合人群、按分匹配（1v1 / 5v5）、上头、操纵规则。

模型（与正文附录的参数表一致）：
- 真实实力 s_i ~ N(0, 200²)，N 名玩家，评分从 0 起步；每轮所有人各打一局。
- 匹配键 = 评分 R + N(0, σ_q²) 排队噪声 [+ 操纵偏移]；1v1 排序后相邻配对，5v5 每 10 人一个房间。
- 5v5 分队：random（房间内随机分两队）或 snake（按评分 [+ 操纵偏移] 蛇形 ABBAABBAAB）。
- 团队强度 = 5 人有效实力的均值；单局胜率 F(差)。Elo：R ← R + K(y - F(评分差))，团队各成员同增减。
- 上头：有效实力 = s - θ·min(当前连败, m)。
- 操纵：key（匹配键偏移）或 split（分队时把评分当作偏移后的值）；sym 为“连胜 ≥k0 +δ、连败 ≥k0 -δ”，
  asym 只惩罚连胜。

预热 burn 轮后记录 T 局，只保存汇总统计量到 code/ch3/cache/pop_<名称>.npz。
用法：python code/ch3/population.py [名称 ...]（不给名称则跑全部缺失的场景）。一次只跑一个进程。
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import (Z_TWO_SIDED_80, count_wklk, elo_F, lag_autocorr,  # noqa: E402
                   longest_loss_runs, shuffle_within)

CACHE = Path(__file__).resolve().parent / "cache"

DEFAULT = dict(N=10000, burn=1500, T=2000, K=32.0, sigma=100.0, mode="1v1", match="rating",
               split="random", tilt=0.0, tilt_cap=3, manip="none", manip_on="key", manip_k=3,
               manip_d=0.0, seed=1)

SCENARIOS = {
    # 诚实 Elo，1v1
    "elo10": dict(K=10, seed=3101),
    "elo32": dict(K=32, seed=3102),
    # 排队噪声敏感性（K=32）
    "elo32_s25": dict(sigma=25, seed=3111),
    "elo32_s50": dict(sigma=50, seed=3112),
    "elo32_s200": dict(sigma=200, seed=3114),
    "elo32_s400": dict(sigma=400, seed=3115),
    # 5v5
    "t5_elo32": dict(mode="5v5", sigma=250, seed=3121),
    "t5_random": dict(mode="5v5", match="random", seed=3122),
    # 上头（人群版，便于与操纵对照）
    "tilt30_elo32": dict(tilt=30, seed=3131),
    # 操纵
    "manip_sym": dict(manip="sym", manip_on="key", manip_d=100, seed=3141),
    "manip_asym": dict(manip="asym", manip_on="key", manip_d=100, seed=3142),
    "t5_loserq": dict(mode="5v5", sigma=250, split="snake", manip="sym", manip_on="split",
                      manip_d=300, seed=3143),
}


def simulate(cfg: dict):
    """运行一个场景，返回汇总统计量 dict。"""
    c = dict(DEFAULT)
    c.update(cfg)
    rng = np.random.default_rng(c["seed"])
    N, burn, T, K = c["N"], c["burn"], c["T"], c["K"]
    s = rng.normal(0, 200, N)
    R = np.zeros(N)
    ws = np.zeros(N, np.int32)
    ls = np.zeros(N, np.int32)
    team = c["mode"] == "5v5"
    rec = dict(y=np.zeros((T, N), bool), p=np.zeros((T, N), np.float32),
               ws=np.zeros((T, N), np.int16), ls=np.zeros((T, N), np.int16),
               dR=np.zeros((T, N), np.float32), dS=np.zeros((T, N), np.float32),
               E=np.zeros((T, N), np.float32))
    if team:
        rec.update(mates=np.zeros((T, N), np.float32), weakest_mate=np.zeros((T, N), bool),
                   weakest_me=np.zeros((T, N), bool), team_weaker=np.zeros((T, N), bool))
    slope_trace = []
    for r in range(burn + T):
        s_eff = s - c["tilt"] * np.minimum(ls, c["tilt_cap"])
        if c["manip"] == "sym":
            shift = c["manip_d"] * ((ws >= c["manip_k"]).astype(float) - (ls >= c["manip_k"]))
        elif c["manip"] == "asym":
            shift = c["manip_d"] * (ws >= c["manip_k"]).astype(float)
        else:
            shift = np.zeros(N)
        key_shift = shift if c["manip_on"] == "key" else 0.0
        if c["match"] == "random":
            order = rng.permutation(N)
        else:
            order = np.argsort(R + rng.normal(0, c["sigma"], N) + key_shift)
        if not team:
            a, b = order[0::2], order[1::2]
            pa = elo_F(s_eff[a] - s_eff[b])
            Ea = elo_F(R[a] - R[b])
            win_a = rng.random(a.size) < pa
            delta = K * (win_a - Ea)
            if r >= burn:
                t = r - burn
                rec["y"][t, a] = win_a
                rec["y"][t, b] = ~win_a
                rec["p"][t, a] = pa
                rec["p"][t, b] = 1 - pa
                rec["E"][t, a] = Ea
                rec["E"][t, b] = 1 - Ea
                rec["dR"][t, a] = R[b] - R[a]
                rec["dR"][t, b] = R[a] - R[b]
                rec["dS"][t, a] = s[b] - s[a]
                rec["dS"][t, b] = s[a] - s[b]
            R[a] += delta
            R[b] -= delta
            win = np.empty(N, bool)
            win[a] = win_a
            win[b] = ~win_a
        else:
            lob = order.reshape(-1, 10)
            if c["split"] == "random":
                lob = np.take_along_axis(lob, np.argsort(rng.random(lob.shape), axis=1), 1)
                A, B = lob[:, :5], lob[:, 5:]
            else:   # 按评分（操纵时加偏移）蛇形分队
                mmr = R + (shift if c["manip_on"] == "split" else 0.0)
                srt = np.take_along_axis(lob, np.argsort(-(mmr[lob] + 1e-6 * rng.random(lob.shape)),
                                                         axis=1), 1)
                A, B = srt[:, [0, 3, 4, 7, 8]], srt[:, [1, 2, 5, 6, 9]]
            dS_ = s_eff[A].mean(1) - s_eff[B].mean(1)
            dR_ = R[A].mean(1) - R[B].mean(1)
            pA = elo_F(dS_)
            EA = elo_F(dR_)
            winA = rng.random(pA.size) < pA
            delta = K * (winA - EA)
            if r >= burn:
                t = r - burn
                rec["y"][t, A] = winA[:, None]
                rec["y"][t, B] = ~winA[:, None]
                rec["p"][t, A] = pA[:, None]
                rec["p"][t, B] = (1 - pA)[:, None]
                rec["E"][t, A] = EA[:, None]
                rec["E"][t, B] = (1 - EA)[:, None]
                mA, mB = R[A].mean(1), R[B].mean(1)
                rec["dR"][t, A] = (mB - mA)[:, None]
                rec["dR"][t, B] = (mA - mB)[:, None]
                tA, tB = s[A].mean(1), s[B].mean(1)
                rec["dS"][t, A] = (tB - tA)[:, None]
                rec["dS"][t, B] = (tA - tB)[:, None]
                rec["mates"][t, A] = (R[A].sum(1)[:, None] - R[A]) / 4 - R[A]
                rec["mates"][t, B] = (R[B].sum(1)[:, None] - R[B]) / 4 - R[B]
                th = s[np.concatenate([A, B], 1)]
                wk = th.argmin(1)
                pos = np.arange(5)[None, :]
                inA = (wk < 5)[:, None]
                rec["weakest_mate"][t, A] = inA & (wk[:, None] != pos)
                rec["weakest_mate"][t, B] = ~inA & ((wk - 5)[:, None] != pos)
                rec["weakest_me"][t, A] = wk[:, None] == pos
                rec["weakest_me"][t, B] = (wk - 5)[:, None] == pos
                rec["team_weaker"][t, A] = (tA < tB)[:, None]
                rec["team_weaker"][t, B] = (tB < tA)[:, None]
            R[A] += delta[:, None]
            R[B] -= delta[:, None]
            win = np.empty(N, bool)
            win[A] = winA[:, None]
            win[B] = ~winA[:, None]
        if r >= burn:
            t = r - burn
            rec["ws"][t] = ws
            rec["ls"][t] = ls
        ws = np.where(win, ws + 1, 0)
        ls = np.where(win, 0, ls + 1)
        if (r + 1) % 500 == 0:
            slope_trace.append((r + 1, float(np.polyfit(s, R, 1)[0])))
    return analyse(c, s, R, rec, np.random.default_rng(c["seed"] + 777), slope_trace)


def _excess(val, mask, mean_by_player):
    if not mask.any():
        return np.nan
    return float((val[mask] - np.broadcast_to(mean_by_player, val.shape)[mask]).mean())


def analyse(c, s, R, rec, rng, slope_trace, kmax=8):
    y, p = rec["y"], rec["p"]
    T, N = y.shape
    pbar = p.mean(0, dtype=np.float64)
    out = dict(cfg=str(c), slope_trace=np.array(slope_trace))
    keys = ["W", "L", "pooledW", "pooledL", "oppR_W", "oppR_L", "oppS_W", "oppS_L", "E_W", "E_L"]
    arr = {k: np.full(kmax, np.nan) for k in keys}
    if "mates" in rec:
        arr["mates_W"] = np.full(kmax, np.nan)
        arr["mates_L"] = np.full(kmax, np.nan)
        mtbar = rec["mates"].mean(0, dtype=np.float64)
    dRbar = rec["dR"].mean(0, dtype=np.float64)
    dSbar = rec["dS"].mean(0, dtype=np.float64)
    Ebar = rec["E"].mean(0, dtype=np.float64)
    for k in range(1, kmax + 1):
        mW = rec["ws"] >= k
        mL = rec["ls"] >= k
        i = k - 1
        arr["W"][i] = _excess(p, mW, pbar)
        arr["L"][i] = _excess(p, mL, pbar)
        arr["pooledW"][i] = y[mW].mean()
        arr["pooledL"][i] = y[mL].mean()
        arr["oppR_W"][i] = _excess(rec["dR"], mW, dRbar)
        arr["oppR_L"][i] = _excess(rec["dR"], mL, dRbar)
        arr["oppS_W"][i] = _excess(rec["dS"], mW, dSbar)
        arr["oppS_L"][i] = _excess(rec["dS"], mL, dSbar)
        arr["E_W"][i] = _excess(rec["E"], mW, Ebar)
        arr["E_L"][i] = _excess(rec["E"], mL, Ebar)
        if "mates" in rec:
            arr["mates_W"][i] = _excess(rec["mates"], mW, mtbar)
            arr["mates_L"][i] = _excess(rec["mates"], mL, mtbar)
    out.update(arr)
    # 滞后 1 自相关，并扣除按玩家去均值造成的 -1/T 偏差（用打乱序列估计）
    rho = lag_autocorr(y)
    rho_sh = lag_autocorr(shuffle_within(y, rng))
    out.update(rho1=rho, rho1_shuffled=rho_sh, rho1_corr=rho - rho_sh,
               n_detect=Z_TWO_SIDED_80 / (rho - rho_sh) ** 2)
    # 连败统计：两个 1000 局半段，实际 vs 玩家内打乱
    stats = {}
    for h in range(T // 1000):
        yh = y[h * 1000:(h + 1) * 1000]
        sh = shuffle_within(yh, rng)
        for tag, arr_ in (("real", yh), ("shuf", sh)):
            L = longest_loss_runs(arr_)
            for nm, val in (("mean_longest", L.mean()), ("P10", (L >= 10).mean()),
                            ("P7", (L >= 7).mean()), ("wl4", count_wklk(arr_, 4).mean()),
                            ("wl5", count_wklk(arr_, 5).mean())):
                stats.setdefault(f"{tag}_{nm}", []).append(float(val))
            if h == 0:
                out[f"{tag}_longest_hist"] = np.bincount(L, minlength=40)[:40]
    for k_, v in stats.items():
        out[k_] = float(np.mean(v))
    wr = y.mean(0)
    out.update(sd_winrate=float(wr.std()), pct_45_55=float(np.mean((wr >= .45) & (wr <= .55))),
               corr_R_s=float(np.corrcoef(R, s)[0, 1]), slope_R_s=float(np.polyfit(s, R, 1)[0]),
               slope_s_R=float(np.polyfit(R, s, 1)[0]))
    if "weakest_mate" in rec:
        for nm in ("weakest_mate", "weakest_me", "team_weaker"):
            a = rec[nm]
            out[f"{nm}_loss"] = float(a[~y].mean())
            out[f"{nm}_win"] = float(a[y].mean())
            out[f"{nm}_all"] = float(a.mean())
    return out


def cache_path(name: str) -> Path:
    return CACHE / f"pop_{name}.npz"


def load(name: str) -> dict:
    """读取缓存；没有就现跑（较慢，约 1–3 分钟）。"""
    path = cache_path(name)
    if not path.exists():
        run([name])
    z = np.load(path, allow_pickle=False)
    return {k: (z[k].item() if z[k].shape == () else z[k]) for k in z.files}


def run(names):
    CACHE.mkdir(parents=True, exist_ok=True)
    for nm in names:
        t0 = time.time()
        out = simulate(SCENARIOS[nm])
        out["secs"] = time.time() - t0
        np.savez(cache_path(nm), **{k: np.asarray(v) for k, v in out.items()})
        print(f"[{nm}] {out['secs']:.0f}s  W1..W6 " + " ".join(f"{100 * x:+.2f}" for x in out["W"][:6])
              + f" | L5 {100 * out['L'][4]:+.2f} | oppR_W5 {out['oppR_W'][4]:+.1f} oppS_W5 "
              f"{out['oppS_W'][4]:+.1f} | rho {out['rho1']:+.4f} corr {out['rho1_corr']:+.4f} "
              f"n* {out['n_detect']:.0f} | slope {out['slope_R_s']:.2f} corr {out['corr_R_s']:.3f} | "
              f"P10 {out['real_P10']:.3f}/{out['shuf_P10']:.3f} wl4 {out['real_wl4']:.2f}/"
              f"{out['shuf_wl4']:.2f} wl5 {out['real_wl5']:.3f}/{out['shuf_wl5']:.3f}"
              + (f" | mates_W5 {out['mates_W'][4]:+.1f} weakest {out['weakest_mate_loss']:.3f}/"
                 f"{out['weakest_mate_win']:.3f}" if "mates_W" in out else ""),
              flush=True)


if __name__ == "__main__":
    todo = sys.argv[1:] or [n for n in SCENARIOS if not cache_path(n).exists()]
    run(todo)
