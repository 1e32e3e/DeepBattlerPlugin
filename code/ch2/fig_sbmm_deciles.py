"""图 2.4：按分匹配把各实力十分位的胜率压向 50%，剩余偏离由匹配窗口宽度 σ_q 决定。

(a) K=16 下各实力十分位的长期胜率：随机匹配与按分匹配（σ_q = 200/100/50/20）。
(b) 最强 10% 玩家的胜率随 σ_q 的变化：点为模拟（K=16/32），曲线为平稳刻度下的窗口边缘公式
    （model.sbmm_edge_winrate，仅在 σ_q > σ_e 时存在平稳刻度）。
模拟参数：10,000 人，τ=200，按 R+N(0,σ_q²) 排序相邻配对，3000 轮，统计第 1001–3000 局。
运行：python code/ch2/fig_sbmm_deciles.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import numpy as np

import model as m
from figstyle import INK, LINESTYLES, SERIES, WIDTH_FULL, save, use


def main():
    use()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9), gridspec_kw=dict(wspace=0.3))
    series = [("随机匹配", "r_k16"), ("按分 $\\sigma_q$=200", "s200_k16"), ("按分 $\\sigma_q$=100", "s100_k16"),
              ("按分 $\\sigma_q$=50", "s50_k16"), ("按分 $\\sigma_q$=20", "s20_k16")]
    x = np.arange(1, 11)
    for i, (lab, name) in enumerate(series):
        r = m.get(name)
        d = m.by_decile(r["s"], r["W"]) * 100
        ax.plot(x, d, marker="o", ms=3.5, color=SERIES[i], ls=LINESTYLES[i % 4], lw=1.4, label=lab,
                mec="white", mew=0.5)
    ax.axhline(50, color=INK["muted"], lw=0.8, ls=":")
    ax.set_xticks(x)
    ax.set_xlabel("实力十分位（1 = 最弱，10 = 最强）")
    ax.set_ylabel("长期胜率（%）")
    ax.set_ylim(10, 90)
    ax.legend(loc="upper left", fontsize=7.5)
    ax.set_title("(a) 各十分位胜率（$K=16$）", loc="left", fontsize=9)

    z = m.PhiInv(np.linspace(0.9, 0.99999, 4001))
    for j, K in enumerate((16, 32)):
        thr = float(m.sigma_e(K))
        sq = np.linspace(thr * 1.02, 400, 300)
        top = np.array([np.mean(m.sbmm_edge_winrate(z, K, q)) for q in sq]) * 100
        bx.plot(sq, top, color=SERIES[j], ls=["-", "--"][j], label=f"公式 $K={K}$")
        pts = []
        for q in (20, 50, 100, 200):
            r = m.get(f"s{q}_k{K}")
            pts.append(m.by_decile(r["s"], r["W"])[9] * 100)
        off = -4 if K == 16 else 4      # 水平错开，避免两组点重叠
        bx.plot(np.array([20, 50, 100, 200]) + off, pts, "o" if K == 16 else "s", ms=4, color=SERIES[j], mec="white", mew=0.6,
                label=f"模拟 $K={K}$")
        bx.axvline(thr, color=SERIES[j], lw=0.8, ls=":")
    rand = m.by_decile(m.get("r_k16")["s"], m.get("r_k16")["W"])[9] * 100
    bx.axhline(rand, color=INK["secondary"], lw=0.9, ls="-.")
    bx.text(398, rand - 1.2, "随机匹配 83%", ha="right", va="top", fontsize=7.5, color=INK["primary"])
    bx.text(39, 87, "$\\sigma_q=\\sigma_e$", fontsize=7.5, color=INK["primary"], ha="left")
    bx.set_xlabel("匹配噪声 $\\sigma_q$（Elo）")
    bx.set_ylabel("最强 10% 的胜率（%）")
    bx.set_xlim(0, 400); bx.set_ylim(45, 90)
    bx.legend(loc="center right", fontsize=7.5, bbox_to_anchor=(1.0, 0.42))
    bx.set_title("(b) 最强 10% 与窗口宽度", loc="left", fontsize=9)
    save(fig, "ch2", "sbmm_deciles")


if __name__ == "__main__":
    main()
