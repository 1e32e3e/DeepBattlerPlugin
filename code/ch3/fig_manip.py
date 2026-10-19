"""图：操纵的指纹（闭合人群，1v1，K=32，σ_q=100）。(a) 连胜/连败 k 局后真实胜率的玩家内部超额；
(b) 对手评分 − 我方评分的玩家内部超额。诚实 Elo、上头与两种操纵规则对照。"""
import numpy as np
import matplotlib.pyplot as plt

from _common import CH, INK, SERIES, WIDTH_FULL, bottom_legend, save, use
from population import load

CASES = [("elo32", "诚实 Elo"), ("tilt30_elo32", "上头 θ=30"),
         ("manip_sym", "对称操纵：连胜≥3 配 +100、连败≥3 配 −100"),
         ("manip_asym", "非对称操纵：只对连胜≥3 配 +100")]
KMAX = 7


def main():
    use()
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_FULL, 3.0))
    ks = np.r_[-np.arange(KMAX, 0, -1), np.arange(1, KMAX + 1)]
    for i, (nm, lab) in enumerate(CASES):
        d = load(nm)
        win = np.r_[d["L"][:KMAX][::-1], d["W"][:KMAX]] * 100
        opp = np.r_[d["oppR_L"][:KMAX][::-1], d["oppR_W"][:KMAX]]
        for ax, val in zip(axes, (win, opp)):
            ax.plot(ks[ks < 0], val[ks < 0], "-o", color=SERIES[i], ms=3, lw=1.3, label=lab)
            ax.plot(ks[ks > 0], val[ks > 0], "-o", color=SERIES[i], ms=3, lw=1.3)
    for ax in axes:
        ax.axhline(0, color=INK["muted"], lw=0.8)
        ax.axvline(0, color=INK["grid"], lw=0.8)
        for x in (-3, 3):
            ax.axvline(x, color=INK["grid"], lw=0.8, ls=(0, (2, 2)))
        ticks = [-7, -5, -3, -1, 1, 3, 5, 7]
        ax.set_xticks(ticks)
        ax.set_xticklabels([f"{t:+d}".replace("-", "−") for t in ticks])
        ax.set_xlabel("最近连续结果（负＝连败，正＝连胜）")
    axes[0].set_ylabel("下一局胜率超额（百分点）")
    axes[0].set_title("(a) 条件胜率：阈值处的断崖", loc="left")
    axes[1].set_ylabel("对手评分 − 我方评分（Elo）")
    axes[1].set_title("(b) 匹配输入：对手评分差", loc="left")
    h, l = axes[0].get_legend_handles_labels()
    fig.tight_layout()
    bottom_legend(fig, h, l, ncol=2)
    save(fig, CH, "manip")


if __name__ == "__main__":
    main()
