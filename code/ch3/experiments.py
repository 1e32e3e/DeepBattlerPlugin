"""第三章第 3、4 节的单人实验：标准实力波动模型、缓存的模拟结果、检验力。

所有实验都用 model.simulate_player（单个玩家对校准对手池，排队噪声 σ_q=50），
结果缓存在 code/ch3/cache/player_*.npz。用法：
    python code/ch3/experiments.py          # 跑全部缺失的缓存
参数是示意值（正文给出范围），不是从真实数据校准的。
"""
from __future__ import annotations

import sys
import time
from dataclasses import replace
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import (PlayerModel, chain_fatigue, chain_hmm, chain_iid, chain_tilt,  # noqa: E402
                   cond_excess, count_wklk, lag_autocorr, longest_loss_runs, shuffle_within,
                   simulate_player, stat_block_dispersion, stat_lag1, stat_session_slope,
                   stat_tilt_slope)

CACHE = Path(__file__).resolve().parent / "cache"
SIGMA_Q = 50.0          # 单人模型的排队噪声
K_ELO = 20              # 单人模型的 Elo K：对手池校准（κ=1），b=cK/4≈0.029，与人群模拟 K=32、σ_q=100（κ≈0.64）相当
END_PROB = 1 / 8        # 疲劳 / 带休息的上头：每局后结束本次游玩的概率（平均每次 8 局）

# 标准模型（正文第 4 节的示意参数）
STANDARD = {
    "none": PlayerModel("none", label="无波动"),
    "iid": PlayerModel("iid", sd=100.0, label="(a) 逐局独立噪声"),
    "ar1": PlayerModel("ar1", sd=60.0, rho=0.9, label="(b) AR(1) 状态"),
    "hmm": PlayerModel("hmm", u_states=(0.0, -120.0), trans=(0.02, 0.10), label="(c) 两状态"),
    "tilt": PlayerModel("tilt", theta=30.0, cap=3, label="(d) 上头"),
    "tilt_break": PlayerModel("tilt", theta=30.0, cap=3, end_prob=END_PROB, label="(d') 上头+休息"),
    "fatigue": PlayerModel("fatigue", phi=6.0, end_prob=END_PROB, label="(e) 疲劳"),
}
ORDER = ["none", "iid", "ar1", "hmm", "tilt", "fatigue"]


def exact_chain(name: str):
    """K=0（评分不动）时模型对应的马尔可夫调制链；AR(1) 没有有限状态表示，返回 None。"""
    m = STANDARD[name]
    if m.kind in ("none", "iid"):
        return chain_iid(0.5)
    if m.kind == "hmm":
        a, b = m.trans
        return chain_hmm(m.u_states, [[1 - a, a], [b, 1 - b]], SIGMA_Q)
    if m.kind == "tilt":
        return chain_tilt(m.theta, m.cap, SIGMA_Q, break_prob=m.end_prob)
    if m.kind == "fatigue":
        return chain_fatigue(m.phi, m.end_prob, jmax=80, sigma_q=SIGMA_Q)
    return None


def _path(tag):
    return CACHE / f"player_{tag}.npz"


def _save(tag, out):
    CACHE.mkdir(parents=True, exist_ok=True)
    np.savez(_path(tag), **{k: np.asarray(v) for k, v in out.items()})


def _load(tag):
    z = np.load(_path(tag))
    return {k: (z[k].item() if z[k].shape == () else z[k]) for k in z.files}


