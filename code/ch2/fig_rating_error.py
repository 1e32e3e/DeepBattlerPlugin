"""图 2.5：评分围绕实力的稳态误差约 9.3√K，误差的衰减时间比理想值 695/K 长。

(a) 稳态误差标准差（相对评分-实力回归线的残差）随 K 的变化：曲线为线性化公式
    σ_e² = Kλ/(2c(1-Kc/(4λ)))（随机匹配 λ=1；按分匹配取平稳刻度 λ*），点为模拟。
(b) 评分误差的自相关（K=16/32）：实线为模拟，虚线为平均场时间常数 4/(Kcκ) 的指数，
    灰色点线为理想时间常数 4/(Kc) ≈ 695/K。
模拟参数：(a) 4,000 人，2500 轮，预热 1000 轮后每 50 轮取一次残差；(b) 10,000 人中前 2,000 人第 1001–1400 轮的逐轮评分。
运行：python code/ch2/fig_rating_error.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import numpy as np

import model as m
from figstyle import INK, SERIES, WIDTH_FULL, save, use


def random_mixture_acf(K, lags, tau=m.TAU):
    """随机匹配：每人恢复速率 K c E[P(1-P)] 不同，总体自相关是各人指数的平均。"""
    z = m.PhiInv((np.arange(4000) + 0.5) / 4000)
    pq = m.gauss_expect(lambda x: m.F(x) * (1 - m.F(x)), tau * z, tau)
    rate = K * m.C * pq
    return np.exp(-np.outer(lags, rate)).mean(1)


def main():
    use()
    ks = m.k_sweep()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9), gridspec_kw=dict(wspace=0.3))
    KK = np.linspace(4, 68, 200)
    ax.plot(KK, m.sigma_e(KK), color=SERIES[0], label="公式，随机匹配（$\\lambda$=1）")
    ax.plot(KK, [float(m.sigma_e(k, m.lambda_star(k, 100))) for k in KK], color=SERIES[1], ls="--",
            label="公式，按分 $\\sigma_q$=100（$\\lambda^*$）")
    ax.plot(ks["Ks"], ks["resid_random"], "o", ms=4, color=SERIES[0], mec="white", mew=0.6, label="模拟，随机匹配")
    ax.plot(ks["Ks"], ks["resid_s100"], "s", ms=4, color=SERIES[1], mec="white", mew=0.6, label="模拟，按分 $\\sigma_q$=100")
    ax.plot(KK, 9.32 * np.sqrt(KK), color=INK["muted"], lw=0.9, ls=":", label="$9.32\\sqrt{K}$")
    ax.set_xlabel("K 因子")
    ax.set_ylabel("稳态评分误差 $\\sigma_e$（Elo）")
    ax.set_xlim(0, 70); ax.set_ylim(0, 140)
    ax.legend(loc="upper left", fontsize=6.6)
    ax.set_title("(a) 误差大小 $\\propto\\sqrt{K}$", loc="left", fontsize=9)

    lags = np.arange(0, 201, 2)
    cases = [("r_k16", 16, None, "随机匹配 $K$=16"), ("s100_k16", 16, 100, "按分 $\\sigma_q$=100，$K$=16"),
             ("s100_k32", 32, 100, "按分 $\\sigma_q$=100，$K$=32")]
    for i, (name, K, sq, lab) in enumerate(cases):
        r = m.get(name)
        acf = m.error_autocorr(r["snaps"].astype(float), r["s"][:m.N_SEQ], lags)
        bx.plot(lags, acf, color=SERIES[i], lw=1.6, label=f"{lab}（$e$ 折 {m.efold(lags, acf):.0f} 局）")
        th = random_mixture_acf(K, lags) if sq is None else np.exp(-lags / m.tau_R_meanfield(K, sq))
        bx.plot(lags, th, color=SERIES[i], lw=1.0, ls="--")
    for K in (16, 32):
        bx.plot(lags, np.exp(-lags / m.tau_R_ideal(K)), color=INK["muted"], lw=0.9, ls=":")
        t0 = 75 if K == 16 else 42
        bx.text(t0 + 4, np.exp(-t0 / m.tau_R_ideal(K)), f"695/{K}", fontsize=6.5, color=INK["secondary"])
    bx.axhline(np.exp(-1), color=INK["grid"], lw=0.8)
    bx.set_xlabel("滞后（局）")
    bx.set_ylabel("评分误差自相关")
    bx.set_xlim(0, 200); bx.set_ylim(-0.02, 1.0)
    bx.legend(loc="upper right", fontsize=6.4)
    bx.set_title("(b) 误差衰减：实线模拟，虚线公式", loc="left", fontsize=9)
    save(fig, "ch2", "rating_error")

    print("K sweep:", dict(Ks=ks["Ks"], random=np.round(ks["resid_random"], 1), s200=np.round(ks["resid_s200"], 1),
                           s100=np.round(ks["resid_s100"], 1), lam_s100=np.round(ks["lam_s100"], 2)))
    print("theory:", np.round(m.sigma_e(ks["Ks"]), 1), "simple", np.round(m.sigma_e_simple(ks["Ks"]), 1))
    for name, K, sq in (("r_k16", 16, None), ("s100_k16", 16, 100), ("s200_k16", 16, 200),
                        ("r_k32", 32, None), ("s100_k32", 32, 100), ("s200_k32", 32, 200)):
        r = m.get(name)
        acf = m.error_autocorr(r["snaps"].astype(float), r["s"][:m.N_SEQ], lags)
        th = m.efold(lags, random_mixture_acf(K, lags)) if sq is None else m.tau_R_meanfield(K, sq)
        print(f"{name}: efold sim {m.efold(lags, acf):.1f}, theory {th:.1f}, ideal {m.tau_R_ideal(K):.1f}")


if __name__ == "__main__":
    main()
