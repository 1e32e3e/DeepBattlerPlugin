"""图 2.9：8 人自由混战（如酒馆战棋）中，实力优势如何换成名次。

Plackett–Luce（表现 = 实力 + Gumbel 噪声，任意两人的相对名次概率恰为 Elo 的 F）：
焦点玩家对其余 7 名同水平对手的优势为 d，w = 10^(d/400)，P(第 1) = w/(w+7)，
P(前 k) = 1 - Π_{j<k} (7-j)/(w+7-j)。
(a) P(第 1)、P(前 4) 与 1v1 胜率 F(d)：曲线为公式，点为 Gumbel 表现的蒙特卡洛（每点 20 万局）；
(b) d = 0/+100/+200/+400 时的名次分布。
运行：python code/ch2/fig_ffa.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import numpy as np

import model as m
from figstyle import INK, LINESTYLES, SERIES, WIDTH_FULL, save, use

N = 8


def mc_place(d, n_games=200_000, seed=0):
    rng = np.random.default_rng(seed)
    g = -np.log(-np.log(rng.random((n_games, N))))
    perf = m.GUMBEL_SCALE * g
    perf[:, 0] += d
    return 1 + (perf[:, 1:] > perf[:, :1]).sum(1)


def main():
    use()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9), gridspec_kw=dict(wspace=0.3))
    d = np.linspace(-400, 400, 401)
    w = 10 ** (d / 400)
    ax.plot(d, m.F(d) * 100, color=SERIES[0], ls=LINESTYLES[0], label="1v1 胜率 $F(d)$")
    ax.plot(d, m.pl_top_k(w, N, 4) * 100, color=SERIES[1], ls=LINESTYLES[1], label="8 人局进前 4")
    ax.plot(d, m.pl_top_k(w, N, 1) * 100, color=SERIES[2], ls=LINESTYLES[2], label="8 人局第 1 名")
    dd = np.arange(-300, 301, 100)
    mc = [mc_place(x, seed=i) for i, x in enumerate(dd)]
    ax.plot(dd, [np.mean(p <= 4) * 100 for p in mc], "o", ms=3.5, color=SERIES[1], mec="white", mew=0.5)
    ax.plot(dd, [np.mean(p == 1) * 100 for p in mc], "o", ms=3.5, color=SERIES[2], mec="white", mew=0.5)
    ax.axhline(50, color=INK["muted"], lw=0.8, ls=":")
    ax.axhline(12.5, color=INK["muted"], lw=0.8, ls=":")
    ax.text(-395, 13.5, "1/8", fontsize=7.5, color=INK["secondary"])
    ax.set_xlabel("对其余 7 人的实力优势 $d$（Elo）")
    ax.set_ylabel("概率（%）")
    ax.set_xlim(-400, 400); ax.set_ylim(0, 100)
    ax.legend(loc="upper left", fontsize=7.5)
    ax.set_title("(a) 名次概率（Plackett–Luce）", loc="left", fontsize=9)

    places = np.arange(1, N + 1)
    width = 0.2
    for i, dv in enumerate((0, 100, 200, 400)):
        pdist = m.pl_place_dist(10 ** (dv / 400), N)
        mean = float((pdist * places).sum())
        bx.bar(places + (i - 1.5) * width, pdist * 100, width=width * 0.88, color=SERIES[i],
               label=f"$d$={dv:+d}（平均名次 {mean:.2f}）" if dv else f"$d$=0（平均名次 {mean:.2f}）")
    bx.set_xticks(places)
    bx.set_xlabel("名次")
    bx.set_ylabel("概率（%）")
    bx.set_ylim(0, 62)
    bx.grid(axis="x", visible=False)
    bx.legend(loc="upper right", fontsize=7.5)
    bx.set_title("(b) 名次分布", loc="left", fontsize=9)
    save(fig, "ch2", "ffa")

    print("d | w | 1v1 | P1 | top4 | mean place")
    for dv in (-200, 0, 100, 200, 400):
        wv = 10 ** (dv / 400)
        pdist = m.pl_place_dist(wv, N)
        print(dv, round(wv, 2), round(float(m.F(dv)), 3), round(float(m.pl_top_k(wv, N, 1)), 3),
              round(float(m.pl_top_k(wv, N, 4)), 3), round(float((pdist * places).sum()), 2))
    print("MC check d=+200:", np.mean(mc_place(200, seed=99) == 1), "formula", float(m.pl_top_k(10 ** 0.5, N, 1)))
    for name in ("f_r_k16", "f_s100_k16"):
        r = m.get(name)
        d1, d10 = (m.by_decile(r["s"], r[k]) for k in ("W",)) , None
        dW = m.by_decile(r["s"], r["W"]); dT = m.by_decile(r["s"], r["top"]); dP = m.by_decile(r["s"], r["place"])
        top1 = r["s"] >= np.quantile(r["s"], 0.99)
        print(f"{name}: top10% P1 {dW[9]:.3f} top4 {dT[9]:.3f} place {dP[9]:.2f}; bottom10% P1 {dW[0]:.3f} top4 {dT[0]:.3f} "
              f"place {dP[0]:.2f}; top1% P1 {r['W'][top1].mean():.3f}; resid {m.fit_line(r['s'], r['R_end'])[2]:.1f}; "
              f"mean P1 {r['W'].mean():.3f} top4 {r['top'].mean():.3f} place {r['place'].mean():.2f}")
    print("FFA sigma_e theory:", float(m.sigma_e(16)) * np.sqrt((N + 1) / (3 * (N - 1))))


if __name__ == "__main__":
    main()
