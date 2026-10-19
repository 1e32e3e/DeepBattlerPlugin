"""图：8 人名次游戏里的“久不夺冠”：n 局中至少出现一段 ≥d 局没拿第一的概率（同分大厅，夺冠率 1/8）。"""
import numpy as np
import matplotlib.pyplot as plt

from _common import CH, INK, SERIES, WIDTH_FULL, bottom_legend, label_at_level, log_count_axis, save, use
from model import prob_longest_ge_curve

N_MAX = 500


def main():
    use()
    fig, ax = plt.subplots(figsize=(WIDTH_FULL * 0.72, 2.3))
    n = np.arange(N_MAX + 1)
    for i, d in enumerate((10, 20, 30, 40)):
        cur = prob_longest_ge_curve(N_MAX, 7 / 8, d)
        ax.plot(n[d:], cur[d:], color=SERIES[i], label=f"≥{d} 局无冠")
        label_at_level(ax, n[d:], cur[d:], f"≥{d}", level=0.5, side="right")
    cur = prob_longest_ge_curve(N_MAX, 0.5, 5)
    ax.plot(n[5:], cur[5:], color=INK["muted"], lw=1.0, ls=(0, (3, 2)), label="≥5 局连续后四（对照）")
    ax.axvline(100, color=INK["grid"], lw=0.8, zorder=0)
    ax.set_xscale("log")
    log_count_axis(ax)
    ax.set_xlim(10, N_MAX)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("局数 $n$（对数刻度）")
    ax.set_ylabel("至少出现一次的概率")
    fig.tight_layout()
    h, l = ax.get_legend_handles_labels()
    bottom_legend(fig, h, l, ncol=3)
    save(fig, CH, "bg_drought")


if __name__ == "__main__":
    main()
