"""图 1a-2：Elo 逻辑斯蒂曲线、Thurstone 正态曲线、FIDE 现行换算表与 Glicko 的不确定性折减。

(a) 期望得分随评分差 D 的变化：
    - Elo 逻辑斯蒂曲线 F(D) = 1/(1+10^{-D/400})；
    - 正态（Thurstone Case V）曲线 Φ(D/(200√2))，即每人单局表现标准差 200；
    - FIDE 等级分条例（2024-03-01 起施行）8.1.1 表：分数 p ↔ 评分差 dp（逐格抄录）；
    - Glicko 预测式 1/(1+10^{-g(√(RD_i²+RD_j²)) D/400})，取 RD_i = RD_j = 350（未定级玩家）。
(b) 正态曲线、FIDE 表与 Elo 逻辑斯蒂曲线之差（百分点）。

纯解析计算，无随机性。运行：python code/ch1/fig_1a_curves.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

from figstyle import INK, SERIES, WIDTH_FULL, save, use

# FIDE Rating Regulations effective from 1 March 2024, table 8.1.1（p -> dp），
# 来源 https://handbook.fide.com/chapter/B022024 ，只取 p >= 0.50 一侧（另一侧对称）。
FIDE_P = [0.50, 0.51, 0.52, 0.53, 0.54, 0.55, 0.56, 0.57, 0.58, 0.59, 0.60, 0.61, 0.62, 0.63,
          0.64, 0.65, 0.66, 0.67, 0.68, 0.69, 0.70, 0.71, 0.72, 0.73, 0.74, 0.75, 0.76, 0.77,
          0.78, 0.79, 0.80, 0.81, 0.82, 0.83, 0.84, 0.85, 0.86, 0.87, 0.88, 0.89, 0.90, 0.91,
          0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99]
FIDE_DP = [0, 7, 14, 21, 29, 36, 43, 50, 57, 65, 72, 80, 87, 95,
           102, 110, 117, 125, 133, 141, 149, 158, 166, 175, 184, 193, 202, 211,
           220, 230, 240, 251, 262, 273, 284, 296, 309, 322, 336, 351, 366, 383,
           401, 422, 444, 470, 501, 538, 589, 677]

Q = math.log(10) / 400  # Glicko 的 q，即全文的 c


def elo(d):
    return 1.0 / (1.0 + 10.0 ** (-d / 400.0))


def thurstone(d, sigma=200.0):
    return norm.cdf(d / (sigma * math.sqrt(2.0)))


def glicko_pred(d, rd_i=350.0, rd_j=350.0):
    rd = math.sqrt(rd_i ** 2 + rd_j ** 2)
    g = 1.0 / math.sqrt(1.0 + 3.0 * Q ** 2 * rd ** 2 / math.pi ** 2)
    return 1.0 / (1.0 + 10.0 ** (-g * d / 400.0))


def main():
    use()
    p = np.array(FIDE_P)
    dp = np.array(FIDE_DP, dtype=float)
    fide_d = np.concatenate([-dp[::-1], dp[1:]])
    fide_p = np.concatenate([1 - p[::-1], p[1:]])

    d = np.linspace(-800, 800, 801)
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9),
                                 gridspec_kw=dict(wspace=0.32, width_ratios=[1.15, 1]))

    ax.plot(d, elo(d), color=SERIES[0], label="Elo 逻辑斯蒂 $F(D)$")
    ax.plot(d, thurstone(d), color=SERIES[1], ls="--", label=r"正态 $\Phi(D/200\sqrt{2})$")
    ax.plot(fide_d[::3], fide_p[::3], ls="none", marker="o", ms=3.2, mfc="white", mec=SERIES[2],
            mew=1.0, label="FIDE 条例换算表")
    ax.plot(d, glicko_pred(d), color=SERIES[3], ls="-.", label="Glicko 预测（双方 RD=350）")
    ax.axhline(0.5, color=INK["axis"], lw=0.7)
    ax.axvline(0, color=INK["axis"], lw=0.7)
    ax.set_xlim(-800, 800)
    ax.set_ylim(0, 1)
    ax.set_xticks([-800, -400, 0, 400, 800])
    ax.set_xlabel("评分差 $D=R_i-R_j$（Elo）")
    ax.set_ylabel("期望得分 $E$")
    ax.set_title("(a) 四种“评分差 → 期望得分”换算", loc="left", fontsize=9)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=7, handlelength=2.2,
               bbox_to_anchor=(0.5, -0.16), columnspacing=1.4)
    ax.annotate("D=400 时\n$F$=0.909", xy=(400, elo(400)), xytext=(470, 0.62), fontsize=7,
                color=INK["secondary"], arrowprops=dict(arrowstyle="-", color=INK["muted"], lw=0.6))

    dd = np.linspace(0, 800, 401)
    bx.plot(dd, (thurstone(dd) - elo(dd)) * 100, color=SERIES[1], ls="--")
    pos = fide_d >= 0
    bx.plot(fide_d[pos], (fide_p[pos] - elo(fide_d[pos])) * 100, ls="none", marker="o", ms=3.2,
            mfc="white", mec=SERIES[2], mew=1.0)
    bx.axhline(0, color=SERIES[0], lw=1.2)
    bx.text(790, 0.12, "Elo 逻辑斯蒂（基准）", ha="right", va="bottom", fontsize=7, color=INK["secondary"])
    bx.text(640, 1.3, "正态曲线", ha="left", va="bottom", fontsize=7, color=INK["secondary"])
    bx.text(250, 0.95, "FIDE 表", ha="center", va="bottom", fontsize=7, color=INK["secondary"])
    bx.set_xlim(0, 800)
    bx.set_xticks([0, 200, 400, 600, 800])
    bx.set_xlabel("评分差 $D$（Elo，强者一方）")
    bx.set_ylabel("与 $F(D)$ 之差（百分点）")
    bx.set_title("(b) 相对 Elo 曲线的偏差不足 1.5 个百分点", loc="left", fontsize=9)
    save(fig, "ch1", "1a_curves")


if __name__ == "__main__":
    main()
