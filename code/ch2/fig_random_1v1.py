"""图 2.3：随机匹配 1v1 的期望胜率随实力百分位变化，W(q) = Φ(ρ z_q)，ρ = τ/sqrt(τ² + σ_d'²)。

(a) 群体离散度 τ = 100/200/300（σ_d = 295.7）；(b) 游戏随机性：单局独立噪声 σ_x = 0/150/300，
    等效 σ_d' = sqrt(σ_d² + 2σ_x²)。曲线为闭式公式，点为模拟（每 5% 百分位一组的平均胜率）。
模拟参数：10,000 人，s ~ N(1500, τ²)，K=16，随机配对，3000 轮，统计第 1001–3000 局。
运行：python code/ch2/fig_random_1v1.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import numpy as np

import model as m
from figstyle import INK, SERIES, WIDTH_FULL, save, use


def binned(name, nb=20):
    r = m.get(name)
    q = (np.argsort(np.argsort(r["s"])) + 0.5) / r["s"].size
    b = np.minimum((q * nb).astype(int), nb - 1)
    return (np.array([q[b == k].mean() for k in range(nb)]),
            np.array([r["W"][b == k].mean() for k in range(nb)]))


def curve(q, tau, sigma_d=m.SIGMA_D):
    return m.Phi(m.rho(tau, sigma_d) * m.PhiInv(q))


def main():
    use()
    q = np.linspace(0.001, 0.999, 400)
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9), sharey=True,
                                 gridspec_kw=dict(wspace=0.08))
    for i, (tau, name) in enumerate(((100, "r_k16_tau100"), (200, "r_k16"), (300, "r_k16_tau300"))):
        ax.plot(q * 100, curve(q, tau) * 100, color=SERIES[i], ls=["-", "--", "-."][i],
                label=f"$\\tau={tau}$（$\\rho$={m.rho(tau):.2f}）")
        x, y = binned(name)
        ax.plot(x * 100, y * 100, "o", ms=3.2, color=SERIES[i], mec="white", mew=0.6)
    ax.set_xlabel("实力百分位 $q$（%）")
    ax.set_ylabel("长期胜率 $W$（%）")
    ax.set_xlim(0, 100); ax.set_ylim(0, 100)
    ax.axhline(50, color=INK["muted"], lw=0.8, ls=":")
    ax.legend(loc="upper left", fontsize=7)
    ax.set_title("(a) 群体实力离散度 $\\tau$", loc="left", fontsize=9)

    for i, (sx, name) in enumerate(((0, "r_k16"), (150, "r_k16_noise150"), (300, None))):
        sd = math.sqrt(m.SIGMA_D ** 2 + 2 * sx ** 2)
        bx.plot(q * 100, curve(q, 200, sd) * 100, color=SERIES[i], ls=["-", "--", "-."][i],
                label=f"$\\sigma_x={sx}$（$\\sigma_d'$={sd:.0f}）")
        if name:
            x, y = binned(name)
            bx.plot(x * 100, y * 100, "o", ms=3.2, color=SERIES[i], mec="white", mew=0.6)
    bx.set_xlabel("实力百分位 $q$（%）")
    bx.set_xlim(0, 100)
    bx.axhline(50, color=INK["muted"], lw=0.8, ls=":")
    bx.legend(loc="upper left", fontsize=7)
    bx.set_title("(b) 单局随机性 $\\sigma_x$（$\\tau=200$）", loc="left", fontsize=9)
    save(fig, "ch2", "random_1v1")

    # 正文用到的数值
    print("max |F(d) - Phi(d/295.7)| =", float(np.max(np.abs(m.F(np.linspace(-1500, 1500, 30001)) -
                                                         m.Phi(np.linspace(-1500, 1500, 30001) / m.SIGMA_D)))))
    for tau in (100, 150, 200, 300, 400):
        rr = m.rho(tau)
        # 百分位点值与组内平均（精确逻辑斯蒂、正态实力）
        z = m.PhiInv(np.linspace(0.9, 0.99999, 20001))
        top10 = float(np.mean(m.winrate_random_exact(m.MU + tau * z, tau=tau)))
        z1 = m.PhiInv(np.linspace(0.99, 0.999999, 20001))
        top1 = float(np.mean(m.winrate_random_exact(m.MU + tau * z1, tau=tau)))
        print(f"tau={tau}: rho={rr:.3f} rho^2={rr**2:.2f} W(75%)={m.Phi(rr*0.6745):.3f} W(90%)={m.Phi(rr*1.2816):.3f}"
              f" top10avg={top10:.3f} top1avg={top1:.3f}")
    r = m.get("r_k16")
    print("sim deciles K16:", np.round(m.by_decile(r["s"], r["W"]) * 100, 1))
    r32 = m.get("r_k32")
    print("sim deciles K32:", np.round(m.by_decile(r32["s"], r32["W"]) * 100, 1))
    z = m.PhiInv((np.arange(100000) + 0.5) / 100000)
    Wex = m.winrate_random_exact(m.MU + 200 * z)
    print("exact decile averages:", np.round(Wex.reshape(10, -1).mean(1) * 100, 1))
    print("sd individual W K16:", r["W"].std())
    top1 = r["s"] >= np.quantile(r["s"], 0.99)
    print("sim top1%:", r["W"][top1].mean(), "bottom1%:", r["W"][r["s"] <= np.quantile(r["s"], 0.01)].mean())
    rn = m.get("r_k16_noise150")
    print("noise150 deciles:", np.round(m.by_decile(rn["s"], rn["W"]) * 100, 1), "slope", m.fit_line(rn["s"], rn["R_end"]))
    print("noise 150 effective sd", math.sqrt(m.SIGMA_D**2 + 2*150**2), "ratio", m.SIGMA_D/math.sqrt(m.SIGMA_D**2 + 2*150**2))


if __name__ == "__main__":
    main()
