"""图：最难预测的对局最有信息量；分辨小实力差需要的局数。

(a) 随评分差 d 变化：单局可预测性 2|p-1/2|（完美模型准确率超出 50% 的部分，归一化到 [0,1]）
    与单局 Fisher 信息 I(d)=c^2 p(1-p) 相对其最大值 c^2/4 的比例。
(b) 在 p≈1/2 附近，分辨实力差 Δ 所需局数：两倍标准误 N=(1/(F(Δ)-1/2))^2 / 4 * 4，
    以及 5% 双侧检验、80% 检验力 N=((z_.975+z_.8)*0.5/(F(Δ)-1/2))^2。解析式，无随机性。
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from figstyle import use, save, SERIES, INK, WIDTH_FULL  # noqa: E402
from ch4_model import F  # noqa: E402


def games_needed(delta, power=None):
    dp = F(delta) - 0.5
    if power is None:
        return (1.0 / dp) ** 2          # dp = 2 * 0.5 / sqrt(N)
    z = stats.norm.ppf(0.975) + stats.norm.ppf(power)
    return (z * 0.5 / dp) ** 2


def main():
    use()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.8))
    d = np.linspace(-800, 800, 801)
    p = F(d)
    ax1.plot(d, 4 * p * (1 - p), color=SERIES[0], lw=1.6, label="单局 Fisher 信息 $I(d)/I(0)$")
    ax1.plot(d, 2 * np.abs(p - 0.5), color=SERIES[1], lw=1.4, ls="--", label=r"单局可预测性 $2|p-\frac{1}{2}|$")
    ax1.set_xlabel("评分差 $d=R_i-R_j$（Elo）")
    ax1.set_ylabel("相对值")
    ax1.set_ylim(0, 1.42)
    ax1.set_xlim(-800, 800)
    ax1.set_title("(a) 最难预测 = 最有信息", loc="left")
    ax1.legend(loc="upper center", fontsize=7.2, ncol=1)

    deltas = np.logspace(np.log10(3), np.log10(200), 200)
    ax2.plot(deltas, games_needed(deltas), color=SERIES[0], lw=1.6, label="两倍标准误")
    ax2.plot(deltas, games_needed(deltas, 0.8), color=SERIES[2], lw=1.4, ls="--", label="5% 检验 + 80% 检验力")
    spots = {5: (3.3, 700), 50: (9, 25)}
    for dl in (5, 50):
        n = float(games_needed(dl))
        ax2.plot([dl], [n], "o", color=SERIES[0], ms=5, mec="white", mew=1.0)
        ax2.annotate(f"Δ={dl}：约 {round(n, -1 if n < 1000 else -2):,.0f} 局", (dl, n), xytext=spots[dl],
                     textcoords="data", fontsize=7.5, color=INK["primary"],
                     arrowprops=dict(arrowstyle="-", color=INK["muted"], lw=0.6, shrinkB=3))
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.minorticks_off()
    ax2.set_xticks([3, 5, 10, 20, 50, 100, 200])
    ax2.set_xticklabels(["3", "5", "10", "20", "50", "100", "200"])
    ax2.set_yticks([10, 100, 1000, 10000, 100000])
    ax2.set_yticklabels(["10", "100", "1K", "10K", "100K"])
    ax2.set_xlabel("要分辨的实力差 Δ（Elo，对数刻度）")
    ax2.set_ylabel("所需局数（对数刻度）")
    ax2.set_title("(b) 分辨小差距需要的局数", loc="left")
    ax2.legend(loc="upper right", fontsize=7.2)
    fig.tight_layout()
    save(fig, "ch4", "fig_fisher")
    for dl in (5, 10, 25, 50, 100):
        print(dl, round(float(games_needed(dl))), round(float(games_needed(dl, 0.8))))


if __name__ == "__main__":
    main()
