"""图 2.11：长期进步——评分滞后于实力，胜率高出系统期望得分约 λv/K。

系统平稳（1000 轮，按分匹配 σ_q=100）后，随机抽 2% 玩家（200 人）每局实力 +v，共 +300 分（300/v 局），
之后停止并再观察 200 局。
(a) v = 0.5：进步者的平均实力增量与评分折算的实力增量（相对未进步玩家的回归线）；
(b) 斜坡第 101 局至结束的胜率减期望得分 W - Ē：点为模拟，实线为 λ*v/K，点线为 v/K。
参数：10,000 人，τ=200，K=16/32。
运行：python code/ch2/fig_improve.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import numpy as np

import model as m
from figstyle import INK, SERIES, WIDTH_FULL, save, use


def main():
    use()
    runs = m.improve_runs()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9), gridspec_kw=dict(wspace=0.3))
    v = 0.5
    r16 = runs[(v, 16)]
    ramp = int(r16["ramp"])
    t = np.arange(r16["lag"].size) + 1
    true_gain = np.minimum(t, ramp) * v
    ax.plot(t, true_gain, color=INK["primary"], lw=1.4, label="真实实力增量")
    for i, K in enumerate((16, 32)):
        r = runs[(v, K)]
        implied = true_gain - r["lag"]
        ax.plot(t, implied, color=SERIES[i], lw=1.4, ls=["-", "--"][i], label=f"评分折算的增量，$K$={K}")
    ax.axvline(ramp, color=INK["muted"], lw=0.8, ls=":")
    ax.text(ramp - 8, 20, "停止进步", ha="right", fontsize=7, color=INK["secondary"])
    ax.set_xlabel("开始进步后的局数")
    ax.set_ylabel("实力增量（Elo）")
    ax.set_xlim(0, t[-1]); ax.set_ylim(-20, 340)
    ax.legend(loc="upper left", fontsize=6.8)
    ax.set_title("(a) 评分滞后（每局 +0.5 分）", loc="left", fontsize=9)

    vv = np.linspace(0, 1.1, 50)
    for i, K in enumerate((16, 32)):
        lam = float(m.lambda_star(K, 100))
        bx.plot(vv, lam * vv / K * 100, color=SERIES[i], ls=["-", "--"][i], label=f"$\\lambda^* v/K$，$K$={K}")
        bx.plot(vv, vv / K * 100, color=SERIES[i], lw=0.9, ls=":")
        pts = []
        for vi in (0.25, 0.5, 1.0):
            r = runs[(vi, K)]
            rp = int(r["ramp"])
            pts.append((r["W"][100:rp].mean() - r["E"][100:rp].mean()) * 100)
        bx.plot([0.25, 0.5, 1.0], pts, "o" if K == 16 else "s", ms=4.5, color=SERIES[i], mec="white", mew=0.6,
                label=f"模拟，$K$={K}")
    bx.text(1.08, 1.08 / 32 * 100 - 0.25, "$v/K$", fontsize=6.6, color=INK["secondary"], ha="right", va="top")
    bx.set_xlabel("进步速度 $v$（Elo/局）")
    bx.set_ylabel("胜率 − 期望得分（百分点）")
    bx.set_xlim(0, 1.1); bx.set_ylim(0, 8.5)
    bx.legend(loc="upper left", fontsize=6.6)
    bx.set_title("(b) 胜率超出期望得分", loc="left", fontsize=9)
    save(fig, "ch2", "improve")

    for (vi, K), r in sorted(runs.items()):
        rp = int(r["ramp"])
        W, E = r["W"][100:rp].mean(), r["E"][100:rp].mean()
        drift = (r["Rmean"][rp - 1] - r["Rmean"][99]) / (rp - 100) / K
        lam = float(m.lambda_star(K, 100))
        print(f"v={vi} K={K}: W={W:.4f} E={E:.4f} W-E={100*(W-E):.2f}pp drift/K={100*drift:.2f}pp "
              f"lam*v/K={100*lam*vi/K:.2f} v/K={100*vi/K:.2f} lag={r['lag'][100:rp].mean():.1f} "
              f"theory 4lam v/(Kc)={4*lam*vi/(K*m.C):.1f} after W/E={r['W'][rp:].mean():.3f}/{r['E'][rp:].mean():.3f}")
    for K, r in m.improve_cohort10_runs().items():
        rp = int(r["ramp"])
        print(f"10% cohort, v=0.5, K={K}: W-E={100*(r['W'][100:rp].mean()-r['E'][100:rp].mean()):.2f}pp")


if __name__ == "__main__":
    main()
