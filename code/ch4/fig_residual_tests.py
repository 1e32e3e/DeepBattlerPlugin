"""图：把收敛后的模型当零假设——残差检验能分辨“上头”和“连败保护”。

一名玩家在按分匹配下打天梯，系统用 Elo（K=16）更新评分 R_t。
对手评分 = R_t + m_t + N(0, 50^2)，对手评分等于其真实实力。基础实力 s=0。
- 上头（tilt）：上一局输了，本局实力下降 delta（Elo）。
- 连败保护（一种操纵）：前两局都输了，匹配器把对手评分压低 100（m_t=-100）。
先打 2000 局让评分收敛，取最后 1000 局的平均评分作为冻结模型的实力 Ŝ，
随后 N 局上用冻结模型 p̂_t = F(Ŝ - R_opp) 作零假设，比较四种检验在 5% 双侧水平下的检出率：
 (1) 残差差异检验：触发组与其余对局的标准化残差 (y-p̂) 之差；
 (2) 原始胜率差异检验（不看对手强度）；
 (3) 对手评分差检验：R_opp - R_t 在触发组与其余对局的均值差；
 (4) 条件游程检验：给定 p̂_t 的游程数（只用于上头情形）。
每个场景 2000 次重复。
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
from ch4_model import F  # noqa: E402

CACHE = HERE / "cache" / "residual_tests.npz"
CHECK = np.array([100, 200, 500, 1000, 2000, 5000, 10000])
SCEN = [("tilt", 0.0), ("tilt", 25.0), ("tilt", 50.0), ("tilt", 100.0), ("protect", 100.0)]
NREP = 2000
K, SIGQ, BURN = 16.0, 50.0, 2000


def simulate_raw():
    """逐次重复累计各检验所需的统计量（内存中，不落盘）。"""
    rng = np.random.default_rng(20261018)
    L = len(SCEN) * NREP
    tilt = np.concatenate([np.full(NREP, d if k == "tilt" else 0.0) for k, d in SCEN])
    prot = np.concatenate([np.full(NREP, d if k == "protect" else 0.0) for k, d in SCEN])
    R = np.zeros(L)
    y1 = np.ones(L, dtype=bool)   # 上一局结果（初始化为赢）
    y2 = np.ones(L, dtype=bool)   # 上上局结果
    Racc = np.zeros(L)
    for t in range(BURN):
        m = np.where(~y1 & ~y2, -prot, 0.0)
        opp = R + m + SIGQ * rng.standard_normal(L)
        u = np.where(~y1, -tilt, 0.0)
        y = rng.random(L) < F(u - opp)
        R += K * (y - F(R - opp))
        y2, y1 = y1, y
        if t >= BURN - 1000:
            Racc += R
    S_hat = Racc / 1000

    # 两种分组：g1=上一局输；g2=前两局都输。对每组累计各统计量
    names = ["n", "A", "B", "ys", "gs", "gs2", "As", "Bs"]   # As/Bs：用系统在线预测的残差
    acc = {g: {k: np.zeros((2, L)) for k in names} for g in ("g1", "g2")}
    # 游程检验（冻结 p̂）
    runs = np.ones(L)
    ER = np.ones(L)
    VR = np.zeros(L)
    p_prev = None
    p_prev2 = None
    m_prev = None
    y_prev_eval = None
    out = {f"{g}_{k}": [] for g in ("g1", "g2") for k in names}
    out.update(runs=[], ER=[], VR=[], MR=[], MV=[])
    MR = np.zeros(L)   # 鞅修正游程统计：sum (1-2 y_{t-1}) (y_t - p̂_t)
    MV = np.zeros(L)
    Tmax = CHECK[-1]
    for t in range(Tmax):
        trig2 = ~y1 & ~y2
        m = np.where(trig2, -prot, 0.0)
        opp = R + m + SIGQ * rng.standard_normal(L)
        u = np.where(~y1, -tilt, 0.0)
        y = rng.random(L) < F(u - opp)
        ph = F(S_hat - opp)
        ps = F(R - opp)
        gap = opp - R
        for g, trig in (("g1", ~y1), ("g2", trig2)):
            a = acc[g]
            for idx, sel in ((1, trig), (0, ~trig)):
                w = sel.astype(float)
                a["n"][idx] += w
                a["A"][idx] += w * (y - ph)
                a["B"][idx] += w * ph * (1 - ph)
                a["ys"][idx] += w * y
                a["gs"][idx] += w * gap
                a["gs2"][idx] += w * gap ** 2
                a["As"][idx] += w * (y - ps)
                a["Bs"][idx] += w * ps * (1 - ps)
        MR += (1 - 2 * y1.astype(float)) * (y - ph)
        MV += ph * (1 - ph)
        # 游程：I_t = 1[y_t != y_{t-1}]
        if p_prev is not None:
            runs += (y != y_prev_eval)
            mt = ph * (1 - p_prev) + p_prev * (1 - ph)
            ER += mt
            VR += mt * (1 - mt)
            if m_prev is not None:
                e2 = p_prev2 * (1 - p_prev) * ph + (1 - p_prev2) * p_prev * (1 - ph)
                VR += 2 * (e2 - m_prev * mt)
            m_prev = mt
        p_prev2, p_prev = p_prev, ph
        y_prev_eval = y
        R += K * (y - ps)
        y2, y1 = y1, y
        if (t + 1) in CHECK:
            for g in ("g1", "g2"):
                for k in names:
                    out[f"{g}_{k}"].append(acc[g][k].copy())
            out["runs"].append(runs.copy())
            out["ER"].append(ER.copy())
            out["VR"].append(VR.copy())
            out["MR"].append(MR.copy())
            out["MV"].append(MV.copy())
    res = {k: np.array(v) for k, v in out.items()}
    res["S_hat"] = S_hat
    return res


def zstats(z, g):
    n, A, B = z[f"{g}_n"], z[f"{g}_A"], z[f"{g}_B"]
    ys, gs, gs2 = z[f"{g}_ys"], z[f"{g}_gs"], z[f"{g}_gs2"]
    As, Bs = z[f"{g}_As"], z[f"{g}_Bs"]
    # 形状 (checkpoint, 2组, L)
    th = A / B
    z_res = (th[:, 1] - th[:, 0]) / np.sqrt(1 / B[:, 1] + 1 / B[:, 0])
    ths = As / Bs
    z_sys = (ths[:, 1] - ths[:, 0]) / np.sqrt(1 / Bs[:, 1] + 1 / Bs[:, 0])
    yb = ys / n
    ypool = ys.sum(axis=1) / n.sum(axis=1)
    z_raw = (yb[:, 1] - yb[:, 0]) / np.sqrt(ypool * (1 - ypool) * (1 / n[:, 1] + 1 / n[:, 0]))
    gm = gs / n
    var = (gs2.sum(axis=1) - (gs ** 2 / n).sum(axis=1)) / (n.sum(axis=1) - 2)
    z_gap = (gm[:, 1] - gm[:, 0]) / np.sqrt(var * (1 / n[:, 1] + 1 / n[:, 0]))
    return {"res": z_res, "sys": z_sys, "raw": z_raw, "gap": z_gap}


def power(zz, scen_idx):
    sl = slice(scen_idx * NREP, (scen_idx + 1) * NREP)
    return np.mean(np.abs(zz[:, sl]) > 1.96, axis=1)


def summarize(z):
    """把逐次重复的累计量压缩成检出率与少量汇总量；缓存只存这些（体积很小）。"""
    tests = {f"g1_{k}": v for k, v in zstats(z, "g1").items()}
    tests.update({f"g2_{k}": v for k, v in zstats(z, "g2").items()})
    tests["runs"] = (z["runs"] - z["ER"]) / np.sqrt(z["VR"])   # 视 p_t 为固定的游程检验
    tests["mruns"] = z["MR"] / np.sqrt(z["MV"])                # 鞅修正游程检验
    out = {"pow_" + name: np.array([power(zz, i) for i in range(len(SCEN))]) for name, zz in tests.items()}
    agg = np.zeros((len(SCEN), 2, 2, 3))   # 场景, 分组(g1,g2), (其余,触发), (局数, 胜场, 对手评分差之和)
    for i in range(len(SCEN)):
        sl = slice(i * NREP, (i + 1) * NREP)
        for jg, g in enumerate(("g1", "g2")):
            for k in (0, 1):
                agg[i, jg, k] = [z[f"{g}_n"][-1][k, sl].sum(), z[f"{g}_ys"][-1][k, sl].sum(),
                                 z[f"{g}_gs"][-1][k, sl].sum()]
    out["agg"] = agg
    out["S_hat_mean"] = np.array([z["S_hat"][i * NREP:(i + 1) * NREP].mean() for i in range(len(SCEN))])
    return out


def load():
    if CACHE.exists():
        return dict(np.load(CACHE))
    out = summarize(simulate_raw())
    CACHE.parent.mkdir(exist_ok=True)
    np.savez_compressed(CACHE, **out)
    return out


def main():
    use()
    z = load()

    def P(name, i):
        return z["pow_" + name][i]

    i_tilt50, i_null, i_prot = 2, 0, 4
    fig, axs = plt.subplots(2, 2, figsize=(WIDTH_FULL, 4.5), sharex=True)
    (ax1, ax2), (ax3, ax4) = axs
    specs = [
        ("res", "残差差异（冻结模型）", SERIES[0], "-", "o"),
        ("raw", "原始胜率差异", SERIES[1], "--", "s"),
        ("gap", "对手评分差", SERIES[2], "-.", "^"),
    ]
    for key, lab, col, ls, mk in specs:
        ax1.plot(CHECK, 100 * P("g1_" + key, i_tilt50), color=col, ls=ls, marker=mk, ms=3.5, lw=1.4, label=lab)
        ax2.plot(CHECK, 100 * P("g2_" + key, i_prot), color=col, ls=ls, marker=mk, ms=3.5, lw=1.4, label=lab)
    nulls = [
        ("g1_res", "残差差异（冻结模型）", SERIES[0], "-", "o"),
        ("g1_raw", "原始胜率差异", SERIES[1], "--", "s"),
        ("runs", "游程检验（视 $p_t$ 为固定）", SERIES[3], ":", "D"),
        ("mruns", "游程检验（鞅修正）", SERIES[6], "-", "v"),
    ]
    for name, lab, col, ls, mk in nulls:
        ax3.plot(CHECK, 100 * P(name, i_null), color=col, ls=ls, marker=mk, ms=3.3, lw=1.3, label=lab)
    for jd, (idx, d) in enumerate(((1, 25), (2, 50), (3, 100))):
        ax4.plot(CHECK, 100 * P("g1_res", idx), color=SERIES[0], ls=["--", "-", "-."][jd],
                 marker="o", ms=3.0, lw=1.3, alpha=[0.55, 1.0, 0.8][jd], label=f"上头 $\\delta={d}$")
    titles = ["(a) 上头：输一局后实力 −50", "(b) 连败保护：两连败后对手 −100",
              "(c) 无上头、无操纵时的误报率", "(d) 残差差异检验的检出率"]
    for ax, title in zip(axs.flat, titles):
        ax.axhline(5, color=INK["muted"], lw=0.6)
        ax.set_xscale("log")
        ax.minorticks_off()
        ax.set_xticks([100, 200, 500, 1000, 2000, 5000, 10000])
        ax.set_xticklabels(["100", "200", "500", "1K", "2K", "5K", "10K"])
        ax.set_ylim(0, 103)
        ax.set_title(title, loc="left")
    ax1.legend(loc="upper left", fontsize=6.8)
    ax2.legend(loc="center right", fontsize=6.8)
    ax3.legend(loc="upper left", fontsize=6.8)
    ax4.legend(loc="lower right", fontsize=6.8)
    for ax in (ax3, ax4):
        ax.set_xlabel("用于检验的局数 $N$")
    for ax in (ax1, ax3):
        ax.set_ylabel("5% 水平下的检出率（%）")
    fig.tight_layout(h_pad=1.0, w_pad=1.0)
    save(fig, "ch4", "fig_residual_tests")

    # 给正文的数字（g1：上一局输为触发；g2：前两局都输为触发；sys：用系统在线预测的残差）
    print("S_hat mean by scenario:", np.round(z["S_hat_mean"], 1))
    names = sorted(k[4:] for k in z if k.startswith("pow_"))
    for i, (k, d) in enumerate(SCEN):
        print(f"--- {k} {d}")
        for name in names:
            print(f"  {name:9s}: " + " ".join(f"{n}:{100*v:.1f}" for n, v in zip(CHECK, P(name, i))))
        for jg, g in enumerate(("g1", "g2")):
            a = z["agg"][i, jg]
            print(f"  {g}: winrate trig={100*a[1,1]/a[1,0]:.2f}% other={100*a[0,1]/a[0,0]:.2f}%; "
                  f"gap trig={a[1,2]/a[1,0]:.1f} other={a[0,2]/a[0,0]:.1f}")

if __name__ == "__main__":
    main()
