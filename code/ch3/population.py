"""第三章的人群 Monte Carlo：闭合人群、按分匹配（1v1 / 5v5）、上头、操纵规则。

模型（与正文附录的参数表一致）：
- 真实实力 s_i ~ N(0, 200²)，N 名玩家，评分从 0 起步；每轮所有人各打一局。
- 匹配键 = 评分 R + N(0, σ_q²) 排队噪声 [+ 操纵偏移]；1v1 排序后相邻配对，5v5 每 10 人一个房间。
- 5v5 分队：random（房间内随机分两队）、snake（按评分 [+ 操纵偏移] 蛇形 ABBAABBAAB）、
  balanced（126 种分法中两队评分均值最接近的一种）或 assort（M4：在两队评分均值差不超过
  lq_cap 的分法中，选“连胜 ≥3 者尽量同队、连败 ≥3 者尽量在另一队”的一种）。
- 团队强度：team="mean" 为 5 人有效实力的均值（均值模型，默认）；team="sum" 为和/√5（加和模型）。
  单局胜率 F(差)。Elo：R ← R + K(y - F(评分差))，评分差与结果用同一团队模型，团队各成员同增减。
- 上头：有效实力 = s - θ·min(当前连败, m)。AR 状态：有效实力再加 u_t，u_t = ρ u_{t-1} + ε_t，平稳标准差 ar_sd。
- 连胜加分（1v1）：赛前已连胜 ≥ bonus_from-1 局者若再赢，本局评分收益 ×bonus（只乘赢家；匹配用的就是这个评分）。
- 爬分实验（climb_drop>0）：预热结束时把 climb_n 名随机玩家的评分压低 climb_drop 个实力分（按当时的评分–实力
  斜率换算），记录他们“评分折算的实力 − 真实实力”的平均差距随局数的变化。
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
               split="random", team="mean", tilt=0.0, tilt_cap=3, ar_sd=0.0, ar_rho=0.0,
               bonus=1.0, bonus_from=3, manip="none", manip_on="key", manip_k=3, manip_d=0.0,
               lq_cap=25.0, climb_drop=0.0, climb_n=500, seed=1)

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
    # ---- 第二轮补充 ----
    # M3 的诚实对照：同样按评分蛇形分队、不操纵
    "t5_snake": dict(mode="5v5", sigma=250, split="snake", seed=3151),
    # 加和团队模型（随机分队）：个人评分误差按 1/√n 而不是 1/n 进入胜率
    "t5_sum": dict(mode="5v5", sigma=250, team="sum", seed=3152),
    # M4 社区说的 loser queue：连败者与连败者同队、对上连胜者（保持两队评分均值差 ≤ 25）
    "t5_balanced": dict(mode="5v5", sigma=250, split="balanced", seed=3153),
    "t5_assort": dict(mode="5v5", sigma=250, split="assort", lq_cap=25.0, seed=3154),
    "t5_balanced_tilt": dict(mode="5v5", sigma=250, split="balanced", tilt=30, seed=3155),
    "t5_assort_tilt": dict(mode="5v5", sigma=250, split="assort", lq_cap=25.0, tilt=30, seed=3156),
    # 慢状态与连胜加分（1v1，K=32，σ_q=100）
    "ar09_elo32": dict(ar_sd=60.0, ar_rho=0.9, seed=3161),
    "streakbonus_elo32": dict(bonus=2.0, bonus_from=3, seed=3162),
    # 爬分（H3 “出不去”）：评分比实力低 150 分的玩家多久追回
    "climb_elo32": dict(T=1000, climb_drop=150.0, seed=3171),
    "climb_t5": dict(mode="5v5", sigma=250, T=1000, climb_drop=150.0, seed=3172),
    "climb_t5sum": dict(mode="5v5", sigma=250, team="sum", T=1000, climb_drop=150.0, seed=3173),
}

# 10 人房间分成两队的全部 126 种分法（含第 0 人的一队记为 A）
_PARTS = np.array([[1 if i in comb else 0 for i in range(10)]
                   for comb in __import__("itertools").combinations(range(10), 5) if 0 in comb], bool)
_IDX_A = np.array([np.flatnonzero(m) for m in _PARTS])
_IDX_B = np.array([np.flatnonzero(~m) for m in _PARTS])
_SIGN = np.where(_PARTS, 1.0, -1.0)            # A 为 +1、B 为 -1


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
    u = rng.normal(0, c["ar_sd"], N) if c["ar_sd"] > 0 else np.zeros(N)
    eps_sd = c["ar_sd"] * np.sqrt(1 - c["ar_rho"] ** 2)
    rec = dict(y=np.zeros((T, N), bool), p=np.zeros((T, N), np.float32),
               ws=np.zeros((T, N), np.int16), ls=np.zeros((T, N), np.int16),
               dR=np.zeros((T, N), np.float32), dS=np.zeros((T, N), np.float32),
               E=np.zeros((T, N), np.float32), R=np.zeros((T, N), np.float32))
    climb = c["climb_drop"] > 0
    cohort, climb_gap = None, []
    if team:
        rec.update(mates=np.zeros((T, N), np.float32), weakest_mate=np.zeros((T, N), bool),
                   weakest_me=np.zeros((T, N), bool), team_weaker=np.zeros((T, N), bool))
    slope_trace = []
    for r in range(burn + T):
        if climb and r == burn:       # 爬分实验：把一批随机玩家的评分压低 climb_drop 个实力分
            cohort = rng.choice(N, c["climb_n"], replace=False)
            lam_now = float(np.polyfit(s, R, 1)[0])
            R[cohort] -= c["climb_drop"] * lam_now
        if climb and r >= burn:
            others = np.ones(N, bool)
            others[cohort] = False
            lam_now, a_now = np.polyfit(s[others], R[others], 1)
            climb_gap.append(float(((R[cohort] - a_now) / lam_now - s[cohort]).mean()))
        if r >= burn:
            rec["R"][r - burn] = R
        s_eff = s + u - c["tilt"] * np.minimum(ls, c["tilt_cap"])
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
            if c["bonus"] != 1.0:     # 连胜加分只乘赢家的收益
                ga = np.where(win_a & (ws[a] + 1 >= c["bonus_from"]), c["bonus"], 1.0)
                gb = np.where(~win_a & (ws[b] + 1 >= c["bonus_from"]), c["bonus"], 1.0)
                da = np.where(win_a, delta * ga, delta)
                db = np.where(win_a, -delta, -delta * gb)
            else:
                da, db = delta, -delta
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
            R[a] += da
            R[b] += db
            win = np.empty(N, bool)
            win[a] = win_a
            win[b] = ~win_a
        else:
            lob = order.reshape(-1, 10)
            if c["split"] == "random":
                lob = np.take_along_axis(lob, np.argsort(rng.random(lob.shape), axis=1), 1)
                A, B = lob[:, :5], lob[:, 5:]
            elif c["split"] == "snake":   # 按评分（操纵时加偏移）蛇形分队
                mmr = R + (shift if c["manip_on"] == "split" else 0.0)
                srt = np.take_along_axis(lob, np.argsort(-(mmr[lob] + 1e-6 * rng.random(lob.shape)),
                                                         axis=1), 1)
                A, B = srt[:, [0, 3, 4, 7, 8]], srt[:, [1, 2, 5, 6, 9]]
            else:   # balanced / assort：在 126 种分法中选
                dmean = np.abs(R[lob] @ _SIGN.T) / 5.0               # 两队评分均值差 |ΔR|
                if c["split"] == "balanced":
                    best = dmean.argmin(1)
                else:
                    z = ((ws >= c["manip_k"]).astype(float) - (ls >= c["manip_k"]))[lob]
                    score = np.abs(z @ _SIGN.T)                       # 连胜者同队、连败者在另一队
                    cap = np.maximum(c["lq_cap"], dmean.min(1, keepdims=True))
                    obj = np.where(dmean <= cap, score * 1e4 - dmean, -np.inf)
                    best = obj.argmax(1)
                A = np.take_along_axis(lob, _IDX_A[best], 1)
                B = np.take_along_axis(lob, _IDX_B[best], 1)
            if c["team"] == "sum":
                dS_ = (s_eff[A].sum(1) - s_eff[B].sum(1)) / np.sqrt(5.0)
                dR_ = (R[A].sum(1) - R[B].sum(1)) / np.sqrt(5.0)
            else:
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
        if c["ar_sd"] > 0:
            u = c["ar_rho"] * u + rng.normal(0, eps_sd, N)
        if (r + 1) % 500 == 0:
            slope_trace.append((r + 1, float(np.polyfit(s, R, 1)[0])))
    out = analyse(c, s, R, rec, np.random.default_rng(c["seed"] + 777), slope_trace)
    if climb:
        out["climb_gap"] = np.array(climb_gap)
    return out


def _excess(val, mask, mean_by_player):
    if not mask.any():
        return np.nan
    return float((val[mask] - np.broadcast_to(mean_by_player, val.shape)[mask]).mean())


def _within_corr(y, x):
    """按玩家去均值后合并的相关系数 corr(y_t, x_t)（每列一名玩家）。"""
    y = y.astype(np.float64)
    x = x.astype(np.float64)
    y = y - y.mean(0)
    x = x - x.mean(0)
    return float((x * y).sum() / np.sqrt((x * x).sum() * (y * y).sum()))


def form_stats(y, p, R=None, windows=(20, 35, 50)):
    """近期战绩与自身评分两类“回拉”统计量（单人检验的对口统计量，见正文“单个玩家能否察觉”）。

    - form{w}：y_t 与“前 w 局胜场”的玩家内部相关，n*_form = 7.85/corr²；
    - form20_hi / form20_lo：前 20 局 14 胜 6 负 / 6 胜 14 负之后，下一局真实胜率相对自身平均的超额；
      form20_hi2 / lo2 为“≥14 胜 / ≤6 胜”；
    - ownR：y_t 与赛前自身评分（减去该玩家平均评分）的玩家内部相关（需要 R）。
    """
    from model import Z_TWO_SIDED_80
    out = {}
    yi = y.astype(np.int16)
    cs = np.concatenate([np.zeros((1, y.shape[1]), np.int32), np.cumsum(yi, 0, dtype=np.int32)], 0)
    pbar = p.mean(0, dtype=np.float64)
    for w in windows:
        prev = (cs[w:-1] - cs[:-w - 1]).astype(np.float32)      # 第 t 局之前 w 局的胜场，t = w..T-1
        r = _within_corr(y[w:], prev)
        out[f"form{w}"] = r
        out[f"nstar_form{w}"] = Z_TWO_SIDED_80 / r ** 2
        if w == 20:
            pp = p[w:]
            for tag, m in (("hi", prev == 14), ("lo", prev == 6), ("hi2", prev >= 14), ("lo2", prev <= 6)):
                out[f"form20_{tag}"] = _excess(pp, m, pbar)
                out[f"form20_{tag}_share"] = float(m.mean())
    if R is not None:
        r = _within_corr(y, R)
        out["ownR"] = r
        out["nstar_ownR"] = Z_TWO_SIDED_80 / r ** 2
    return out


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
    out.update(form_stats(y, p, rec.get("R")))
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
