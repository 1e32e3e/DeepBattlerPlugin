"""图：AlphaStar 优先虚拟自博弈（PFSP）的对手权重函数与 Fisher 信息。

f_hard(x) = (1-x)^p（p = 0.5, 1, 2），f_var(x) = x(1-x)（画成 4x(1-x) 以便与最大值 1 比较），
x 为学习者对该对手的胜率。单局 Fisher 信息 c^2 x(1-x) 归一化后与 f_var 完全重合。
阴影：OpenAI Five 评估时只与胜率在 15%–85% 之间的参考对手对局。解析式，无随机性。
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from figstyle import use, save, SERIES, INK  # noqa: E402


def main():
    use()
    x = np.linspace(0, 1, 401)
    fig, ax = plt.subplots(figsize=(6.2, 2.55))
    ax.axvspan(0.15, 0.85, color=SERIES[0], alpha=0.07, lw=0)
    ax.text(0.5, 1.07, "OpenAI Five 评估只用胜率 15%–85% 的参考对手", ha="center", fontsize=7.2,
            color=INK["secondary"])
    ax.plot(x, 4 * x * (1 - x), color=SERIES[0], lw=1.8,
            label=r"$f_{\mathrm{var}}\propto x(1-x)$ $\equiv$ 单局 Fisher 信息")
    for i, (pp, ls) in enumerate(((0.5, "--"), (1.0, "-."), (2.0, ":"))):
        ax.plot(x, (1 - x) ** pp, color=SERIES[1 + i], lw=1.4, ls=ls,
                label=rf"$f_{{\mathrm{{hard}}}}=(1-x)^{{{pp:g}}}$")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.16)
    ax.set_xticks([0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0])
    ax.set_xticklabels(["0", "20%", "40%", "50%", "60%", "80%", "100%"])
    ax.set_xlabel("学习者对该对手的胜率 $x$")
    ax.set_ylabel("相对抽样权重")
    ax.legend(loc="center left", fontsize=7.2, bbox_to_anchor=(1.01, 0.5))
    fig.tight_layout()
    save(fig, "ch4", "fig_pfsp")


if __name__ == "__main__":
    main()
