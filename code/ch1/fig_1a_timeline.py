"""图 1a-1：评分模型与匹配机制研究的时间线（1927–2026）。

每个点是一篇（一部）文献或一个标志性事件，年份取正式发表年（预印本取首次公开年）；
条目与第一章 1a 节引用的文献一一对应。横轴在 1995 年处换刻度：1925–1995 压缩，1995–2027 放大。
标签用贪心法逐行摆放以避免重叠。无随机性。运行：python code/ch1/fig_1a_timeline.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt

from figstyle import INK, SERIES, WIDTH_FULL, save, use

LANES = [
    ("成对比较\n与统计基础", [
        (1927, "Thurstone"), (1929, "Zermelo"), (1951, "Mosteller"), (1952, "Bradley–Terry"),
        (1959, "Luce 选择公理"), (1975, "Plackett"), (1995, "Glickman 综述"),
    ]),
    ("评分系统", [
        (1960, "Elo（USCF）"), (1970, "FIDE 采用"), (1978, "Elo 专著"), (1999, "Glicko"),
        (2001, "Glicko-2"), (2006, "TrueSkill"), (2007, "TTT"), (2008, "WHR"), (2011, "Weng–Lin"),
        (2018, "TrueSkill 2"), (2021, "Elo-MMR"), (2024, "OpenSkill"), (2025, "TTT 软件包"),
    ]),
    ("Elo 的理论\n与非传递性", [
        (1992, "Stern"), (2011, "Regan–Haworth"), (2015, "Jabin–Junca"), (2017, "Aldous"), (2018, "mElo"),
        (2019, "Düring 等"), (2020, "陀螺结构"), (2023, "Bertrand 等"), (2024, "Olesker-Taylor"),
        (2024.8, "Cortez 等"), (2025, "Tang 等"),
    ]),
    ("匹配机制", [
        (2004, "Hamlet"), (2012, "Delalleau 等"), (2016, "MPMD"), (2017, "EOMM"),
        (2017.4, "Alman–McKay"), (2017.8, "EA DDA"), (2020, "OptMatch"), (2021, "GloMatch"),
        (2022, "QuickSkill"), (2022.5, "凸延迟"), (2024, "EnMatch"), (2024.3, "CUPID"),
        (2024.6, "Yuksel"), (2026, "Chen 等"), (2026.4, "成本平衡"),
    ]),
    ("游戏实证", [
        (2013, "Halo Reach"), (2013.4, "HoN"), (2014, "LoL 轨迹"), (2018, "Kou 等"), (2018.4, "Sapienza 等"),
        (2019, "王者荣耀"), (2020, "PUBG"), (2021, "Do 等"), (2023, "Lichess"), (2024, "Kang 等"),
        (2024.3, "CS:GO"), (2024.6, "Deng 等"), (2025, "Rosenthal"),
    ]),
]

X0, XB, X1 = 1925.0, 1995.0, 2027.5
FRAC_LEFT = 0.2  # 1925–1995 占横轴的比例


def xmap(year):
    if year <= XB:
        return FRAC_LEFT * (year - X0) / (XB - X0)
    return FRAC_LEFT + (1 - FRAC_LEFT) * (year - XB) / (X1 - XB)


def main():
    use()
    n_rows = 5
    lane_h = n_rows + 0.9
    fig, ax = plt.subplots(figsize=(WIDTH_FULL, 4.5))
    ax.set_xlim(-0.01, 1.0)
    total_h = lane_h * len(LANES)
    ax.set_ylim(-0.4, total_h)
    ax.axis("off")
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    inv = ax.transData.inverted()

    for li, (name, events) in enumerate(LANES):
        base = total_h - (li + 1) * lane_h + 0.35
        color = SERIES[li]
        ax.plot([0, 1], [base, base], color=INK["grid"], lw=0.8, zorder=1)
        ax.text(-0.015, base + 0.15, name, ha="right", va="bottom", fontsize=7.5, color=INK["primary"],
                linespacing=1.1)
        occupied = [[] for _ in range(n_rows)]
        lines = []  # (x, row)：已画引线
        for year, label in sorted(events):
            x = xmap(year)
            placed = False
            for r in range(n_rows):
                y = base + 0.55 + r * 0.95
                opts = (("left", 0.004), ("right", -0.004))
                if x > 0.82:
                    opts = opts[::-1]
                for ha, dx in opts:
                    t = ax.text(x + dx, y, label, fontsize=6.5, color=INK["primary"], va="center", ha=ha, zorder=4,
                                bbox=dict(boxstyle="square,pad=0.08", fc="white", ec="none"))
                    bb = t.get_window_extent(renderer)
                    (x_a, _), (x_b, _) = inv.transform([(bb.x0, bb.y0), (bb.x1, bb.y1)])
                    x_a -= 0.006
                    x_b += 0.006
                    if x_b <= 1.06 and x_a >= -0.01 and all(x_b <= a or x_a >= b for a, b in occupied[r]):
                        occupied[r].append((x_a, x_b))
                        lines.append((x, r))
                        ax.plot([x, x], [base, y], color=color, lw=0.6, alpha=0.8, zorder=1)
                        placed = True
                        break
                    t.remove()
                if placed:
                    break
            if not placed:
                raise RuntimeError(f"无法放置标签：{label} ({year})")
            ax.plot([x], [base], marker="o", ms=3.6, color=color, mec="white", mew=0.6, zorder=3)

    # 年份刻度
    for yr in [1925, 1950, 1975, 1995, 2000, 2005, 2010, 2015, 2020, 2025]:
        x = xmap(yr)
        ax.plot([x, x], [-0.15, 0.05], color=INK["axis"], lw=0.8)
        ax.text(x, -0.25, str(yr), ha="center", va="top", fontsize=7, color=INK["muted"])
    ax.plot([0, 1], [0.0, 0.0], color=INK["axis"], lw=0.8)
    xb = xmap(XB)
    ax.plot([xb, xb], [0.0, total_h - 0.2], color=INK["muted"], lw=0.6, ls=(0, (2, 3)))
    ax.text(xb + 0.005, total_h - 0.25, "1995 年后横轴放大约 7 倍", fontsize=6.5, color=INK["muted"],
            ha="left", va="top")
    save(fig, "ch1", "1a_timeline")


if __name__ == "__main__":
    main()
