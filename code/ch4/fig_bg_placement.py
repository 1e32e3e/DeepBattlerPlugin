"""图：8 人名次游戏（酒馆战棋式）——名次分布与评估所需局数。

(a) Plackett–Luce 名次模型：一名玩家比其余 7 名等强对手强 Δ=0/100/200 Elo（log 权重 = c·s，
    即假设名次对实力的敏感度与 1v1 Elo 曲线相同；真实酒馆战棋运气成分更大，敏感度会更低）。
    Δ=0 时每个名次概率都是 1/8。精确计算，无随机性。
(b) 检出平均名次改进 Δm 所需局数（5% 双侧、80% 检验力）：对已知基准（固定参照池下的 4.5）
    与两个版本互比（每个版本的局数）。名次标准差取等强时的 sqrt(63/12)≈2.29。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from figstyle import use, save, SERIES, INK, WIDTH_FULL  # noqa: E402
from ch4_model import C, pl_place_dist_exact  # noqa: E402


def main():
    use()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9))
    places = np.arange(1, 9)
    for i, d in enumerate((0, 100, 200)):
        strength = np.zeros(8)
        strength[0] = C * d
        dist = pl_place_dist_exact(strength, 0)
        mean = (places * dist).sum()
        top4 = dist[:4].sum()
        ax1.plot(places, 100 * dist, color=SERIES[i], marker=["o", "s", "^"][i], ms=4, lw=1.4,
                 ls=["-", "--", "-."][i], label=f"Δ={d}：平均 {mean:.2f}，前四 {100*top4:.0f}%")
        print(f"Δ={d}: dist={np.round(dist,3)}, mean={mean:.3f}, top4={top4:.3f}, first={dist[0]:.3f}")
    ax1.set_xticks(places)
    ax1.set_xlabel("名次")
    ax1.set_ylabel("概率（%）")
    ax1.set_ylim(0, 32)
    ax1.set_title("(a) 比同桌强 Δ Elo 时的名次分布", loc="left")
    ax1.legend(loc="upper right", fontsize=7)

    sd = math.sqrt(63 / 12)
    z = stats.norm.ppf(0.975) + stats.norm.ppf(0.8)
    dm = np.linspace(0.05, 0.5, 200)
    n1 = (z * sd / dm) ** 2
    ax2.plot(dm, n1, color=SERIES[0], lw=1.6, label="对已知基准（固定参照池）")
    ax2.plot(dm, 2 * n1, color=SERIES[1], lw=1.4, ls="--", label="两个版本互比（每版）")
    spots = {0.1: (0.06, 170), 0.25: (0.3, 4000)}
    for x in (0.1, 0.25):
        v = (z * sd / x) ** 2
        ax2.plot([x], [v], "o", color=SERIES[0], ms=4.5, mec="white", mew=1.0)
        ax2.annotate(f"Δm={x:g}：约 {round(v, -1):,.0f} 局", (x, v), xytext=spots[x], textcoords="data",
                     fontsize=7.5, color=INK["primary"],
                     arrowprops=dict(arrowstyle="-", color=INK["muted"], lw=0.6, shrinkB=3))
    ax2.set_yscale("log")
    ax2.minorticks_off()
    ax2.set_yticks([100, 300, 1000, 3000, 10000, 30000])
    ax2.set_yticklabels(["100", "300", "1K", "3K", "10K", "30K"])
    ax2.set_xlabel("平均名次改进 Δm（名次）")
    ax2.set_ylabel("所需局数（对数刻度）")
    ax2.set_title("(b) 检出名次改进所需局数", loc="left")
    ax2.legend(loc="upper right", fontsize=7)
    fig.tight_layout()
    save(fig, "ch4", "fig_bg_placement")


if __name__ == "__main__":
    main()
