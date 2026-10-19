"""图：只和“上一代自己”比，自博弈 Elo 会通胀；进步要对固定参照池来量。

玩具博弈：P(i 胜 j) = σ(A·sin(θ_i-θ_j) + B·(h_i-h_j))，θ 为循环（石头剪刀布式）维度，h 为传递实力。
每一代 θ 增加 Δθ=0.35（恰好克制上一代），A=1.5；
  博弈 1（纯循环）：h 不变；
  博弈 2（循环 + 少量传递）：B=1，每代 h 增加 0.05。
自博弈 Elo：每代与上一代打 400 局，用实测胜率的 logit 换算 Elo 增量后累加（固定随机种子）。
固定参照池：16 个在循环维度上均匀分布、h=0 的冻结智能体；曲线为对该池的精确平均胜率。
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
from ch4_model import C  # noqa: E402

A, DTH, GENS, NGAMES = 1.5, 0.35, 60, 400
GAMES = [("纯循环", 0.0), ("循环 + 少量传递", 0.05)]


def sig(x):
    return 1 / (1 + np.exp(-x))


def main():
    use()
    rng = np.random.default_rng(42)
    k = np.arange(GENS + 1)
    pool = 2 * np.pi * np.arange(16) / 16
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(WIDTH_FULL, 3.5))
    for i, (name, dh) in enumerate(GAMES):
        logit_step = A * np.sin(DTH) + dh            # 新一代对上一代的 logit 优势（B=1）
        p_step = sig(logit_step)
        w = rng.binomial(NGAMES, p_step, GENS) / NGAMES
        w = np.clip(w, 0.5 / NGAMES, 1 - 0.5 / NGAMES)
        self_elo = np.concatenate([[0], np.cumsum(np.log(w / (1 - w)) / C)])
        th, h = k * DTH, k * dh
        vs_pool = np.array([sig(A * np.sin(t - pool) + hh).mean() for t, hh in zip(th, h)])
        col = SERIES[i]
        ax1.plot(k, self_elo, color=col, lw=1.6, ls=["-", "--"][i], label=f"{name}：自博弈累计 Elo")
        ax2.plot(k, 100 * vs_pool, color=col, lw=1.6, ls=["-", "--"][i], label=f"{name}：对固定参照池")
        if dh > 0:
            ax1.plot(k, h / C, color=col, lw=1.0, ls=":", label=f"{name}：真实传递进步")
        print(f"{name}: 对上一代胜率 {p_step:.3f}，每代自博弈 Elo {logit_step/C:.1f}，"
              f"{GENS} 代累计 {self_elo[-1]:.0f}（这一次实现；期望值 {GENS * logit_step / C:.0f}，"
              f"400 局估计噪声使 {GENS} 代累计的标准差约 "
              f"{np.sqrt(GENS / (NGAMES * p_step * (1 - p_step))) / C:.0f}）；真实传递进步 {h[-1]/C:.0f} Elo；"
              f"对参照池胜率 第0代 {100*vs_pool[0]:.1f}% -> 第{GENS}代 {100*vs_pool[-1]:.1f}%")
        if i == 0:
            vs_g0 = sig(A * np.sin(th))
            ax2.plot(k, 100 * vs_g0, color=SERIES[2], lw=1.1, ls="-.", label="纯循环：只对第 0 代")
    ax1.set_xlabel("代数")
    ax1.set_ylabel("Elo")
    ax1.set_title("(a) 只与上一代比较", loc="left")
    ax1.legend(loc="upper center", fontsize=7, bbox_to_anchor=(0.5, -0.2), frameon=False)
    ax2.axhline(50, color=INK["muted"], lw=0.6)
    ax2.set_ylim(0, 100)
    ax2.set_xlabel("代数")
    ax2.set_ylabel("胜率（%）")
    ax2.set_title("(b) 对固定参照的胜率", loc="left")
    ax2.legend(loc="upper center", fontsize=7, bbox_to_anchor=(0.5, -0.2), frameon=False)
    fig.tight_layout()
    save(fig, "ch4", "fig_selfplay_inflation")


if __name__ == "__main__":
    main()