def run_standard(name: str, K: float, M: int = 20000, T: int = 1000, seed: int = None):
    """一个标准模型在给定 K 下的全部汇总统计量（缓存）。"""
    tag = f"{name}_K{int(K)}"
    if _path(tag).exists():
        return _load(tag)
    if seed is None:
        base = 5000 + 17 * ORDER.index(name) if name in ORDER else 5900
        seed = base + int(K)
    t0 = time.time()
    rec = simulate_player(STANDARD[name], M=M, T=T, K=K, sigma_q=SIGMA_Q, seed=seed)
    y, p = rec["y"], rec["p"]
    rng = np.random.default_rng(seed + 1)
    W, L = cond_excess(p, rec["ws"], rec["ls"], kmax=8)
    sh = shuffle_within(y, rng)
    Lr = longest_loss_runs(y)
    Ls = longest_loss_runs(sh)
    out = dict(W=W, L=L, pbar=float(p.mean()), ybar=float(y.mean()),
               longest_hist=np.bincount(Lr, minlength=60)[:60],
               longest_hist_shuf=np.bincount(Ls, minlength=60)[:60],
               wl4=float(count_wklk(y, 4).mean()), wl4_shuf=float(count_wklk(sh, 4).mean()),
               wl5=float(count_wklk(y, 5).mean()), wl5_shuf=float(count_wklk(sh, 5).mean()),
               acf=np.array([lag_autocorr(y, h) for h in range(1, 21)]),
               acf_shuf=float(lag_autocorr(sh, 1)),
               runs_ge5=float(((rec["ls"][1:] == 4) & ~y[1:]).sum(0).mean()))
    # 疲劳：按本次游玩中的局序号统计真实胜率
    j = rec["j"]
    out["winrate_by_j"] = np.array([p[j == jj].mean() if (j == jj).any() else np.nan
                                    for jj in range(1, 21)])
    out["secs"] = time.time() - t0
    _save(tag, out)
    print(f"[{tag}] {out['secs']:.0f}s pbar {out['pbar']:.3f} W " + " ".join(f"{100*x:+.2f}" for x in W[:6])
          + " | L " + " ".join(f"{100*x:+.2f}" for x in L[:6])
          + f" | acf1 {out['acf'][0]:+.4f} | P10 {(Lr>=10).mean():.3f}/{(Ls>=10).mean():.3f}"
          f" | wl4 {out['wl4']:.2f}/{out['wl4_shuf']:.2f}", flush=True)
    return out


def run_examples(seed: int = 4242, T: int = 160):
    """示例轨迹：每个模型 1 名玩家，K=K_ELO，记录 u、评分 R、单局胜率与结果（从一次游玩的开头截取）。"""
    tag = "examples"
    if _path(tag).exists():
        return _load(tag)
    out = {}
    for name in ["ar1", "hmm", "tilt", "fatigue"]:
        rec = simulate_player(STANDARD[name], M=1, T=T + 80, K=K_ELO, sigma_q=SIGMA_Q, burn=400,
                              seed=seed + ORDER.index(name), record_R=True)
        i0 = int(np.argmax(rec["j"][:, 0] == 1)) if name == "fatigue" else 0
        for k in ("u", "R", "p", "y", "j"):
            out[f"{name}_{k}"] = rec[k][i0:i0 + T, 0]
    _save(tag, out)
    return out


def run_event_study(K_list=(10, 32), M=40000, T=400, k=5, hmin=-12, hmax=20):
    """诚实 Elo 的过冲：以“最近 k 局全胜”的时刻为 0 点，平均评分误差 R - s 的走势。"""
    tag = "event_study"
    if _path(tag).exists():
        return _load(tag)
    out = {}
    for K in K_list:
        rec = simulate_player(STANDARD["none"], M=M, T=T, K=K, sigma_q=SIGMA_Q, seed=600 + K,
                              record_R=True)
        R = rec["R"].astype(np.float64)
        ws = rec["ws"]
        hs = np.arange(hmin, hmax + 1)
        prof = np.empty(hs.size)
        t_idx = np.arange(-hmin, T - hmax)
        mask = ws[t_idx] >= k
        for i, h in enumerate(hs):
            prof[i] = R[t_idx + h][mask].mean()
        out[f"K{K}_h"] = hs
        out[f"K{K}_mean_err"] = prof
        out[f"K{K}_sd_err"] = R.std()
    _save(tag, out)
    return out


