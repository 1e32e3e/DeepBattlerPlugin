"""图：评分对 AR(1) 状态的吸收。(a) 残留在胜率里的状态方差比例 2(1-ρ)/((2-b)(1-(1-b)ρ))；
(b) AR(0.9, 60) 下结果的自相关：评分不动（K=0）与 Elo（K=20），以及无波动的诚实 Elo。"""
import numpy as np
import matplotlib.pyplot as plt

from _common import CH, INK, SERIES, WIDTH_FULL, save, use
from experiments import K_ELO, run_ar_absorption
from model import ar1_retained, elo_error_sd, elo_gain, linear_outcome_acf, slope_attenuation
from experiments import SIGMA_Q


def main():
    use()
    d = run_ar_absorption()
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9))
    ax = axes[0]
    rr = np.linspace(0.3, 0.995, 200)
    for i, K in enumerate(d["Ks"]):
        b = elo_gain(float(K))
        ax.plot(rr, [ar1_retained(r, b) for r in rr], color=SERIES[i], label=f"K={int(K)}（b={b:.3f}）")
        ax.plot(d["rhos"], d[f"retained_K{int(K)}"], "o", color=SERIES[i], ms=3.5, mec="white", mew=0.6)
    ax.set_xlabel("状态持续性 ρ（平均记忆约 1/(1−ρ) 局）")
    ax.set_ylabel("残留比例")
    ax.set_ylim(0, 1.05)
    ax.set_title("(a) 评分没吸收掉的状态方差", loc="left")
    ax.legend(loc="lower left", fontsize=7.5)
    ax = axes[1]
    h = np.arange(1, 21)
    series = [("ar_K0", 0, 0.9, 60, "AR(0.9, 60)，评分不动"),
              ("ar_Kelo", K_ELO, 0.9, 60, f"AR(0.9, 60)，Elo K={K_ELO}"),
              ("none_Kelo", K_ELO, 0.0, 0.0, f"无波动，Elo K={K_ELO}")]
    for i, (tag, K, rho, sd, lab) in enumerate(series):
        # 用实力差分布上的平均斜率 E[F'] 代替 F'(0)（κ_F），近似计入 F 的非线性
        var_d = sd ** 2 * (ar1_retained(rho, elo_gain(K)) if K else 1.0) + (elo_error_sd(K) ** 2 if K else 0.0)
        kap = slope_attenuation(np.sqrt(var_d + SIGMA_Q ** 2))
        th = linear_outcome_acf(rho, sd, K, hmax=20, kappa=kap)
        ax.plot(h, th, color=SERIES[i], lw=1.4, label=lab)
        ax.plot(h, d[f"acf_{tag}"], "o", color=SERIES[i], ms=3.2, mec="white", mew=0.6)
    ax.axhline(0, color=INK["muted"], lw=0.8)
    ax.set_xlabel("滞后 $h$（局）")
    ax.set_ylabel("Corr$(y_t, y_{t+h})$")
    ax.set_title("(b) 结果自相关（线：线性近似；点：模拟）", loc="left")
    ax.legend(loc="upper right", fontsize=7.5)
    fig.tight_layout()
    save(fig, CH, "ar_absorb")


if __name__ == "__main__":
    main()
