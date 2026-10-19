"""图：上头如何把一次失败变成一串。(a) 一段连败开始后长度 ≥r 的概率（精确马尔可夫链，评分不动）；
(b) 平均连败长度随上头强度 θ 的变化（上限 m=3 与 m=5）。"""
import numpy as np
import matplotlib.pyplot as plt

from _common import FONT_SCALE, CH, INK, SERIES, WIDTH_FULL, save, use
from experiments import END_PROB, SIGMA_Q
from model import chain_iid, chain_tilt


def mean_run(ch, rmax=400):
    return ch.loss_run_survival(rmax).sum()


def main():
    use()
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9))
    ax = axes[0]
    r = np.arange(1, 16)
    tilt = chain_tilt(30, 3, SIGMA_Q)
    tilt_b = chain_tilt(30, 3, SIGMA_Q, break_prob=END_PROB)
    pbar = tilt.mean_winrate()
    cases = [(chain_iid(0.5), "独立 50%"),
             (chain_iid(pbar), f"独立 {100 * pbar:.1f}%（同均值）"),
             (tilt, "上头 θ=30, m=3"),
             (tilt_b, "上头 + 休息")]
    for i, (ch, lab) in enumerate(cases):
        ax.plot(r, ch.loss_run_survival(r.size), "-o", color=SERIES[i], ms=3, lw=1.3, label=lab)
    ax.set_yscale("log")
    ax.set_xlabel("连败长度 $r$")
    ax.set_ylabel("P(这段连败 ≥ r | 已开始)")
    ax.set_title("(a) 连败长度的尾部", loc="left")
    ax.set_xticks([1, 3, 5, 7, 9, 11, 13, 15])
    ax.legend(loc="lower left", fontsize=7 * FONT_SCALE)
    ax = axes[1]
    th = np.linspace(0, 80, 41)
    for i, m in enumerate((3, 5)):
        ax.plot(th, [mean_run(chain_tilt(t, m, SIGMA_Q)) for t in th], color=SERIES[i + 2],
                label=f"上限 m={m}")
        ax.plot(th, [mean_run(chain_tilt(t, m, SIGMA_Q, break_prob=END_PROB)) for t in th],
                color=SERIES[i + 2], ls=(0, (3, 2)), lw=1.1, label=f"上限 m={m}，有休息")
    ax.axhline(2.0, color=INK["muted"], lw=0.8)
    ax.text(79, 2.04, "独立 50%：平均 2 局", fontsize=7.5 * FONT_SCALE, color=INK["secondary"], va="bottom",
            ha="right")
    ax.set_ylim(1.75, None)
    ax.set_xlabel("上头强度 θ（每多输一局实力下降，Elo）")
    ax.set_ylabel("一段连败的平均长度（局）")
    ax.set_title("(b) 剂量–反应", loc="left")
    ax.legend(loc="upper left", fontsize=7.5 * FONT_SCALE)
    fig.tight_layout()
    save(fig, CH, "tilt_chain")


if __name__ == "__main__":
    main()