def run_ar_absorption(rhos=(0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99), Ks=(10, 20, 32), sd=60.0,
                      M=4000, T=3000):
    """AR(1) 状态被评分吸收的比例：(Var(u - R) - σ_e²) / Var(u)，以及结果自相关。"""
    tag = "ar_absorption"
    if _path(tag).exists():
        return _load(tag)
    out = dict(rhos=np.array(rhos), Ks=np.array(Ks))
    for K in Ks:
        base = simulate_player(STANDARD["none"], M=M, T=T, K=K, sigma_q=SIGMA_Q, seed=700 + K,
                               record_R=True)
        var_e = base["R"].astype(np.float64).var()
        ret = []
        for i, rho in enumerate(rhos):
            rec = simulate_player(PlayerModel("ar1", sd=sd, rho=rho), M=M, T=T, K=K,
                                  sigma_q=SIGMA_Q, seed=800 + 10 * i + K, record_R=True)
            D = rec["u"].astype(np.float64) - rec["R"].astype(np.float64)
            ret.append((D.var() - var_e) / rec["u"].astype(np.float64).var())
        out[f"retained_K{K}"] = np.array(ret)
        out[f"var_e_K{K}"] = var_e
    # 结果自相关：AR(0.9, 60) 在 K=0 / K_ELO 下，以及无波动 K_ELO
    for tag2, mdl, K in (("ar_K0", PlayerModel("ar1", sd=sd, rho=0.9), 0),
                         ("ar_Kelo", PlayerModel("ar1", sd=sd, rho=0.9), K_ELO),
                         ("none_Kelo", STANDARD["none"], K_ELO)):
        rec = simulate_player(mdl, M=20000, T=1000, K=K, sigma_q=SIGMA_Q, seed=900 + K + len(tag2))
        out[f"acf_{tag2}"] = np.array([lag_autocorr(rec["y"], h) for h in range(1, 21)])
    _save(tag, out)
    return out


# ---- 单人检验力 ----

POWER_T = np.array([100, 200, 500, 1000, 2000, 4000])
TESTS = {"lag1": "滞后 1 自相关", "tilt": "对连败长度回归", "block": "10 局分块离散度",
         "session": "对局序号回归"}
NATURAL_TEST = {"none": "lag1", "iid": "lag1", "ar1": "block", "hmm": "block", "tilt": "tilt",
                "tilt_break": "tilt", "fatigue": "session"}


def _stats(rec, Tp):
    y = rec["y"][:Tp]
    return dict(lag1=stat_lag1(y), tilt=stat_tilt_slope(y, rec["ls"][:Tp]),
                block=stat_block_dispersion(y), session=stat_session_slope(y, rec["j"][:Tp]))


def run_power(M=3000, M_null=8000, Tmax=4000, models=("none", "ar1", "hmm", "tilt", "tilt_break",
                                                        "fatigue"), Ks=(0, K_ELO)):
    """每个模型、每个 K、每个样本量 T 下四种检验的检验力（双侧 5%，零分布 = 无波动、K=0 的 i.i.d.）。

    疲劳与带休息的上头需要“本次游玩”的划分；零分布与其他模型共用同样的休息过程（END_PROB），
    这样“对局序号”在零分布下也有定义。
    """
    tag = "power"
    if _path(tag).exists():
        return _load(tag)
    null_model = PlayerModel("none", end_prob=END_PROB)
    rec0 = simulate_player(null_model, M=M_null, T=Tmax, K=0, sigma_q=SIGMA_Q, seed=1001)
    crit = {}
    for Tp in POWER_T:
        st = _stats(rec0, Tp)
        for tname, v in st.items():
            crit[(tname, Tp)] = np.quantile(v, [0.025, 0.975])
    del rec0
    out = dict(T=POWER_T)
    for name in models:
        # 休息过程只影响“局序号”和上头的归零；不带休息的上头保持 end_prob=0
        mdl = STANDARD[name] if name == "tilt" else replace(STANDARD[name], end_prob=END_PROB)
        for K in Ks:
            rec = simulate_player(mdl, M=M, T=Tmax, K=K, sigma_q=SIGMA_Q,
                                  seed=2000 + 31 * len(name) + K)
            for tname in TESTS:
                pw = []
                for Tp in POWER_T:
                    v = _stats(rec, Tp)[tname]
                    lo, hi = crit[(tname, Tp)]
                    pw.append(np.mean((v < lo) | (v > hi)))
                out[f"{name}_K{K}_{tname}"] = np.array(pw)
            print(f"[power {name} K{K}] " + " ".join(
                f"{t}:" + "/".join(f"{x:.2f}" for x in out[f'{name}_K{K}_{t}']) for t in TESTS),
                flush=True)
            del rec
    _save(tag, out)
    return out


