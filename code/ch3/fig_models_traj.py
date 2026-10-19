"""图：四种实力波动模型的示例轨迹（单人、校准对手池、Elo K=20）：实力偏离 u_t、评分 R_t 与胜负。"""
import numpy as np
import matplotlib.pyplot as plt

from _common import FONT_SCALE, CH, INK, SERIES, WIDTH_FULL, save, use
from experiments import STANDARD, run_examples

ROWS = [("ar1", "(b) AR(1) 状态：ρ=0.9，SD=60"),
        ("hmm", "(c) 两状态：状态差时 −120，平均持续 10 局"),
        ("tilt", "(d) 上头：每连败一局 −30，上限 −90"),
        ("fatigue", "(e) 疲劳：每多打一局 −6，休息后恢复")]


def main():
    use()
    d = run_examples()
    fig, axes = plt.subplots(len(ROWS), 1, figsize=(5.2, 4.9), sharex=True)
    for ax, (nm, title) in zip(axes, ROWS):
        u = d[f"{nm}_u"]
        R = d[f"{nm}_R"]
        y = d[f"{nm}_y"].astype(bool)
        t = np.arange(u.size)
        ax.step(t, u, where="post", color=SERIES[0], lw=1.3, label="有效实力偏离 $u_t$")
        ax.plot(t, R, color=SERIES[1], lw=1.3, label="评分 $R_t$（相对平均实力）")
        top = 175
        ax.vlines(t[y], top, top + 22, color=INK["secondary"], lw=0.9)
        ax.vlines(t[~y], top - 22, top, color=INK["muted"], lw=0.9)
        ax.axhline(top, color=INK["axis"], lw=0.5)
        if nm == "fatigue":
            br = t[1:][d[f"{nm}_j"][1:] == 1]
            for b in br:
                ax.axvline(b - 0.5, color=INK["grid"], lw=0.8, zorder=0)
        ax.axhline(0, color=INK["muted"], lw=0.6)
        ax.set_ylim(-190, 205)
        ax.set_yticks([-150, -75, 0, 75, 150])
        ax.set_title(title, loc="left", fontsize=9 * FONT_SCALE)
        ax.set_ylabel("Elo")
    axes[-1].set_xlabel("局序号 $t$（竖线：一次游玩结束）")
    h, l = axes[0].get_legend_handles_labels()
    from matplotlib.lines import Line2D
    h.append(Line2D([], [], color=INK["secondary"], lw=0, marker="|", ms=8, mew=1.0))
    l.append("顶部短线：胜（向上）/ 负（向下）")
    fig.tight_layout(h_pad=0.6)
    fig.legend(h, l, loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False, fontsize=8 * FONT_SCALE)
    save(fig, CH, "models_traj")


if __name__ == "__main__":
    main()
