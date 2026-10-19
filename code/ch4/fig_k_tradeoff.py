"""图：K 是学习率——收敛速度、稳态噪声与跟踪滞后的权衡。

(a) 一名玩家的实力在第 200 局跳升 200 Elo，K=8 与 K=32 的评分轨迹。
(b) 稳态均方根跟踪误差 vs K：实力恒定（sigma_w=0）与实力随机游走（sigma_w=3、10 Elo/局），
    点为模拟，线为线性化理论（附录推导）。
模型：按分匹配，对手评分 = 玩家当前评分（sigma_q=0），对手评分准确。
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from figstyle import use, save, SERIES, INK, WIDTH_FULL  # noqa: E402
from ch4_model import track_rating, track_rmse, rmse_theory  # noqa: E402

CACHE = HERE / "cache" / "k_tradeoff.npz"
KS = np.array([2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64])
SWS = np.array([0.0, 3.0, 10.0])


def simulate():
    if CACHE.exists():
        z = np.load(CACHE)
        return z["S"], z["R"], z["rmse"]
    rng = np.random.default_rng(20261018)
    S, R = track_rating(rng, np.array([[8.0], [32.0]]), T=600, n_rep=1, step_at=200, step_size=200.0)
    rmse = track_rmse(np.random.default_rng(7), KS, SWS, T=24000, burn=4000, n_rep=200)
    CACHE.parent.mkdir(exist_ok=True)
    np.savez(CACHE, S=S, R=R, rmse=rmse)
    return S, R, rmse


def main():
    use()
    S, R, rmse = simulate()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9), gridspec_kw={"width_ratios": [1.15, 1]})

    t = np.arange(S.shape[-1])
    ax1.plot(t, S[0, 0], color=INK["primary"], lw=1.2, label="真实实力 $s_t$")
    ax1.plot(t, R[0, 0], color=SERIES[0], lw=1.2, label="评分 $R_t$，$K=8$")
    ax1.plot(t, R[1, 0], color=SERIES[1], lw=1.0, ls="--", label="评分 $R_t$，$K=32$")
    ax1.set_xlabel("局数 $t$")
    ax1.set_ylabel("Elo")
    ax1.set_title("(a) 实力跳升 200 后的跟踪", loc="left")
    ax1.legend(loc="lower right", fontsize=7.5)
    ax1.set_ylim(-120, 330)

    kk = np.linspace(1.6, 70, 300)
    labels = ["实力恒定", r"漂移 $\sigma_w=3$", r"漂移 $\sigma_w=10$"]
    for i, sw in enumerate(SWS):
        col = SERIES[i]
        ax2.plot(kk, rmse_theory(kk, sw), color=col, ls=["-", "--", "-."][i], lw=1.4, label=labels[i])
        ax2.plot(KS, rmse[i], "o", color=col, ms=4, mec="white", mew=0.8)
        if sw > 0:
            kopt = 2 * sw
            ax2.plot([kopt], [rmse_theory(kopt, sw)], marker="v", color=INK["secondary"], ms=5)
            ax2.annotate(f"$K^*\\approx{kopt:.0f}$", (kopt, rmse_theory(kopt, sw)),
                         xytext=(0, 7), textcoords="offset points", ha="center", va="bottom",
                         fontsize=7.5, color=INK["secondary"])
    ax2.set_xscale("log")
    ax2.minorticks_off()
    ax2.set_xticks([2, 4, 8, 16, 32, 64])
    ax2.set_xticklabels(["2", "4", "8", "16", "32", "64"])
    ax2.set_ylim(0, 140)
    ax2.set_xlabel("K 因子（对数刻度）")
    ax2.set_ylabel("稳态跟踪误差 RMSE（Elo）")
    ax2.set_title("(b) K 的偏差—方差权衡", loc="left")
    ax2.legend(loc="upper center", fontsize=7.5, ncol=1, bbox_to_anchor=(0.45, 1.0))
    fig.tight_layout()
    save(fig, "ch4", "fig_k_tradeoff")
    # 打印给正文用的数字
    for i, sw in enumerate(SWS):
        print(f"sigma_w={sw}: " + ", ".join(f"K={k}:{v:.1f}" for k, v in zip(KS, rmse[i])))


if __name__ == "__main__":
    main()
