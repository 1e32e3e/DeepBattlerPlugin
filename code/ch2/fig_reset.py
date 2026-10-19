"""图 2.6：强玩家评分被重置为 1500 后的追分过程（"新号/回流"实验）。

系统平稳（1000 轮）后，从实力前 10% 中随机取 500 人，把评分设为 1500，跟踪其后 400 局。
(a) 差距（实力分）= s - (R - a_t)/λ_t，(a_t, λ_t) 每轮在未重置玩家上重新拟合；
(b) 这批玩家的逐局胜率（10 局滑动平均）。
参数：10,000 人，τ=200，按分匹配 σ_q=100 或随机匹配，K=16/32。
运行：python code/ch2/fig_reset.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import numpy as np

import model as m
from figstyle import INK, SERIES, WIDTH_FULL, save, use


def rolling(x, w=10):
    return np.convolve(x, np.ones(w) / w, mode="valid")


def main():
    use()
    runs = m.reset_runs()
    cases = [(("sbmm", 16), "按分 $\\sigma_q$=100，$K$=16", "-"), (("sbmm", 32), "按分 $\\sigma_q$=100，$K$=32", "--"),
             (("random", 16), "随机匹配，$K$=16", "-.")]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(WIDTH_FULL, 2.9), gridspec_kw=dict(wspace=0.3))
    for i, (key, lab, ls) in enumerate(cases):
        r = runs[key]
        g = r["gap"]
        t = np.arange(g.size)
        h, n90 = m.closure_time(g, 0.5), m.closure_time(g, 0.9)
        ax.plot(t, g, color=SERIES[i], ls=ls, label=f"{lab}（{h} / {n90} 局）")
        w = rolling(r["win"]) * 100
        bx.plot(np.arange(w.size) + 10, w, color=SERIES[i], ls=ls, lw=1.3, label=lab)
    ax.axhline(0, color=INK["muted"], lw=0.8)
    ax.set_xlabel("重置后的局数")
    ax.set_ylabel("评分落后于实力（实力分）")
    ax.set_xlim(0, 400); ax.set_ylim(-20, 370)
    ax.legend(loc="upper right", fontsize=6.4, title="括号内：追回 50% / 90% 差距的局数", title_fontsize=6.4)
    ax.set_title("(a) 评分追回实力", loc="left", fontsize=9)
    stat = m.get("s100_k16")
    top = stat["W"][stat["s"] >= np.quantile(stat["s"], 0.9)].mean() * 100
    bx.axhline(top, color=INK["secondary"], lw=0.8, ls=":")
    bx.text(398, top - 1.5, f"平稳时前 10% 的胜率 {top:.0f}%（$K$=16）", ha="right", va="top", fontsize=6.5,
            color=INK["primary"])
    bx.axhline(50, color=INK["muted"], lw=0.8, ls=":")
    bx.set_xlabel("重置后的局数")
    bx.set_ylabel("胜率（%，10 局滑动平均）")
    bx.set_xlim(0, 400); bx.set_ylim(40, 100)
    bx.legend(loc="upper right", fontsize=6.4)
    bx.set_title("(b) 这批玩家的胜率", loc="left", fontsize=9)
    save(fig, "ch2", "reset")
    for key, r in runs.items():
        g, gf, w = r["gap"], r["gap_frozen"], r["win"]
        print(key, f"gap0={g[0]:.0f} half={m.closure_time(g, .5)} 90%={m.closure_time(g, .9)} "
              f"(frozen target: {m.closure_time(gf, .5)}/{m.closure_time(gf, .9)}) "
              f"W1-50={w[:50].mean():.3f} W1-100={w[:100].mean():.3f} W301-400={w[300:400].mean():.3f}")


if __name__ == "__main__":
    main()
