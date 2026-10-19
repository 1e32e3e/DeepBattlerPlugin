"""图 2.8：团队游戏中个人实力优势被稀释（随机队友、随机对手）。

焦点玩家比群体平均高 d 分，n-1 名队友和 n 名对手都从 N(μ, τ²) 随机抽取。
(a) 加和模型 P = F((Σs_A - Σs_B)/√n)：W(d) = E[F(X)]，X ~ N(d/√n, (2n-1)τ²/n)；
(b) 均值模型 P = F(s̄_A - s̄_B)：X ~ N(d/n, (2n-1)τ²/n²)。
曲线为精确数值积分；点为模拟（n=1：1v1 随机匹配；n=5：5v5 随机分队），按实力分组的平均胜率。
参数：τ=200，10,000 人，K=16，3000 轮，统计第 1001–3000 局。
运行：python code/ch2/fig_team.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import numpy as np

import model as m
from figstyle import INK, LINESTYLES, SERIES, WIDTH_FULL, save, use


def W_team(d, n, model="sum", tau=m.TAU):
    d = np.asarray(d, dtype=float)
    if model == "sum":
        return m.gauss_expect(m.F, d / math.sqrt(n), tau * math.sqrt((2 * n - 1) / n))
    return m.gauss_expect(m.F, d / n, tau * math.sqrt(2 * n - 1) / n)


def W_team_probit(d, n, model="sum", tau=m.TAU):
    if model == "sum":
        return m.Phi((d / math.sqrt(n)) / math.sqrt(m.SIGMA_D ** 2 + (2 * n - 1) * tau ** 2 / n))
    return m.Phi((d / n) / math.sqrt(m.SIGMA_D ** 2 + (2 * n - 1) * tau ** 2 / n ** 2))


def binned(name, edges):
    r = m.get(name)
    d = r["s"] - m.MU
    b = np.digitize(d, edges) - 1
    ok = [k for k in range(len(edges) - 1) if (b == k).sum() >= 30]
    return (np.array([d[b == k].mean() for k in ok]), np.array([r["W"][b == k].mean() for k in ok]))


def main():
    use()
    d = np.linspace(-500, 500, 401)
    edges = np.arange(-550, 551, 50)
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9), sharey=True, gridspec_kw=dict(wspace=0.08))
    for ax, model, title in ((axes[0], "sum", "(a) 加和模型：稀释约 $1/\\sqrt{n}$"),
                             (axes[1], "mean", "(b) 均值模型：稀释约 $1/n$")):
        for i, n in enumerate((1, 3, 5)):
            ax.plot(d, W_team(d, n, model) * 100, color=SERIES[i], ls=LINESTYLES[i], label=f"每队 $n$={n}")
        x, y = binned("r_k16", edges)
        ax.plot(x, y * 100, "o", ms=3.2, color=SERIES[0], mec="white", mew=0.5)
        x, y = binned("t_r_sum_k16" if model == "sum" else "t_r_mean_k16", edges)
        ax.plot(x, y * 100, "o", ms=3.2, color=SERIES[2], mec="white", mew=0.5)
        ax.axhline(50, color=INK["muted"], lw=0.8, ls=":")
        ax.axvline(0, color=INK["muted"], lw=0.8, ls=":")
        ax.set_xlabel("个人实力优势 $d=s-\\mu$（Elo）")
        ax.set_xlim(-500, 500); ax.set_ylim(0, 100)
        ax.set_title(title, loc="left", fontsize=9)
        ax.legend(loc="upper left", fontsize=7.5)
    axes[0].set_ylabel("长期胜率（%）")
    save(fig, "ch2", "team")

    # 正文数值
    z = m.PhiInv(np.linspace(0.9, 0.99999, 4001))
    print("n | top10 sum | top10 mean | slope/100 sum | slope/100 mean | slope/100 sum, equal teammates")
    for n in (1, 2, 3, 5, 6, 8):
        t_sum = float(np.mean(W_team(200 * z, n, "sum")))
        t_mean = float(np.mean(W_team(200 * z, n, "mean")))
        h = 1.0
        sl_sum = float((W_team(h, n, "sum") - W_team(-h, n, "sum")) / (2 * h)) * 100 * 100
        sl_mean = float((W_team(h, n, "mean") - W_team(-h, n, "mean")) / (2 * h)) * 100 * 100
        sl_eq = m.SLOPE0 / math.sqrt(n) * 100 * 100
        print(f"{n} | {t_sum:.3f} | {t_mean:.3f} | {sl_sum:.1f} | {sl_mean:.1f} | {sl_eq:.1f}")
    s1 = float((W_team(1, 1) - W_team(-1, 1)) / 2)
    print("slope ratio n=5: sum", float((W_team(1, 5) - W_team(-1, 5)) / 2) / s1,
          "mean", float((W_team(1, 5, 'mean') - W_team(-1, 5, 'mean')) / 2) / s1, "1/sqrt5", 1 / math.sqrt(5))
    for name in ("t_r_sum_k16", "t_r_mean_k16", "t_s100_sum_k16", "t_s200_sum_k16", "t_s100_mean_k16"):
        r = m.get(name)
        dec = m.by_decile(r["s"], r["W"])
        lam, a, rs = m.fit_line(r["s"], r["R_end"])
        print(f"{name}: deciles {dec[0]*100:.1f}–{dec[9]*100:.1f}%, top1% {r['W'][r['s'] >= np.quantile(r['s'], .99)].mean()*100:.1f}%, "
              f"sd(W) {r['W'].std()*100:.2f}pp, lambda {lam:.2f}, resid {rs:.1f}, lam_t(1k,2k,3k) {np.round(r['lam_t'][[9,19,29]],2)}")
    # 团队评分误差的粗略公式：K√n/(2c(1-√n Kc/4))
    for n, K in ((5, 16), (5, 32)):
        print("team sigma_e theory (sum)", n, K, math.sqrt(K * math.sqrt(n) / (2 * m.C * (1 - math.sqrt(n) * K * m.C / 4))))


if __name__ == "__main__":
    main()
