"""图：局内疲劳与停止规则。(a) 疲劳模型下按局序号的真实胜率；(b) 结果完全独立、
但“输了更容易下线”时，按会话长度分组画出的伪“局内下滑”。"""
import numpy as np
import matplotlib.pyplot as plt

from _common import FONT_SCALE, CH, INK, SERIES, WIDTH_FULL, save, use
from experiments import K_ELO, SIGMA_Q, STANDARD, run_standard
from model import win_prob_noisy

S_WIN, S_LOSS = 0.10, 0.20    # 赢后 / 输后结束本次游玩的概率（示意）


def main():
    use()
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9))
    ax = axes[0]
    phi = STANDARD["fatigue"].phi
    j = np.arange(1, 16)
    ax.plot(j, 100 * win_prob_noisy(-phi * (j - 1), SIGMA_Q), "-o", color=SERIES[0], ms=3,
            label="评分不动（精确）")
    d = run_standard("fatigue", K_ELO)
    ax.plot(j, 100 * d["winrate_by_j"][:15], "-s", color=SERIES[1], ms=3,
            label=f"Elo K={K_ELO}（模拟）")
    ax.axhline(50, color=INK["muted"], lw=0.8)
    ax.set_xticks([1, 3, 5, 7, 9, 11, 13, 15])
    ax.set_xlabel("本次游玩中的第几局 $j$")
    ax.set_ylabel("真实单局胜率（%）")
    ax.set_title(f"(a) 疲劳 φ={phi:g}，平均每次 8 局", loc="left")
    ax.legend(loc="lower left", fontsize=7.5 * FONT_SCALE)
    ax = axes[1]
    p = 0.5
    mid = p * (1 - S_WIN) / (p * (1 - S_WIN) + (1 - p) * (1 - S_LOSS))
    last = p * S_WIN / (p * S_WIN + (1 - p) * S_LOSS)
    for i, n in enumerate((3, 4, 5, 6)):
        x = np.arange(1, n + 1)
        yv = np.r_[np.full(n - 1, mid), last] * 100
        ax.plot(x, yv, "-o", color=SERIES[i], ms=3, label=f"这次共 {n} 局")
    ax.axhline(50, color=INK["muted"], lw=0.8)
    ax.set_xlabel("这次游玩中的第几局")
    ax.set_ylabel("该位置的胜率（%）")
    ax.set_title(f"(b) 独立结果 + 输后下线概率 {S_LOSS:g}、赢后 {S_WIN:g}", loc="left", fontsize=9 * FONT_SCALE)
    ax.set_ylim(15, 60)
    ax.legend(loc="lower left", fontsize=7 * FONT_SCALE, ncol=2, columnspacing=1.0)
    fig.tight_layout()
    save(fig, CH, "fatigue_session")


if __name__ == "__main__":
    main()
