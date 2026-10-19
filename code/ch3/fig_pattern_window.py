"""图：(a)“≥k 连胜紧接 ≥k 连败”至少出现一次的概率；(b) 滑动窗口低谷（某连续 w 局只赢 ≤x 局）。"""
import numpy as np
import matplotlib.pyplot as plt

from _common import CH, INK, SERIES, WIDTH_FULL, label_at_level, label_end, log_count_axis, save, use
from model import prob_window_slump_curve, wklk_automaton

N_MAX = 1000


def pattern_curve(n_max, p, k):
    tw, tl = wklk_automaton(k)
    m = 2 * k
    v = np.zeros(m + 1)
    v[0] = 1.0
    out = np.zeros(n_max + 1)
    for n in range(1, n_max + 1):
        nv = np.zeros(m + 1)
        nv[m] = v[m]
        for s in range(m):
            nv[tw[s]] += v[s] * p
            nv[tl[s]] += v[s] * (1 - p)
        v = nv
        out[n] = v[m]
    return out


def main():
    use()
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9), sharey=True)
    n = np.arange(N_MAX + 1)
    ax = axes[0]
    for i, k in enumerate((3, 4, 5)):
        cur = pattern_curve(N_MAX, 0.5, k)
        ax.plot(n[2 * k:], cur[2 * k:], color=SERIES[i], label=f"$k={k}$")
        label_at_level(ax, n[2 * k:], cur[2 * k:], f"$k={k}$", level=0.5)
    ax.axvline(100, color=INK["grid"], lw=0.8, zorder=0)
    ax.set_xscale("log")
    log_count_axis(ax)
    ax.set_xlim(10, N_MAX)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("局数 $n$（对数刻度）")
    ax.set_ylabel("至少出现一次的概率")
    ax.set_title("(a) ≥k 连胜紧接 ≥k 连败", loc="left")
    ax.legend(loc="upper left")
    ax = axes[1]
    nm = 500
    for i, (w, x) in enumerate(((10, 2), (20, 6))):
        cur = prob_window_slump_curve(nm, w, x, 0.5)
        lab = f"某 {w} 局只赢 ≤{x} 局"
        ax.plot(np.arange(w, nm + 1), cur[w:], color=SERIES[i], label=lab)
    ax.axvline(100, color=INK["grid"], lw=0.8, zorder=0)
    ax.set_xscale("log")
    log_count_axis(ax)
    ax.set_xlim(10, nm)
    ax.set_xlabel("局数 $n$（对数刻度）")
    ax.set_title("(b) 滑动窗口里的低谷", loc="left")
    ax.legend(loc="upper left")
    fig.tight_layout()
    save(fig, CH, "pattern_window")


if __name__ == "__main__":
    main()