def opponent_residuals(rec, Tp, iters=12):
    """用“对手评分”做协变量、把自身实力当作常数 ŝ（最大似然）时的残差 r_t = y_t - F(ŝ - opp_t)。

    单人模型里对手评分 opp_t = R_t + η_t 可由 u_t 与 p_t 反推：opp_t = u_t - 400·log10(p_t/(1-p_t))。
    真实数据中 opp_t 直接可得（对手评分或敌队均分）。返回 (r, 方差权重 F(1-F))。
    """
    y = rec["y"][:Tp].astype(np.float64)
    p = np.clip(rec["p"][:Tp].astype(np.float64), 1e-9, 1 - 1e-9)
    opp = rec["u"][:Tp].astype(np.float64) - 400.0 * np.log10(p / (1 - p))
    s_hat = np.zeros(y.shape[1])
    for _ in range(iters):            # 牛顿法解 sum_t [y_t - F(s - opp_t)] = 0
        f = 1.0 / (1.0 + 10.0 ** (-(s_hat[None, :] - opp) / 400.0))
        g = (y - f).sum(0)
        h = (f * (1 - f)).sum(0) * np.log(10) / 400.0
        s_hat = s_hat + g / np.maximum(h, 1e-9)
    f = 1.0 / (1.0 + 10.0 ** (-(s_hat[None, :] - opp) / 400.0))
    return y - f, f * (1 - f)


def _resid_stats(rec, Tp, block=10):
    r, v = opponent_residuals(rec, Tp)
    T, M = r.shape
    lag = (r[:-1] * r[1:]).sum(0) / np.maximum((r * r).sum(0), 1e-12)
    x = np.minimum(rec["ls"][:Tp], 3).astype(np.float64)
    xm = x - x.mean(0)
    tilt = (xm * r).sum(0) / np.maximum((xm * xm).sum(0), 1e-12)
    nb = T // block
    bs = r[:nb * block].reshape(nb, block, M).sum(1)
    bv = v[:nb * block].reshape(nb, block, M).sum(1)
    disp = (bs ** 2).mean(0) / np.maximum(bv.mean(0), 1e-12)
    j = np.minimum(rec["j"][:Tp], 15).astype(np.float64)
    jm = j - j.mean(0)
    sess = (jm * r).sum(0) / np.maximum((jm * jm).sum(0), 1e-12)
    return dict(lag1=lag, tilt=tilt, block=disp, session=sess)


def run_power_resid(M=3000, M_null=8000, Tmax=4000, models=("ar1", "hmm", "tilt", "tilt_break",
                                                             "fatigue")):
    """Elo（K=K_ELO）下，用对手评分残差做同样四种检验的检验力；零分布 = 无波动的诚实 Elo。"""
    tag = "power_resid"
    if _path(tag).exists():
        return _load(tag)
    null = replace(STANDARD["none"], end_prob=END_PROB)
    rec0 = simulate_player(null, M=M_null, T=Tmax, K=K_ELO, sigma_q=SIGMA_Q, seed=3001)
    crit = {}
    for Tp in POWER_T:
        for tname, v in _resid_stats(rec0, Tp).items():
            crit[(tname, Tp)] = np.quantile(v, [0.025, 0.975])
    del rec0
    out = dict(T=POWER_T)
    for name in models:
        mdl = STANDARD[name] if name == "tilt" else replace(STANDARD[name], end_prob=END_PROB)
        rec = simulate_player(mdl, M=M, T=Tmax, K=K_ELO, sigma_q=SIGMA_Q,
                              seed=4000 + 31 * len(name))
        for tname in TESTS:
            pw = []
            for Tp in POWER_T:
                v = _resid_stats(rec, Tp)[tname]
                lo, hi = crit[(tname, Tp)]
                pw.append(np.mean((v < lo) | (v > hi)))
            out[f"{name}_{tname}"] = np.array(pw)
        print(f"[power_resid {name}] " + " ".join(
            f"{t}:" + "/".join(f"{x:.2f}" for x in out[f'{name}_{t}']) for t in TESTS), flush=True)
        del rec
    _save(tag, out)
    return out


def games_for_power(T, power, target=0.8):
    """在 log(T) 上线性插值，求检验力达到 target 所需局数；达不到返回 nan。"""
    power = np.asarray(power, float)
    if power[-1] < target:
        return np.nan
    i = int(np.argmax(power >= target))
    if i == 0:
        return float(T[0])
    x0, x1 = np.log(T[i - 1]), np.log(T[i])
    y0, y1 = power[i - 1], power[i]
    return float(np.exp(x0 + (target - y0) / (y1 - y0) * (x1 - x0)))


if __name__ == "__main__":
    for nm in ORDER + ["tilt_break"]:
        for K in (0, K_ELO):
            run_standard(nm, K)
    run_examples()
    run_event_study()
    run_ar_absorption()
    run_power()
    run_power_resid()
