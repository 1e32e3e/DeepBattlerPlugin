"""图：(a) Miller–Sanjurjo 有限样本偏差：自查一段 n 局历史里“连胜 k 局后的胜率”的期望；
(b) 构成效应：跨人群合并统计的 P(胜 | 最近 k 局全胜/全负)。"""
import numpy as np
import matplotlib.pyplot as plt

from _common import FONT_SCALE, CH, INK, SERIES, WIDTH_FULL, log_count_axis, save, use
from model import miller_sanjurjo_curve, pooled_streak_winrate
from population import load

N_MAX = 500


def main():
    use()
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9))
    ax = axes[0]
    ns = np.unique(np.round(np.logspace(np.log10(12), np.log10(N_MAX), 40)).astype(int))
    for i, k in enumerate((1, 2, 3, 4)):
        res = miller_sanjurjo_curve(N_MAX, k, 0.5, checkpoints=ns)
        y = np.array([res[n] for n in ns])
        ax.plot(ns, 100 * y, color=SERIES[i], label=f"连胜 {k} 局后")
    v = miller_sanjurjo_curve(100, 3, 0.5, checkpoints=[100])[100]
    ax.plot([100], [100 * v], "o", color=SERIES[2], ms=5, mec="white", mew=1.2, zorder=5)
    ax.axhline(50, color=INK["muted"], lw=0.9)
    ax.text(N_MAX, 50.4, "真实胜率 / 合并计数 50%", ha="right", va="bottom", fontsize=7.5 * FONT_SCALE,
            color=INK["secondary"])
    ax.set_xscale("log")
    log_count_axis(ax)
    ax.set_xlim(12, N_MAX)
    ax.set_ylim(30, 52)
    ax.set_xlabel("自查的历史长度 $n$（局，对数刻度）")
    ax.set_ylabel("条件胜率估计量的期望（%）")
    ax.set_title("(a) 单人自查的选择偏差", loc="left")
    ax.legend(loc="lower right", fontsize=7.5 * FONT_SCALE)

    ax = axes[1]
    ks = np.arange(-6, 7)
    ks = ks[ks != 0]
    rnd = [pooled_streak_winrate(int(k)) for k in ks]
    ax.plot(ks[ks > 0], 100 * np.array(rnd)[ks > 0], "-o", color=SERIES[0], ms=3.5,
            label="随机匹配（解析）")
    ax.plot(ks[ks < 0], 100 * np.array(rnd)[ks < 0], "-o", color=SERIES[0], ms=3.5)
    for i, (nm, lab) in enumerate((("elo10", "按分 K=10"), ("elo32", "按分 K=32"))):
        d = load(nm)
        yW = 100 * d["pooledW"][:6]
        yL = 100 * d["pooledL"][:6]
        ax.plot(np.arange(1, 7), yW, "-s", color=SERIES[i + 1], ms=3.5, label=lab + "（模拟）")
        ax.plot(-np.arange(1, 7), yL, "-s", color=SERIES[i + 1], ms=3.5)
    ax.axhline(50, color=INK["muted"], lw=0.9)
    ax.axvline(0, color=INK["grid"], lw=0.8)
    ax.set_xticks(ks)
    ax.set_xticklabels([f"{k:+d}".replace("-", "−") for k in ks])
    ax.set_xlabel("最近连续结果（负数＝连败局数，正数＝连胜局数）")
    ax.set_ylabel("合并统计的下一局胜率（%）")
    ax.set_title("(b) 跨人群合并的构成效应", loc="left")
    ax.legend(loc="upper left", fontsize=7 * FONT_SCALE, handlelength=1.6)
    fig.tight_layout()
    save(fig, CH, "ms_bias")


if __name__ == "__main__":
    main()
