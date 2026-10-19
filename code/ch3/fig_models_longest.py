"""图：1000 局内最长连败的分布（生存函数），Elo K=20 下各波动模型与独立 50% 基线（精确）的比较。"""
import numpy as np
import matplotlib.pyplot as plt

from _common import CH, INK, SERIES, WIDTH_FULL, save, use
from experiments import K_ELO, run_standard
from model import longest_run_distribution

MODELS = ["none", "ar1", "hmm", "tilt", "fatigue"]
LABELS = {"none": "无波动（诚实 Elo）", "ar1": "(b) AR(1)", "hmm": "(c) 两状态", "tilt": "(d) 上头",
          "fatigue": "(e) 疲劳"}


def main():
    use()
    fig, ax = plt.subplots(figsize=(WIDTH_FULL * 0.72, 2.9))
    r = np.arange(5, 22)
    ge = longest_run_distribution(1000, 0.5)[4]
    ax.plot(r, ge[r], color=INK["muted"], lw=1.2, ls=(0, (3, 2)), label="独立 50%（精确）")
    for i, nm in enumerate(MODELS):
        d = run_standard(nm, K_ELO)
        hist = d["longest_hist"].astype(float)
        surv = hist[::-1].cumsum()[::-1] / hist.sum()
        ax.plot(r, surv[r], color=SERIES[i], lw=1.4, label=LABELS[nm])
    ax.set_yscale("log")
    ax.set_ylim(1e-3, 1.1)
    ax.set_xticks(np.arange(5, 22, 2))
    ax.set_xlabel("连败长度 $r$")
    ax.set_ylabel("P(1000 局内最长连败 ≥ r)")
    ax.legend(loc="lower left", fontsize=7.5)
    fig.tight_layout()
    save(fig, CH, "models_longest")


if __name__ == "__main__":
    main()
