"""图：诚实 Elo 的评分过冲。以“最近 5 局全胜”的时刻为 0 点，平均评分误差 R−s 的前后走势（单人、校准对手池）。

线性高斯近似：连胜前 E[e]≈-(kc/2)σ_e²·(1-b)^j，连胜中每局 +K/2，连胜后按 (1-b)^h 衰减。"""
import numpy as np
import matplotlib.pyplot as plt

from _common import FONT_SCALE, CH, INK, SERIES, WIDTH_FULL, save, use
from experiments import run_event_study
from model import C_ELO, elo_gain

K_STREAK = 5


def theory(K, hs, k=K_STREAK):
    b = elo_gain(K)
    a = 1 - b
    var_e = K ** 2 / (4 * b * (2 - b))
    start = -k * C_ELO / 2 * var_e            # E[e_{t-k}]
    out = np.empty(hs.size)
    for i, h in enumerate(hs):
        if h <= -k:
            out[i] = a ** (-k - h) * start
        elif h <= 0:
            out[i] = start + (h + k) * K / 2
        else:
            out[i] = a ** h * (start + k * K / 2)
    return out


def main():
    use()
    d = run_event_study()
    fig, ax = plt.subplots(figsize=(WIDTH_FULL * 0.72, 2.4))
    for i, K in enumerate((10, 32)):
        hs = d[f"K{K}_h"]
        ax.plot(hs, theory(K, hs), color=SERIES[i], lw=1.4, label=f"线性近似 K={K}")
        ax.plot(hs, d[f"K{K}_mean_err"], "o", color=SERIES[i], ms=3.2, mec="white", mew=0.6,
                label=f"模拟 K={K}")
    ax.axvspan(-K_STREAK, 0, color=INK["grid"], alpha=0.35, lw=0)
    ax.text(-K_STREAK / 2, ax.get_ylim()[1] if False else 41, "5 连胜", ha="center", va="bottom",
            fontsize=8 * FONT_SCALE, color=INK["secondary"])
    ax.axhline(0, color=INK["muted"], lw=0.8)
    ax.axvline(0, color=INK["muted"], lw=0.8)
    ax.set_xlabel("相对“连胜 5 局之后下一局”的局数 $h$")
    ax.set_ylabel("平均评分误差 $R-s$（Elo）")
    ax.legend(loc="lower right", fontsize=7.5 * FONT_SCALE, ncol=1)
    fig.tight_layout()
    save(fig, CH, "elo_event")


if __name__ == "__main__":
    main()
