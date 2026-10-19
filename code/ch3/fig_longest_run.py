"""图：独立对局中“至少出现一次 ≥k 连败”的概率随局数 n 的变化（精确 DP 与泊松近似）。"""
import numpy as np
import matplotlib.pyplot as plt

from _common import CH, INK, SERIES, WIDTH_FULL, bottom_legend, label_at_level, log_count_axis, save, use
from model import expected_runs_ge, prob_longest_ge_curve

N_MAX = 2000
KS = [5, 7, 10, 12]


def main():
    use()
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9), sharey=True)
    n = np.arange(N_MAX + 1)
    for ax, pw, title in zip(axes, (0.5, 0.45), ("(a) 单局胜率 50%", "(b) 单局胜率 45%")):
        q = 1 - pw
        for i, k in enumerate(KS):
            exact = prob_longest_ge_curve(N_MAX, q, k)
            approx = np.array([1 - np.exp(-expected_runs_ge(m, q, k)) for m in n])
            ax.plot(n[k:], exact[k:], color=SERIES[i], lw=1.6, label=f"≥{k} 连败")
            ax.plot(n[k:], approx[k:], color=SERIES[i], lw=0.9, ls=(0, (3, 2)), alpha=0.9)
            label_at_level(ax, n[k:], exact[k:], f"≥{k}", level=0.5)
        for x in (100, 1000):
            ax.axvline(x, color=INK["grid"], lw=0.8, zorder=0)
        ax.set_xscale("log")
        ax.set_xlim(10, N_MAX)
        log_count_axis(ax)
        ax.set_xticks([10, 30, 100, 300, 1000])
        ax.set_xticklabels(["10", "30", "100", "300", "1000"])
        ax.set_ylim(0, 1.02)
        ax.set_xlabel("局数 $n$（对数刻度）")
        ax.set_title(title, loc="left")
    axes[0].set_ylabel("P(最长连败 ≥ k)")
    h, l = axes[0].get_legend_handles_labels()
    from matplotlib.lines import Line2D
    h.append(Line2D([], [], color=INK["muted"], lw=0.9, ls=(0, (3, 2))))
    l.append("虚线：泊松近似")
    fig.tight_layout()
    bottom_legend(fig, h, l)
    save(fig, CH, "longest_run")


if __name__ == "__main__":
    main()
