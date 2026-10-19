"""图：各实力波动模型下，连败 k 局 / 连胜 k 局后下一局真实胜率相对自身平均的超额（单人模拟，M=20000×1000 局）。"""
import numpy as np
import matplotlib.pyplot as plt

from _common import FONT_SCALE, CH, INK, SERIES, WIDTH_FULL, bottom_legend, save, use
from experiments import K_ELO, STANDARD, run_standard

MODELS = ["none", "ar1", "hmm", "tilt", "fatigue"]
LABELS = {"none": "无波动", "ar1": "(b) AR(1)", "hmm": "(c) 两状态", "tilt": "(d) 上头",
          "fatigue": "(e) 疲劳"}
MARKERS = ["o", "s", "^", "D", "v"]


def main():
    use()
    ks = np.arange(1, 7)
    fig, axes = plt.subplots(2, 2, figsize=(5.0, 4.1), sharex=True, sharey="row")
    for r, K in enumerate((0, K_ELO)):
        for c, key in enumerate(("L", "W")):
            ax = axes[r, c]
            for i, nm in enumerate(MODELS):
                d = run_standard(nm, K)
                ax.plot(ks, 100 * d[key][:6], "-" + MARKERS[i], color=SERIES[i], ms=3.2, lw=1.3,
                        label=LABELS[nm])
            ax.axhline(0, color=INK["muted"], lw=0.8)
            what = "连败" if key == "L" else "连胜"
            sys_ = "K=0" if K == 0 else f"K={K}"
            ax.set_title(f"({'abcd'[2 * r + c]}) {sys_}：{what} k 局后", loc="left", fontsize=9 * FONT_SCALE)
            if c == 0:
                ax.set_ylabel("胜率超额（百分点）")
            if r == 1:
                ax.set_xlabel("$k$")
            ax.set_xticks(ks)
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.tight_layout()
    bottom_legend(fig, h, l, ncol=5)
    save(fig, CH, "models_conditional")


if __name__ == "__main__":
    main()
