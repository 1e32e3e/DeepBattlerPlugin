"""图：诚实 Elo 下“连胜 k 局后下一局胜率”相对自身平均的超额：线性近似 Δ_k≈-κcKk/(16n) 与模拟。

(a) 单人、校准对手池（κ=1）；(b) 闭合人群（1v1 K=10/32、5v5 K=32，σ_q=100/250），κ 取模拟中 s 对 R 的回归斜率。"""
import numpy as np
import matplotlib.pyplot as plt

from _common import FONT_SCALE, CH, INK, SERIES, WIDTH_FULL, save, use
from experiments import SIGMA_Q, STANDARD
from model import cond_excess, elo_streak_excess, simulate_player
from population import load
from pathlib import Path

KS = np.arange(1, 9)
CACHE = Path(__file__).resolve().parent / "cache" / "player_reversion.npz"


def single_player():
    if CACHE.exists():
        z = np.load(CACHE)
        return {k: z[k] for k in z.files}
    out = {}
    for K in (10, 32):
        rec = simulate_player(STANDARD["none"], M=40000, T=1000, K=K, sigma_q=SIGMA_Q, seed=1100 + K)
        W, L = cond_excess(rec["p"], rec["ws"], rec["ls"], kmax=8)
        out[f"W{K}"] = W
        out[f"L{K}"] = L
    np.savez(CACHE, **out)
    return out


def main():
    use()
    sp = single_player()
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9), sharey=True)
    ax = axes[0]
    for i, K in enumerate((10, 32)):
        th = 100 * elo_streak_excess(KS, K)[0]
        ax.plot(KS, th, color=SERIES[i], lw=1.4, label=f"近似 K={K}")
        ax.plot(KS, 100 * sp[f"W{K}"], "o", color=SERIES[i], ms=3.5, mec="white", mew=0.6,
                label=f"模拟 K={K}")
    ax.set_title("(a) 单人、校准对手池（κ=1）", loc="left")
    ax.set_xlabel("连胜局数 $k$")
    ax.set_ylabel("下一局胜率超额（百分点）")
    ax.legend(loc="lower left", fontsize=7.5 * FONT_SCALE)
    ax = axes[1]
    for i, (nm, K, n, lab) in enumerate((("elo10", 10, 1, "1v1 K=10"), ("elo32", 32, 1, "1v1 K=32"),
                                         ("t5_elo32", 32, 5, "5v5 K=32"))):
        d = load(nm)
        kappa = float(d["slope_s_R"])
        th = 100 * elo_streak_excess(KS, K, kappa=kappa, team_size=n)[0]
        ax.plot(KS, th, color=SERIES[i], lw=1.4, label=f"{lab}（κ={kappa:.2f}）")
        ax.plot(KS, 100 * d["W"][:8], "o", color=SERIES[i], ms=3.5, mec="white", mew=0.6)
    ax.set_title("(b) 闭合人群（点：模拟；线：近似）", loc="left")
    ax.set_xlabel("连胜局数 $k$")
    ax.legend(loc="lower left", fontsize=7.5 * FONT_SCALE)
    for ax in axes:
        ax.axhline(0, color=INK["muted"], lw=0.8)
        ax.set_xticks(KS)
    fig.tight_layout()
    save(fig, CH, "elo_reversion")


if __name__ == "__main__":
    main()
