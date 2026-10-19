"""图：在数据空间评估——校准图，以及“把玩家胜率当目标”在按分匹配下学不到实力。

(a) 随机匹配下，Elo 评分给出的预测胜率 E=F(R_i-R_j) 的校准图（K=16/32/64）。
    评分噪声使预测“过于自信”：拟合 y~F(gamma*(R_i-R_j)) 得到 gamma<1。
(b) 每名玩家长期胜率 vs 真实实力：随机匹配（胜率随实力单调变化）与按分匹配（几乎都在 50% 附近）。
参数：N=2000 人，实力 ~ N(0, 200^2)，评分初值 0，每轮每人一局；
(a) 前 300 轮收敛，后 300 轮评估；(b) K=16，前 500 轮收敛，后 1000 轮统计胜率，按分匹配噪声 sigma_q=25。
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from figstyle import use, save, SERIES, INK, WIDTH_FULL  # noqa: E402
from ch4_model import F, population_elo, reliability, fit_scale  # noqa: E402

CACHE = HERE / "cache" / "calibration.npz"
KS = [16, 32, 64]
BINS = np.linspace(0, 1, 21)


def simulate():
    if CACHE.exists():
        return dict(np.load(CACHE))
    out = {}
    for i, K in enumerate(KS):
        rng = np.random.default_rng(100 + i)
        r = population_elo(rng, 2000, 200.0, K, rounds=600, eval_from=300, matching="random")
        mp, fr, n = reliability(r["E"], r["y"], BINS)
        out[f"mp{K}"], out[f"fr{K}"], out[f"n{K}"] = mp, fr, n
        out[f"gamma{K}"] = fit_scale(r["d"], r["y"])
        # 对数损失：原始预测、重标定预测、真实概率（oracle）
        def ll(p, y):
            p = np.clip(p, 1e-9, 1 - 1e-9)
            return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
        out[f"ll_raw{K}"] = ll(r["E"], r["y"])
        out[f"ll_cal{K}"] = ll(F(out[f"gamma{K}"] * r["d"]), r["y"])
        out[f"ll_true{K}"] = ll(r["p"], r["y"])
        out[f"rmse{K}"] = np.sqrt(np.mean((r["rating"] - r["rating"].mean() - r["skill"] + r["skill"].mean()) ** 2))
    for j, m in enumerate(["random", "sbmm"]):
        rng = np.random.default_rng(300 + j)
        r = population_elo(rng, 2000, 200.0, 16, rounds=1500, eval_from=500, matching=m,
                           sigma_q=25.0, record=False)
        out[f"skill_{m}"] = r["skill"]
        out[f"wr_{m}"] = r["wins"] / r["games"]
        out[f"rating_{m}"] = r["rating"]
    CACHE.parent.mkdir(exist_ok=True)
    np.savez(CACHE, **out)
    return out


def main():
    use()
    z = simulate()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(WIDTH_FULL, 3.0))

    ax1.axhline(0, color=INK["muted"], lw=0.9, zorder=1)
    ax1.text(0.99, 0.35, "完美校准", fontsize=7.5, color=INK["muted"], ha="right")
    for i, K in enumerate(KS):
        ok = z[f"n{K}"] >= 200
        ax1.plot(z[f"mp{K}"][ok], 100 * (z[f"fr{K}"][ok] - z[f"mp{K}"][ok]), marker="o", ms=3.5,
                 color=SERIES[i], ls=["-", "--", "-."][i], lw=1.3, mec="white", mew=0.6,
                 label=f"$K={K}$（$\\hat\\gamma={float(z[f'gamma{K}']):.2f}$）")
    ax1.set_xlim(0, 1)
    ax1.set_ylim(-7, 7)
    ax1.set_xlabel("系统预测胜率 $E=F(R_i-R_j)$")
    ax1.set_ylabel("实际频率 − 预测（百分点）")
    ax1.set_title("(a) 校准偏差（随机匹配）", loc="left")
    ax1.text(0.97, 2.6, "预测偏向两端\n（过于自信）", fontsize=7.5, color=INK["secondary"], ha="right", va="bottom")
    ax1.legend(loc="lower left", fontsize=7.2)

    ss = np.linspace(-650, 650, 300)
    rng = np.random.default_rng(0)
    pool = rng.normal(0, 200, 200000)
    theo = np.array([F(s - pool).mean() for s in ss])
    sub = np.random.default_rng(1).choice(2000, 700, replace=False)
    ax2.scatter(z["skill_random"][sub], 100 * z["wr_random"][sub], s=5, color=SERIES[0], alpha=0.45,
                lw=0, label="随机匹配")
    ax2.scatter(z["skill_sbmm"][sub], 100 * z["wr_sbmm"][sub], s=5, color=SERIES[1], alpha=0.55,
                lw=0, label="按分匹配")
    ax2.plot(ss, 100 * theo, color=INK["secondary"], lw=1.0)
    ax2.annotate("随机匹配理论值", (-300, 100 * F(-300 - pool).mean()), xytext=(25, -22),
                 textcoords="offset points", fontsize=7.5, color=INK["secondary"],
                 arrowprops=dict(arrowstyle="-", color=INK["muted"], lw=0.6))
    ax2.text(560, 41, "按分匹配：\n几乎都在 50%", fontsize=7.5, color=INK["primary"], ha="right", va="top")
    ax2.set_xlim(-650, 650)
    ax2.set_ylim(0, 100)
    ax2.set_xlabel("真实实力 $s_i$（Elo）")
    ax2.set_ylabel("长期胜率（%）")
    ax2.set_title("(b) 把“玩家胜率”当目标", loc="left")
    leg = ax2.legend(loc="upper left", fontsize=7.5, markerscale=2.5)
    for h in leg.legend_handles:
        h.set_alpha(1)
    fig.tight_layout()
    save(fig, "ch4", "fig_calibration")

    for K in KS:
        print(f"K={K}: gamma={float(z[f'gamma{K}']):.3f}, logloss raw={float(z[f'll_raw{K}']):.4f}, "
              f"recal={float(z[f'll_cal{K}']):.4f}, oracle={float(z[f'll_true{K}']):.4f}, rating RMSE={float(z[f'rmse{K}']):.1f}")
    for m in ["random", "sbmm"]:
        s, w, R = z[f"skill_{m}"], z[f"wr_{m}"], z[f"rating_{m}"]
        r2 = np.corrcoef(s, w)[0, 1] ** 2
        q = np.quantile(s, [0.1, 0.9])
        print(f"{m}: R^2(winrate~skill)={r2:.3f}, corr(rating,skill)={np.corrcoef(s, R)[0,1]:.3f}, "
              f"winrate bottom10%={100*w[s<=q[0]].mean():.1f}%, top10%={100*w[s>=q[1]].mean():.1f}%, "
              f"middle80% range=({100*np.quantile(w[(s>q[0])&(s<q[1])],0.05):.1f}, {100*np.quantile(w[(s>q[0])&(s<q[1])],0.95):.1f})")


if __name__ == "__main__":
    main()
