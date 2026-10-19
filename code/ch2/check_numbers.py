"""第二章正文中不出图的数值核对（各 fig_*.py 运行时也会打印各自用到的数值）。

1. 恒等式 W_T = Ē_T + (R_T - R_0)/(K T) 在所有标准实验中的最大误差；
2. 配对双方评分完全相等时，评分方差每局恰好增加 K²/4（σ_q = 0、初始全为 1500 的确定性配对）；
3. 线性化公式：σ_e、理想时间常数、λ*、修正时间常数；
4. 按分匹配各十分位的胜率分解（Ē 与 ΔR/(KT) 两项）。
运行：python code/ch2/check_numbers.py（文件名不能叫 numbers.py，会遮蔽标准库）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

import model as m


def main():
    worst = 0.0
    for name, cfg in m.EXPERIMENTS.items():
        if cfg["fmt"] == "ffa":
            continue
        r = m.get(name)
        dev = np.abs(r["W"] - (r["Ebar"] + (r["R_end"] - r["R_burn"]) / (r["K"] * r["games"]))).max()
        worst = max(worst, float(dev))
    print(f"1. identity max |W - (E + dR/KT)| over all 1v1/5v5 runs: {worst:.1e}")

    sim = m.EloSim(n_players=2000, K=16, fmt="1v1", mm="sbmm", sigma_q=0.0, seed=4)
    v0 = sim.R.var()
    for _ in range(3000):
        sim.step()
    print(f"2. exact-equal pairing: Var(R) growth after 3000 games = {sim.R.var() - v0:,.0f}; "
          f"K^2 t/4 = {16 ** 2 * 3000 / 4:,.0f}")

    for K in (10, 16, 20, 32, 40):
        print(f"3. K={K}: sigma_e={float(m.sigma_e(K)):.1f} (simple {float(m.sigma_e_simple(K)):.1f}), "
              f"tau_ideal={m.tau_R_ideal(K):.1f}, half-life={m.tau_R_ideal(K) * np.log(2):.1f}, "
              f"lambda*(100)={float(m.lambda_star(K, 100)):.3f}, lambda*(200)={float(m.lambda_star(K, 200)):.3f}")

    for name in ("s100_k16", "s20_k16", "s100_k32", "s20_k32"):
        r = m.get(name)
        W = m.by_decile(r["s"], r["W"]) * 100
        E = m.by_decile(r["s"], r["Ebar"]) * 100
        dR = m.by_decile(r["s"], (r["R_end"] - r["R_burn"]) / (r["K"] * r["games"])) * 100
        Rm = m.by_decile(r["s"], r["R_end"])
        sm = m.by_decile(r["s"], r["s"])
        top1 = r["W"][r["s"] >= np.quantile(r["s"], 0.99)].mean() * 100
        print(f"4. {name}: top1% {top1:.1f}%")
        for k in range(10):
            print(f"   decile {k + 1}: s={sm[k]:.0f} R={Rm[k]:.0f} W={W[k]:.1f}% E={E[k]:.1f}% dR/KT={dR[k]:+.2f}pp")


if __name__ == "__main__":
    main()
