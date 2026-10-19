"""第四章正文与附录中解析数字的独立复算（不出图）。运行：python code/ch4/derivations_check.py

逐条打印：Elo=SGD 的数值梯度核对、恒定 K 的稳态误差、最优 K、TrueSkill 稳态等效 K、
Fisher 信息、分辨小差距所需局数、AlphaGo Zero 评估门槛的误选概率、Plackett–Luce 信息量、
酒馆战棋样本量。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from scipy import stats, optimize

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch4_model import C, F, binary_entropy, rmse_theory, pl_fisher_equal, pl_grad, pl_sample  # noqa: E402


def line(msg):
    print(msg)


def main():
    rng = np.random.default_rng(4)
    line(f"c = ln10/400 = {C:.6f}；F'(0) = c/4 = {C/4:.6f} /Elo")

    # 1. Elo 更新 = 对数损失上的一步 SGD
    RA, RB, y, eta = 1600.0, 1500.0, 1.0, 32 / C
    def loss(ra):
        p = F(ra - RB)
        return -(y * np.log(p) + (1 - y) * np.log(1 - p))
    h = 1e-4
    g_num = (loss(RA + h) - loss(RA - h)) / (2 * h)
    g_ana = -C * (y - F(RA - RB))
    line(f"[SGD] 数值梯度 {g_num:.10f}，解析 -c(y-p) {g_ana:.10f}，差 {abs(g_num-g_ana):.1e}")
    line(f"[SGD] 学习率 eta=K/c 时一步 SGD 的增量 {-eta*g_ana:.4f}；Elo 增量 K(y-E) {32*(y-F(RA-RB)):.4f}")

    # 2. 稳态误差与最优 K
    for K in (16, 32):
        line(f"[稳态] K={K}: sqrt(K/2c) = {math.sqrt(K/(2*C)):.1f} Elo；含 a^2 修正 {float(rmse_theory(K)):.1f} Elo；"
             f"对应胜率 ±{100*(F(math.sqrt(K/(2*C)))-0.5):.1f} 个百分点")
    for sw in (2.0, 4.0, 10.0):
        res = optimize.minimize_scalar(lambda k: float(rmse_theory(k, sw)), bounds=(0.5, 200), method="bounded")
        line(f"[最优K] sigma_w={sw}: 数值最优 K*={res.x:.2f}（近似 2 sigma_w = {2*sw:.1f}），"
             f"最小 RMSE {res.fun:.1f}（近似 sqrt(2 sigma_w / c) = {math.sqrt(2*sw/C):.1f}）")
    line(f"[收敛] K=32 时误差衰减时间常数 1/a = 4/(Kc) = {4/(32*C):.1f} 局；K=16: {4/(16*C):.1f} 局")

    # 3. TrueSkill 两人对局的 ADF 更新与稳态等效 K
    mu0, sig0 = 25.0, 25 / 3
    beta, gamma = sig0 / 2, sig0 / 100
    v = lambda t: stats.norm.pdf(t) / stats.norm.cdf(t)
    w = lambda t: v(t) * (v(t) + t)
    # Elo 与 TrueSkill 刻度换算：在差值 0 处斜率相等 -> phi(0)/(sqrt2*beta_E) = c/4
    beta_elo = stats.norm.pdf(0) / (math.sqrt(2) * C / 4)
    unit = beta_elo / beta
    line(f"[TrueSkill] 等斜率换算：beta 对应 {beta_elo:.1f} Elo，1 个 TrueSkill 单位约 {unit:.1f} Elo")
    # 稳态：对手与自己同为稳态 sigma，比赛势均力敌（t=0）
    def fixed(s2):  # s2 = 赛前方差 sigma^2 + gamma^2
        c2 = 2 * beta ** 2 + 2 * s2
        return s2 * (1 - s2 * w(0.0) / c2) + gamma ** 2 - s2
    s2 = optimize.brentq(fixed, 1e-6, 50)
    c_t = math.sqrt(2 * beta ** 2 + 2 * s2)
    dmu = s2 / c_t * v(0.0)
    line(f"[TrueSkill] 稳态赛前 sigma = {math.sqrt(s2):.3f}（约 {math.sqrt(s2)*unit:.0f} Elo）；"
         f"势均力敌胜一局 mu 增加 {dmu:.4f} = {dmu*unit:.2f} Elo，相当于 Elo 的 K ≈ {2*dmu*unit:.1f}")
    line(f"[TrueSkill] 动态噪声 gamma = {gamma:.4f} = {gamma*unit:.2f} Elo/局 -> 线性化最优 K* ≈ 2*gamma = {2*gamma*unit:.1f}")
    # 新玩家第一局
    c_new = math.sqrt(2 * beta ** 2 + 2 * (sig0 ** 2 + gamma ** 2))
    dmu_new = (sig0 ** 2 + gamma ** 2) / c_new * v(0.0)
    line(f"[TrueSkill] 新玩家（sigma0）势均力敌胜一局 mu 增加 {dmu_new:.2f} = {dmu_new*unit:.0f} Elo（K≈{2*dmu_new*unit:.0f}）")
    # 用数值积分核对 ADF 均值更新（截断高斯矩匹配）
    sA2 = sig0 ** 2
    xs = np.linspace(mu0 - 10 * sig0, mu0 + 10 * sig0, 200001)
    prior = stats.norm.pdf(xs, mu0, sig0)
    like = stats.norm.cdf((xs - mu0) / math.sqrt(2 * beta ** 2 + sig0 ** 2))  # 对手 mu0, sig0 已积分
    post = prior * like
    post /= np.trapezoid(post, xs)
    m_num = np.trapezoid(xs * post, xs) - mu0
    c2 = math.sqrt(2 * beta ** 2 + 2 * sA2)
    line(f"[TrueSkill] 矩匹配数值核对：均值增量 数值 {m_num:.4f} vs 闭式 sigma^2/c*v(0) {sA2/c2*v(0.0):.4f}")

    # 3b. 评分噪声使预测过于自信：gamma ≈ λ / sqrt(1 + π c^2 σ_e^2 λ / 4)，λ = τ^2/(τ^2+σ_e^2)
    tau = 200.0
    for K, se, g_sim in ((16, 37.9, 0.948), (32, 54.3, 0.875), (64, 80.8, 0.770)):
        lam = tau ** 2 / (tau ** 2 + se ** 2)
        g = lam / math.sqrt(1 + math.pi * C ** 2 * se ** 2 * lam / 4)
        line(f"[过度自信] K={K}: 评分误差 {se} -> 收缩 λ={lam:.3f}，近似 gamma={g:.3f}（模拟拟合 {g_sim}）")

    # 4. Fisher 信息与“最难预测 = 最有信息”
    for d in (0, 100, 200, 400):
        p = float(F(d))
        line(f"[Fisher] d={d}: p={p:.3f}，I = c^2 p(1-p) = {C**2*p*(1-p):.3e}（相对最大值 {4*p*(1-p):.3f}），"
             f"准确率上限 {max(p,1-p):.3f}，log-loss 下限 {binary_entropy(p):.3f}，Brier 下限 {p*(1-p):.3f}")
    for delta in (5, 10, 25, 50, 100):
        dp = float(F(delta) - 0.5)
        n2se = (1 / dp) ** 2 * 0.25 * 4  # 2 SE: dp = 2*0.5/sqrt(N)
        n80 = ((stats.norm.ppf(0.975) + stats.norm.ppf(0.8)) * 0.5 / dp) ** 2
        line(f"[局数] Δ={delta} Elo: 胜率差 {100*dp:.2f} pp；两倍标准误需 {n2se:,.0f} 局；"
             f"5% 双侧 + 80% 检验力需 {n80:,.0f} 局")

    # 5. AlphaGo Zero 评估门槛：400 局、胜率需 >55%
    n = 400
    thr = int(math.floor(0.55 * n)) + 1  # 严格大于 55%
    p_false = stats.binom.sf(thr - 1, n, 0.5)
    line(f"[AGZ] 真实胜率 50% 时 400 局中 >55%（≥{thr} 胜）的概率 {p_false:.4f}")
    for ptrue in (0.52, 0.55, 0.60):
        line(f"[AGZ] 真实胜率 {ptrue:.2f} 时通过门槛概率 {stats.binom.sf(thr-1, n, ptrue):.3f}")

    # 6. 8 人名次的信息量与 Plackett–Luce
    line(f"[PL] log2(8!) = {math.log2(math.factorial(8)):.2f} bit；ln 8 = {math.log(8):.3f} nats = 3 bit")
    I8 = pl_fisher_equal(8)
    line(f"[PL] 8 人等强时单局名次的 Fisher 信息（log 权重刻度）= 1 - H_8/8 = {I8:.4f}；1v1 为 0.25；比值 {I8/0.25:.2f}")
    # 蒙特卡洛核对：得分函数（梯度）的方差 = Fisher 信息
    place = pl_sample(rng, np.zeros(8), 200000)
    order = np.argsort(place, axis=1)
    g0 = np.array([pl_grad(np.zeros(8), o)[0] for o in order[:20000]])
    line(f"[PL] 蒙特卡洛：玩家 0 梯度均值 {g0.mean():+.4f}，方差 {g0.var():.4f}（理论 {I8:.4f}）")
    line(f"[PL] 等强时各名次频率（应均为 0.125）：{np.round(np.bincount(place[:,0], minlength=9)[1:]/len(place),3)}")

    # 7. 酒馆战棋样本量
    za, zb = stats.norm.ppf(0.975), stats.norm.ppf(0.8)
    sd_place = math.sqrt((8 ** 2 - 1) / 12)
    n_top4 = ((za + zb) * 0.5 / 0.02) ** 2
    n_mean = ((za + zb) * sd_place / 0.1) ** 2
    line(f"[样本量] 名次标准差（均匀 1..8）= {sd_place:.3f}")
    line(f"[样本量] 前四率 +2pp（对已知 50% 基准）：{n_top4:,.0f} 局；两版本互比每版 {2*n_top4:,.0f} 局")
    line(f"[样本量] 平均名次 -0.1（对已知 4.5 基准）：{n_mean:,.0f} 局；两版本互比每版 {2*n_mean:,.0f} 局")


if __name__ == "__main__":
    main()
