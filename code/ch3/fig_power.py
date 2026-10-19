"""图：单个玩家要多少局才能从自己的战绩里检出各种效应（检验力，双侧 5%）。

(a) 评分不动（K=0），原始胜负；(b) Elo（K=20），原始胜负；(c) Elo（K=20），以对手评分为协变量、
自身实力取常数后的残差。每个模型用它“对口”的检验；零分布由无波动模型模拟得到（(c) 为诚实 Elo）。"""
import numpy as np
import matplotlib.pyplot as plt

from _common import FONT_SCALE, CH, INK, SERIES, WIDTH_FULL, bottom_legend, log_count_axis, save, use
from experiments import K_ELO, NATURAL_TEST, TESTS, run_power, run_power_resid

MODELS = [("none", "无波动（诚实 Elo）"), ("ar1", "(b) AR(1)"), ("hmm", "(c) 两状态"),
          ("tilt", "(d) 上头"), ("tilt_break", "(d') 上头+休息"), ("fatigue", "(e) 疲劳")]
COLORS = {"none": SERIES[0], "ar1": SERIES[1], "hmm": SERIES[2], "tilt": SERIES[3],
          "tilt_break": SERIES[3], "fatigue": SERIES[4]}


def main():
    use()
    d = run_power()
    dr = run_power_resid()
    T = d["T"]
    fig, axes = plt.subplots(1, 3, figsize=(WIDTH_FULL, 2.7), sharey=True)
    panels = [(axes[0], "(a) K=0，原始胜负", lambda nm, t: d[f"{nm}_K0_{t}"]),
              (axes[1], f"(b) K={K_ELO}，原始胜负", lambda nm, t: d[f"{nm}_K{K_ELO}_{t}"]),
              (axes[2], f"(c) K={K_ELO}，对手评分残差", lambda nm, t: dr.get(f"{nm}_{t}"))]
    for ax, title, get in panels:
        for nm, lab in MODELS:
            test = NATURAL_TEST[nm]
            y = get(nm, test)
            if y is None:
                continue
            ls = (0, (3, 2)) if nm == "tilt_break" else "-"
            ax.plot(T, y, ls=ls, marker="o", ms=2.8, color=COLORS[nm], lw=1.3,
                    label=f"{lab}：{TESTS[test]}")
        ax.axhline(0.8, color=INK["muted"], lw=0.8)
        ax.axhline(0.05, color=INK["grid"], lw=0.8)
        ax.set_xscale("log")
        log_count_axis(ax)
        ax.set_xticks([100, 1000, 4000])
        ax.set_xticklabels(["100", "1000", "4000"])
        ax.set_xlim(T[0] * 0.9, T[-1] * 1.1)
        ax.set_ylim(0, 1.02)
        ax.set_xlabel("局数 $T$")
        ax.set_title(title, loc="left", fontsize=9 * FONT_SCALE)
    axes[0].set_ylabel("检验力")
    h, l = axes[1].get_legend_handles_labels()
    fig.tight_layout()
    bottom_legend(fig, h, l, ncol=2)
    save(fig, CH, "power")


if __name__ == "__main__":
    main()
