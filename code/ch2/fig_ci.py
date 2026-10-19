"""图 2.12：胜率的统计不确定性与所需局数。

(a) 真实胜率 50% 时，n 局观测胜率的 95% 区间半宽：二项分布（各局独立）；
    以及按分匹配（实力固定，σ_q=100，K=16）、随机匹配 + AR(1) 状态（σ_u=100，φ=0.99）下按附录公式修正后的半宽。
(b) 双侧 α=0.05、功效 80% 时，把真实水平与"五五开"区分开所需的局数：
    1v1 胜率或 8 人局前四率（对 50%）、8 人局第一名率（对 12.5%）、8 人局平均名次（对 4.5，Plackett–Luce）。
    横轴统一用"前四率/胜率"表示实力优势，8 人局的另外两个指标按 Plackett–Luce 换算。
运行：python code/ch2/fig_ci.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize, stats

import model as m
from figstyle import INK, LINESTYLES, SERIES, WIDTH_FULL, save, use

ZA, ZB = stats.norm.ppf(0.975), stats.norm.ppf(0.80)
N8 = 8
PLACES = np.arange(1, N8 + 1)


def wilson(phat, n, z=ZA):
    c = phat + z * z / (2 * n)
    h = z * np.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n))
    return (c - h) / (1 + z * z / n), (c + h) / (1 + z * z / n)


def n_binom(p0, p1):
    return ((ZA * np.sqrt(p0 * (1 - p0)) + ZB * np.sqrt(p1 * (1 - p1))) / (p1 - p0)) ** 2


def pl_from_top4(x):
    """给定前四率 x，求 Plackett–Luce 下的 w 与名次分布。"""
    d = optimize.brentq(lambda d: float(m.pl_top_k(10 ** (d / 400), N8, 4)) - x, -400, 800)
    w = 10 ** (d / 400)
    return w, m.pl_place_dist(w, N8)


def main():
    use()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9), gridspec_kw=dict(wspace=0.3))
    n = np.geomspace(10, 10000, 200)
    base = ZA * np.sqrt(0.25 / n) * 100
    ax.plot(n, base, color=SERIES[0], label="二项分布（各局独立）")
    big = 1e9   # 单个 n 局窗口相对长期均值的无条件方差（不做窗口样本方差修正）
    ax.plot(n, base * np.sqrt(m.var_ratio_sbmm(n, 16, 100, T=big)), color=SERIES[1], ls="--",
            label="按分匹配、实力固定")
    ax.plot(n, base * np.sqrt(m.var_ratio_random_ar(n, 100.0, T=big)), color=SERIES[2], ls="-.",
            label="随机匹配 + 状态起伏")
    for nn in (20, 100, 500):
        hw = ZA * np.sqrt(0.25 / nn) * 100
        ax.plot(nn, hw, "o", ms=4, color=SERIES[0], mec="white", mew=0.6)
    ax.set_xscale("log")
    ax.set_xlabel("局数 $n$")
    ax.set_ylabel("95% 区间半宽（百分点）")
    ax.set_ylim(0, 35)
    ax.legend(loc="upper right", fontsize=6.6)
    ax.set_title("(a) 观测胜率的误差范围", loc="left", fontsize=9)

    x = np.linspace(0.505, 0.60, 60)
    n_top4 = n_binom(0.5, x)
    n_first, n_place = [], []
    sd0 = np.sqrt((N8 ** 2 - 1) / 12)
    for xi in x:
        w, pdist = pl_from_top4(xi)
        p1 = float(m.pl_top_k(w, N8, 1))
        n_first.append(n_binom(0.125, p1))
        mu = float((pdist * PLACES).sum())
        sd1 = float(np.sqrt((pdist * PLACES ** 2).sum() - mu ** 2))
        n_place.append(((ZA * sd0 + ZB * sd1) / (4.5 - mu)) ** 2)
    # 52% 处的精确值（不用网格插值），写进图例
    w52, pd52 = pl_from_top4(0.52)
    mu52 = float((pd52 * PLACES).sum())
    sd52 = float(np.sqrt((pd52 * PLACES ** 2).sum() - mu52 ** 2))
    exact = (n_binom(0.5, 0.52), ((ZA * sd0 + ZB * sd52) / (4.5 - mu52)) ** 2,
             n_binom(0.125, float(m.pl_top_k(w52, N8, 1))))
    bx.plot(x * 100, n_first, color=SERIES[2], ls="-.", label=f"8 人局第一名率，对 12.5%（{exact[2]:,.0f}）")
    bx.plot(x * 100, n_top4, color=SERIES[0], label=f"1v1 胜率或 8 人局前四率，对 50%（{exact[0]:,.0f}）")
    bx.plot(x * 100, n_place, color=SERIES[1], ls="--", label=f"8 人局平均名次，对 4.5（{exact[1]:,.0f}）")
    for v, col in zip(exact, (SERIES[0], SERIES[1], SERIES[2])):
        bx.plot(52, v, "o", ms=4, color=col, mec="white", mew=0.6)
    bx.axvline(52, color=INK["muted"], lw=0.8, ls=":")
    bx.set_yscale("log")
    bx.set_xlabel("真实胜率 / 前四率（%）")
    bx.set_ylabel("所需局数（80% 功效）")
    bx.set_xlim(50.5, 60)
    bx.set_ylim(100, 4e6)
    bx.legend(loc="upper right", fontsize=6.0, title="括号内：真实值 52% 时所需局数", title_fontsize=6.0)
    bx.set_title("(b) 区分“五五开”所需局数", loc="left", fontsize=9)
    save(fig, "ch2", "ci")

    # 正文数值
    for nn in (20, 50, 100, 200, 500, 1000, 2000, 5000):
        lo, hi = wilson(0.52, nn)
        print(f"n={nn}: SE={100*np.sqrt(.25/nn):.2f}pp, Wald ±{100*ZA*np.sqrt(.25/nn):.1f}pp, Wilson(52%)={100*lo:.1f}–{100*hi:.1f}%")
    print("n for 52 vs 50: two-sided 80%", n_binom(.5, .52), "one-sided", ((stats.norm.ppf(.95)*.5+ZB*np.sqrt(.52*.48))/.02)**2,
          "90% power", ((ZA*.5+stats.norm.ppf(.9)*np.sqrt(.52*.48))/.02)**2)
    print("min n with observed 52% excluding 50% (Wilson):", next(k for k in range(100, 5000) if wilson(0.52, k)[0] > 0.5))
    print("tails: P(X>=60|100)", stats.binom.sf(59, 100, .5), "P(X>=14|20)", stats.binom.sf(13, 20, .5),
          "P(X>=15|20)", stats.binom.sf(14, 20, .5), "P(X>=275|500)", stats.binom.sf(274, 500, .5))
    w, pdist = pl_from_top4(0.52)
    mu = float((pdist * PLACES).sum())
    print("PL top4=52%: d", 400*np.log10(w), "P1", float(m.pl_top_k(w, N8, 1)), "mean place", mu,
          "n_top4/n_place/n_first (exact)", exact)
    print("n to detect mean-placement shift 0.10 (sd 2.29):", ((ZA * sd0 + ZB * sd0) / 0.10) ** 2)
    for nn in (20, 100, 500):
        print("effective half-width", nn, "sbmm", base[np.argmin(abs(n-nn))]*np.sqrt(m.var_ratio_sbmm(nn,16,100,T=big)),
              "random+AR", ZA*np.sqrt(.25/nn)*100*np.sqrt(m.var_ratio_random_ar(nn,100.0,T=big)))


if __name__ == "__main__":
    main()
