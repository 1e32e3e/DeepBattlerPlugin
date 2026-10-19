"""图 2.10：自相关的状态起伏（AR(1)）——评分只能部分追上，窗口胜率比二项分布更分散。

状态 u_{t+1} = φu_t + sqrt(1-φ²)σ_u ε，σ_u = 100，φ = 0.99（相关时间约 100 局）；当局实力 s + u_t。
(a) 按分匹配（σ_q=100，K=16）中一名玩家：当局实力 s+u_t 与评分折算的实力 μ + (R_t - a_t)/λ_t；
(b) n 局窗口胜率的人内方差 / 二项方差 p̂(1-p̂)/n：点为模拟（每人 2000 局切成 2000/n 个窗口），
    曲线为附录中的近似公式（model.var_ratio_sbmm / var_ratio_random_ar）。
参数：10,000 人，τ=200，3000 轮，统计第 1001–3000 局；评分轨迹取第 1001–1400 局。
运行：python code/ch2/fig_ar1.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

import model as m
from figstyle import INK, LINESTYLES, SERIES, WIDTH_FULL, save, use


def main():
    use()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9), gridspec_kw=dict(wspace=0.3))
    r = m.get("s100_k16_ar")
    sn = r["snaps"].astype(float)
    s = r["s"][:m.N_SEQ]
    u = r["u_snap"].T            # (人, 局)
    shat = np.empty_like(sn)
    for i in range(sn.shape[0]):
        lam, a = np.polyfit(s, sn[i], 1)
        shat[i] = (sn[i] - a) / lam
    # 选一名状态起伏明显、实力接近中位数的玩家
    cand = np.where(np.abs(s - m.MU) < 60)[0]
    j = cand[np.argmax(u[cand].max(1) - u[cand].min(1))]
    t = np.arange(sn.shape[0]) + 1001
    ax.plot(t, s[j] + u[j], color=SERIES[0], lw=1.4, label="当局实力 $s+u_t$")
    ax.plot(t, shat[:, j], color=SERIES[1], lw=1.4, ls="--", label="评分折算的实力")
    ax.axhline(s[j], color=INK["muted"], lw=0.9, ls=":")
    ax.text(t[0] + 6, s[j] - 8, "长期实力 $s$", ha="left", va="top", fontsize=7.5, color=INK["secondary"])
    ax.set_xlabel("局数")
    ax.set_ylabel("实力（Elo）")
    ax.set_xlim(t[0], t[-1])
    ax.legend(loc="lower left", fontsize=7.5)
    ax.set_title("(a) 一名玩家的状态与评分（$K$=16）", loc="left", fontsize=9)

    ns = np.array([5, 10, 20, 50, 100, 200, 400])
    nn = np.geomspace(5, 400, 100)
    cases = [("r_k16_ar", "随机匹配 + 状态，$K$=16", lambda n: m.var_ratio_random_ar(n, 100.0)),
             ("s100_k16_ar", "按分 + 状态，$K$=16", lambda n: m.var_ratio_sbmm(n, 16, 100, ar_sd=100.0)),
             ("s100_k32_ar", "按分 + 状态，$K$=32", lambda n: m.var_ratio_sbmm(n, 32, 100, ar_sd=100.0)),
             ("s100_k16", "按分、实力固定，$K$=16", lambda n: m.var_ratio_sbmm(n, 16, 100))]
    handles = []
    for i, (name, lab, th) in enumerate(cases):
        rr = m.get(name)
        vr = [m.window_var_ratio(rr["seq_y"], n) for n in ns]
        bx.plot(nn, th(nn), color=SERIES[i], ls=LINESTYLES[i], lw=1.3)
        bx.plot(ns, vr, "o", ms=3.8, color=SERIES[i], mec="white", mew=0.5)
        handles.append(Line2D([], [], color=SERIES[i], ls=LINESTYLES[i], lw=1.3, marker="o", ms=3.8,
                              mec="white", mew=0.5, label=lab))
        print(name, "sim", np.round(vr, 2), "theory", np.round(th(ns.astype(float)), 2))
    bx.axhline(1, color=INK["secondary"], lw=0.9, ls=":")
    handles.append(Line2D([], [], color=INK["secondary"], lw=0.9, ls=":", label="二项分布（各局独立）"))
    bx.set_xscale("log")
    bx.set_xticks(ns); bx.set_xticklabels([str(n) for n in ns])
    bx.minorticks_off()
    bx.set_xlabel("窗口长度 $n$（局）")
    bx.set_ylabel("窗口胜率方差 / 二项方差")
    bx.set_ylim(0, 7.2)
    bx.legend(handles=handles, loc="upper left", fontsize=7.5, handlelength=2.6)
    bx.set_title("(b) 窗口胜率的离散程度", loc="left", fontsize=9)
    save(fig, "ch2", "ar1")

    # 正文数值
    for name in ("s100_k16_ar", "s100_k32_ar", "r_k16_ar"):
        rr = m.get(name)
        y = rr["seq_y"].astype(float)
        hw, hn, cw, cn = rr["hot_cold"]
        yc = y - y.mean(1, keepdims=True)
        acf = [float((yc[:, :-L] * yc[:, L:]).mean() / (yc * yc).mean()) for L in (1, 5, 20)]
        print(name, f"hot(u>σ) {hw / hn:.3f} cold(u<-σ) {cw / cn:.3f}",
              "deciles", np.round(m.by_decile(rr["s"], rr["W"])[[0, 9]] * 100, 1), "acf", np.round(acf, 4),
              "share of 100-game windows >=60%", float(np.mean(y.reshape(y.shape[0], -1, 100).mean(2) >= 0.6)))
        # 评分对状态的吸收份额：评分误差（相对回归线，折算到实力单位）对下一局所用状态 u 的回归系数
        sn_, s_ = rr["snaps"], rr["s"][:m.N_SEQ]
        ab = []
        for i in range(0, sn_.shape[0] - 1, 10):
            lam, a0 = np.polyfit(s_, sn_[i], 1)
            e = sn_[i] - (a0 + lam * s_)
            ab.append(np.polyfit(rr["u_snap"][i + 1], e, 1)[0] / lam)
        print("   absorbed share (sim)", round(float(np.mean(ab)), 3))
    for K in (16, 32):
        a = 1 / m.tau_R_meanfield(K, 100)
        print(K, "alpha", round(a, 4), "absorbed (mean-field)", round(m.absorbed_share(a, 0.99), 3),
              "absorbed (ideal Kc/4)", round(m.absorbed_share(K * m.C / 4, 0.99), 3))
    for name in ("s100_k16", "r_k16", "s20_k16"):
        y = m.get(name)["seq_y"].astype(float)
        print(name, "share of 100-game windows >=60%", float(np.mean(y.reshape(y.shape[0], -1, 100).mean(2) >= 0.6)))


if __name__ == "__main__":
    main()
