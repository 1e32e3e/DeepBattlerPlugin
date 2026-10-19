"""图 1a-3：Halo 5 测试集中，车队（预先组队）规模与实际胜率、模型预期胜率。

数据逐格抄自 Minka, Cleven & Zaykov (2018) TrueSkill 2 技术报告第 6 节两张表：
  实际胜率（%），经典 TrueSkill（“队伍实力 = 成员实力之和”）预期胜率，加入车队偏移后的 TrueSkill 2 预期胜率。
注：原文第二张表把 6 人车队的实际胜率印作 55，第一张表为 56；此处实际胜率取第一张表。
无随机性。运行：python code/ch1/fig_1a_squad.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np

from figstyle import INK, SERIES, WIDTH_FULL, save, use

SIZES = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "≥10"]
ACTUAL = [47, 50, 50, 57, 53, 56, 62, 68, 70, 89]
EXP_TS = [47, 50, 50, 52, 49, 48, 49, 49, 54, 67]
EXP_TS2 = [46, 51, 50, 57, 53, 54, 59, 61, 66, 87]


def main():
    use()
    x = np.arange(len(SIZES))
    fig, ax = plt.subplots(figsize=(WIDTH_FULL, 2.7))
    ax.plot(x, ACTUAL, color=SERIES[0], marker="o", ms=4.5, label="实际胜率")
    ax.plot(x, EXP_TS, color=SERIES[1], ls="--", marker="s", ms=3.8, label="经典 TrueSkill 预期（求和假设）")
    ax.plot(x, EXP_TS2, color=SERIES[2], ls="-.", marker="^", ms=4.2, label="TrueSkill 2 预期（加车队偏移）")
    ax.axhline(50, color=INK["axis"], lw=0.7)
    # 直接标注：在最右端点旁写系列名
    ax.text(x[-1] + 0.18, ACTUAL[-1] + 1.5, "实际 89%", fontsize=7, color=INK["secondary"], va="center", ha="left")
    ax.text(x[-1] + 0.18, EXP_TS2[-1] - 2.5, "TS2 预期 87%", fontsize=7, color=INK["secondary"], va="center", ha="left")
    ax.text(x[-1] + 0.18, EXP_TS[-1], "TS 预期 67%", fontsize=7, color=INK["secondary"], va="center", ha="left")
    ax.set_xticks(x)
    ax.set_xticklabels(SIZES)
    ax.set_xlim(-0.4, len(SIZES) + 0.45)
    ax.set_ylim(40, 95)
    ax.set_xlabel("玩家所在车队人数（Halo 5 全部模式，测试集约 300 万局）")
    ax.set_ylabel("胜率（%）")
    ax.legend(loc="upper left", fontsize=7.5)
    save(fig, "ch1", "1a_squad")


if __name__ == "__main__":
    main()
