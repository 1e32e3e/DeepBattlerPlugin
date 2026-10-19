"""图：完美校准的模型在真实胜率为 p 的对局上能达到的最好指标。

准确率上限 max(p,1-p)、对数损失下限 H(p)（二元熵）、Brier 分数下限 p(1-p)，均为解析式，无随机性。
阴影：|R_i-R_j| <= 70 Elo 对应的胜率区间（约 40%–60%）。窗口较窄（σ_q≈50）时约三分之二的对局落在这里；
σ_q=100 时只有约四成。
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from figstyle import use, save, SERIES, INK, WIDTH_FULL  # noqa: E402
from ch4_model import F, binary_entropy  # noqa: E402


def main():
    use()
    p = np.linspace(0.001, 0.999, 500)
    lo, hi = float(F(-70)), float(F(70))
    panels = [
        ("(a) 准确率上限", 100 * np.maximum(p, 1 - p), "准确率（%）", (45, 101), 50.0, "50%"),
        ("(b) 对数损失下限", binary_entropy(p), "对数损失（nats）", (0, 0.75), np.log(2), r"$\ln 2\approx0.693$"),
        ("(c) Brier 分数下限", p * (1 - p), "Brier 分数", (0, 0.27), 0.25, "0.25"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(WIDTH_FULL, 2.25))
    for ax, (title, yv, ylab, ylim, y05, lab) in zip(axes, panels):
        ax.axvspan(lo, hi, color=SERIES[0], alpha=0.08, lw=0)
        ax.plot(p, yv, color=SERIES[0], lw=1.6)
        ax.plot([0.5], [y05], "o", color=SERIES[0], ms=5, mec="white", mew=1.0)
        ax.annotate(lab, (0.5, y05), xytext=(0, 6 if title.startswith("(a)") else -14),
                    textcoords="offset points", ha="center", fontsize=7.5, color=INK["primary"])
        ax.set_xlim(0, 1)
        ax.set_ylim(*ylim)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
        ax.set_xticklabels(["0", "0.25", "0.5", "0.75", "1"])
        ax.set_xlabel("真实单局胜率 $p$")
        ax.set_ylabel(ylab)
        ax.set_title(title, loc="left")
    axes[0].text(0.5, 92, "按分匹配\n常见区间", ha="center", fontsize=7, color=INK["secondary"])
    fig.tight_layout(w_pad=1.2)
    save(fig, "ch4", "fig_coinflip")
    print(f"shaded interval: F(-70)={lo:.3f}, F(70)={hi:.3f}")


if __name__ == "__main__":
    main()
