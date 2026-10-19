"""图 2.2："五五开"的一局，真实胜率并不是 50%。

(a) 1v1：从随机匹配 Elo 的稳态评分表中，把评分相邻的两人配成一局（系统预测胜率≈50%），
    看真实胜率 p = F(s_A - s_B) 的分布；曲线是理论密度（Δs ~ N(0, 2τ²σ_e²/(τ²+σ_e²))）。
(b) 5v5（加和模型）：按 R + N(0,100²) 排序每 10 人成一局，在 126 种分队中选两队评分和最接近的一种；
    比较系统预测胜率、真实团队胜率、以及随机分配位置后"对位单挑"的真实胜率。
参数：10,000 人，τ=200，K=16/32，评分取第 3000 轮的稳态评分表（模拟见 model.EXPERIMENTS）。
运行：python code/ch2/fig_fair_game.py
"""
import itertools
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

import model as m
from figstyle import INK, SERIES, WIDTH_FULL, save, use


def p_density(p, sd):
    """p = F(X)，X ~ N(0, sd²) 的密度。"""
    x = m.Finv(p)
    return stats.norm.pdf(x / sd) / (sd * m.C * p * (1 - p))


def sd_ds(sig_e, tau=m.TAU):
    """评分相等的两人真实实力差的标准差 sqrt(2 τ²σ_e²/(τ²+σ_e²))。"""
    return math.sqrt(2 * tau ** 2 * sig_e ** 2 / (tau ** 2 + sig_e ** 2))


def pairs_1v1(name):
    r = m.get(name)
    o = np.argsort(r["R_end"])
    a, b = o[0::2], o[1::2]
    return m.F(r["R_end"][a] - r["R_end"][b]), m.F(r["s"][a] - r["s"][b])


def lobbies_5v5(sigma_q=100.0, seed=2, repeats=10):
    """同一张评分表上重复组局 repeats 次（每次重新抽排队噪声），共 1000×repeats 局。"""
    r = m.get("t_r_sum_k16")
    s, R = r["s"], r["R_end"]
    rng = np.random.default_rng(seed)
    parts = [c for c in itertools.combinations(range(10), 5) if 0 in c]
    mask = np.zeros((len(parts), 10), bool)
    for i, c in enumerate(parts):
        mask[i, list(c)] = True
    o = np.concatenate([np.argsort(R + sigma_q * rng.standard_normal(R.size)).reshape(-1, 10)
                        for _ in range(repeats)])
    diff = (R[o][:, None, :] * np.where(mask, 1, -1)[None]).sum(2)
    mA = mask[np.abs(diff).argmin(1)]
    A, B = o[mA].reshape(-1, 5), o[~mA].reshape(-1, 5)
    E = m.F((R[A].sum(1) - R[B].sum(1)) / math.sqrt(5))
    p = m.F((s[A].sum(1) - s[B].sum(1)) / math.sqrt(5))
    perm = rng.permuted(np.tile(np.arange(5), (B.shape[0], 1)), axis=1)
    duel = m.F(s[A] - s[np.take_along_axis(B, perm, 1)]).ravel()
    resid = m.fit_line(s, R)[2]
    return E, p, duel, resid, float(R[o].std(1).mean())


def main():
    use()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9), sharey=False,
                                 gridspec_kw=dict(wspace=0.28))
    bins = np.linspace(0.15, 0.85, 57)
    pp = np.linspace(0.16, 0.84, 400)
    info = []
    for i, (name, K) in enumerate((("r_k16", 16), ("r_k32", 32))):
        E, p = pairs_1v1(name)
        sd = sd_ds(float(m.sigma_e(K)))
        ax.hist(p, bins=bins, density=True, histtype="stepfilled", color=SERIES[i], alpha=0.18, lw=0)
        ax.hist(p, bins=bins, density=True, histtype="step", color=SERIES[i], lw=0.9)
        ax.plot(pp, p_density(pp, sd), color=SERIES[i], lw=1.6, label=f"$K={K}$（$\\sigma_e$≈{float(m.sigma_e(K)):.0f}）")
        q = np.quantile(p, [0.05, 0.95])
        info.append((K, sd, q, float(np.mean(np.abs(p - 0.5))), float(np.abs(E - 0.5).max())))
    ax.axvline(0.5, color=INK["muted"], lw=0.8, ls=":")
    ax.set_xlim(0.15, 0.85)
    ax.set_ylim(0, 7.2)
    ax.set_xlabel("这一局的真实胜率 $p=F(s_A-s_B)$")
    ax.set_ylabel("密度")
    ax.legend(loc="upper left", fontsize=7)
    ax.set_title("(a) 1v1：系统预测 50% 的对局", loc="left", fontsize=9)

    E, p, duel, resid, lobby_sd = lobbies_5v5()
    bins2 = np.linspace(0.0, 1.0, 81)
    for arr, col, lab in ((duel, SERIES[1], "随机对位单挑"),
                          (p, SERIES[0], "团队真实胜率")):
        bx.hist(arr, bins=bins2, density=True, histtype="stepfilled", color=col, alpha=0.18, lw=0)
        bx.hist(arr, bins=bins2, density=True, histtype="step", color=col, lw=1.0, label=lab)
    sd_t = sd_ds(resid)
    pp2 = np.linspace(0.05, 0.95, 400)
    bx.plot(pp2, p_density(pp2, sd_t), color=SERIES[0], lw=1.6, label="团队理论密度")
    bx.axvline(0.5, color=INK["muted"], lw=0.8, ls=":")
    bx.text(0.99, 0.97, f"系统预测：90% 的对局\n在 {np.quantile(E, 0.05) * 100:.1f}%–{np.quantile(E, 0.95) * 100:.1f}% 之间",
            transform=bx.transAxes, va="top", ha="right", fontsize=7, color=INK["primary"])
    bx.set_xlim(0.0, 1.0)
    bx.set_ylim(0, 6.0)
    bx.set_xlabel("真实胜率")
    bx.legend(loc="upper left", fontsize=6.5)
    bx.set_title("(b) 5v5：两队评分和相等的对局", loc="left", fontsize=9)
    save(fig, "ch2", "fair_game")
    for K, sd, q, mad, emax in info:
        print(f"1v1 K={K}: sd(Δs)={sd:.1f}, p 5–95%: {q[0]:.3f}–{q[1]:.3f}, mean|p-.5|={mad:.3f}, max|E-.5|={emax:.4f}")
    print(f"5v5: team resid {resid:.1f}, lobby rating sd {lobby_sd:.1f}, sd(Δ_team)={sd_t:.1f}")
    print("  E 5–95%", np.quantile(E, [.05, .95]), "team p 5–95%", np.quantile(p, [.05, .95]),
          "duel 5–95%", np.quantile(duel, [.05, .95]))
    print("  mean|p-.5|", np.mean(np.abs(p - .5)), "mean|duel-.5|", np.mean(np.abs(duel - .5)),
          "share duel |p-.5|>0.2", np.mean(np.abs(duel - .5) > 0.2))


if __name__ == "__main__":
    main()
