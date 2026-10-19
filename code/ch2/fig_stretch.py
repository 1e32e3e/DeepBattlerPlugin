"""图 2.7：严格按分匹配下评分刻度的"拉伸"——理想化模型的性质，不是真实数据中的观测。

(a) 评分对实力的回归斜率 λ(t)（初始评分 = 真实实力，λ0 = 1）：实线为模拟，虚线为平均场方程，
    点线为配对评分完全相等时的上包络 sqrt(1 + K²t/(4τ²))。
(b) 平稳伸缩系数 λ* = 1/(1 - σ_e²/σ_q²) 随匹配噪声 σ_q 的变化；σ_q ≤ σ_e 时不存在平稳刻度。
参数：(a) 2,000 人，τ=200，K=16，10,000 轮；(b) 点为 (a) 第 10,000 轮的 λ，以及 10,000 人、
    初始评分全为 1500、K=32 的标准实验第 3,000 轮的 λ。
运行：python code/ch2/fig_stretch.py
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
    runs = m.stretch_runs()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9), gridspec_kw=dict(wspace=0.3))
    K = 16
    for i, sq in enumerate((20, 50, 100, 200)):
        r = runs[sq]
        ax.plot(r["t"], r["lam"], color=SERIES[i], lw=1.6, label=f"$\\sigma_q$={sq}")
        tt, lam = m.lambda_ode(K, sq, r["t"][-1], lam0=1.0)
        ax.plot(tt[::50], lam[::50], color=SERIES[i], lw=1.0, ls="--")
    t = np.linspace(0, 10000, 200)
    ax.plot(t, np.sqrt(1 + K ** 2 * t / (4 * m.TAU ** 2)), color=INK["secondary"], lw=0.9, ls=":",
            label="上包络 $\\sqrt{1+K^2t/4\\tau^2}$")
    ax.set_xlabel("局数 $t$")
    ax.set_ylabel("评分-实力斜率 $\\lambda$")
    ax.set_xlim(0, 10000); ax.set_ylim(0.9, 4.4)
    ax.legend(loc="upper left", fontsize=6.6)
    ax.set_title("(a) 刻度随时间（$K$=16）", loc="left", fontsize=9)

    for j, KK in enumerate((16, 32)):
        thr = float(m.sigma_e(KK))
        sq = np.linspace(thr * 1.03, 300, 300)
        bx.plot(sq, m.lambda_star(KK, sq), color=SERIES[j], ls=["-", "--"][j], label=f"$\\lambda^*$，$K$={KK}")
        bx.axvline(thr, color=SERIES[j], lw=0.8, ls=":")
        if KK == 16:
            bx.text(thr - 3, 4.0, f"$\\sigma_e$={thr:.0f}", fontsize=6.6, color=INK["primary"], ha="right")
        else:
            bx.text(thr + 4, 1.06, f"$\\sigma_e$={thr:.0f}", fontsize=6.6, color=INK["primary"], ha="left")
    bx.plot([50, 100, 200], [runs[q]["lam"][-1] for q in (50, 100, 200)], "o", ms=4, color=SERIES[0],
            mec="white", mew=0.6, label="模拟 $K$=16，$t$=10,000")
    lam32 = [m.get(f"s{q}_k32")["lam_t"][-1] for q in (100, 200)]
    bx.plot([100, 200], lam32, "s", ms=4, color=SERIES[1], mec="white", mew=0.6, label="模拟 $K$=32，$t$=3,000")
    bx.axhline(1, color=INK["muted"], lw=0.8)
    bx.set_xlabel("匹配噪声 $\\sigma_q$（Elo）")
    bx.set_ylabel("平稳斜率 $\\lambda^*$")
    bx.set_xlim(0, 300); bx.set_ylim(0.9, 4.4)
    bx.legend(loc="upper right", fontsize=6.6)
    bx.set_title("(b) 平稳刻度存在的条件", loc="left", fontsize=9)
    save(fig, "ch2", "stretch")

    for sq, r in runs.items():
        tt, lam = m.lambda_ode(K, sq, 10000, lam0=1.0)
        idx = [10, 30, 60, 100]
        print(f"sigma_q={sq}: sim", [(int(r['t'][i]), round(float(r['lam'][i]), 2)) for i in idx],
              "ode", [round(float(lam[int(r['t'][i])]), 2) for i in idx],
              "envelope", [round(float(np.sqrt(1 + K**2 * r['t'][i] / (4 * m.TAU**2))), 2) for i in idx],
              "lambda*", float(m.lambda_star(K, sq)))
    for KK in (16, 32):
        print(KK, "threshold sigma_e", float(m.sigma_e(KK)), "paired diff sd", np.sqrt(2) * float(m.sigma_e(KK)))
        for q in (50, 60, 80, 100, 150, 200):
            print("  lambda*", q, float(m.lambda_star(KK, q)))


if __name__ == "__main__":
    main()
