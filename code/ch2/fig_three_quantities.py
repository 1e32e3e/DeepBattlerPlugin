"""图 2.1：同一实力在不同环境下的长期胜率不同；评分只是实力带噪声、带刻度的估计。

(a) 实力固定为 s = 1756（τ=200 群体的第 90 百分位）的玩家，在不同对手池/匹配规则下的长期胜率。
(b) 按分匹配（σ_q=100，K=16）稳态下，评分 R 对真实实力 s 的散点。
参数：10,000 人，s ~ N(1500, τ²)，K=16，3000 轮，统计第 1001–3000 局（见 model.EXPERIMENTS）。
运行：python code/ch2/fig_three_quantities.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import numpy as np

import model as m
from figstyle import INK, SERIES, WIDTH_FULL, save, use

S_FOCUS = m.MU + 1.2816 * m.TAU      # τ=200 群体的第 90 百分位
BAND = 15.0


def focus_winrate(name):
    r = m.get(name)
    sel = np.abs(r["s"] - S_FOCUS) < BAND
    return float(r["W"][sel].mean()), int(sel.sum())


def main():
    use()
    rows = [
        ("随机匹配，群体 τ=100", "r_k16_tau100", 0),
        ("随机匹配，群体 τ=200", "r_k16", 0),
        ("随机匹配，群体 τ=300", "r_k16_tau300", 0),
        ("随机匹配，τ=200，单局噪声 150", "r_k16_noise150", 0),
        ("按分匹配，σ_q=200", "s200_k16", 1),
        ("按分匹配，σ_q=100", "s100_k16", 1),
        ("按分匹配，σ_q=50", "s50_k16", 1),
        ("按分匹配，σ_q=20", "s20_k16", 1),
    ]
    vals = [focus_winrate(n) for _, n, _ in rows]

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(WIDTH_FULL, 3.1),
                                 gridspec_kw=dict(width_ratios=[1.25, 1.0], wspace=0.55))
    y = np.arange(len(rows))[::-1]
    for yi, (lab, _, grp), (w, n) in zip(y, rows, vals):
        ax.barh(yi, w * 100, height=0.55, color=SERIES[grp], edgecolor="none")
        ax.text(w * 100 + 1.2, yi, f"{w * 100:.1f}%", va="center", fontsize=7.5, color=INK["primary"])
    ax.set_yticks(y)
    ax.set_yticklabels([r[0].replace("σ_q", "$\\sigma_q$").replace("τ", "$\\tau$") for r in rows], fontsize=7.5)
    ax.axvline(50, color=INK["muted"], lw=0.8, ls=":")
    ax.set_xlim(0, 105)
    ax.set_xlabel("长期胜率（%）")
    ax.grid(axis="y", visible=False)
    ax.set_title("(a) 同一实力 $s=1756$，不同环境", loc="left", fontsize=9)
    ax.tick_params(axis="y", length=0)
    # 图例：两组颜色
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=SERIES[0], label="随机匹配"), Patch(color=SERIES[1], label="按分匹配")],
              loc="lower right", fontsize=7.5, handlelength=1.0)

    r = m.get("s100_k16")
    rng = np.random.default_rng(0)
    idx = rng.choice(r["s"].size, 2500, replace=False)
    s, R = r["s"][idx], r["R_end"][idx]
    lam, a, rs = m.fit_line(r["s"], r["R_end"])
    bx.scatter(s, R, s=2.5, color=SERIES[0], alpha=0.35, lw=0, rasterized=True)
    xx = np.array([900, 2100])
    bx.plot(xx, a + lam * xx, color=SERIES[1], lw=1.6, label=f"回归线：斜率 $\\lambda$={lam:.2f}")
    bx.plot(xx, xx, color=INK["secondary"], lw=1.0, ls="--", label="$R=s$")
    corr = float(np.corrcoef(r["s"], r["R_end"])[0, 1])
    bx.text(0.04, 0.96, f"相关系数 {corr:.3f}\n残差标准差 {rs:.0f} 分", transform=bx.transAxes,
            va="top", fontsize=7.5, color=INK["primary"])
    bx.set_xlim(900, 2100); bx.set_ylim(700, 2300)
    bx.set_xlabel("真实实力 $s$（Elo）")
    bx.set_ylabel("评分 $R$（Elo）")
    bx.legend(loc="lower right", fontsize=7.5)
    bx.set_title("(b) 按分匹配稳态下的评分", loc="left", fontsize=9)
    save(fig, "ch2", "three_quantities")
    for (lab, n, _), (w, k) in zip(rows, vals):
        print(f"{lab:30s} W={w:.3f} (n={k})")
    print("lambda", lam, "resid", rs, "corr", corr)


if __name__ == "__main__":
    main()
