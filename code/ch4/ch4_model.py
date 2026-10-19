"""第四章共用的模型函数：Elo 曲线、单玩家跟踪模拟、群体模拟、Plackett–Luce 名次模型。

记号与 docs/STYLE.md 一致：实力 s（Elo 刻度），评分 R，F(x)=1/(1+10^{-x/400})，c=ln10/400。
所有随机模拟都显式接收 numpy Generator，以便固定随机种子复现。
"""
from __future__ import annotations

import math
from itertools import permutations

import numpy as np

C = math.log(10) / 400.0          # Elo 曲线在 0 处的斜率常数 c
SLOPE0 = C / 4.0                  # F'(0) = c/4，约 0.00144 / Elo


def F(x):
    """Elo 胜率曲线 F(x) = 1/(1+10^{-x/400})，x 为评分差（Elo）。"""
    return 1.0 / (1.0 + np.power(10.0, -np.asarray(x, dtype=float) / 400.0))


def binary_entropy(p):
    """二元熵（nats）：H(p) = -p ln p - (1-p) ln(1-p)。"""
    p = np.clip(np.asarray(p, dtype=float), 1e-12, 1 - 1e-12)
    return -(p * np.log(p) + (1 - p) * np.log(1 - p))


# ---------------------------------------------------------------------------
# 1. 单玩家跟踪：K 作为学习率
# ---------------------------------------------------------------------------

def track_rating(rng, K, T, n_rep, sigma_w=0.0, sigma_q=0.0, s0_offset=0.0,
                 step_at=None, step_size=0.0):
    """一名玩家在按分匹配下的 Elo 跟踪。

    对手：评分 = 玩家当前评分 R_t + N(0, sigma_q^2)，且对手评分等于其真实实力（对手是“准的”）。
    真实实力 s_t：初值 0；每局随机游走 N(0, sigma_w^2)；可选在 step_at 局跳变 step_size。
    评分 R_0 = s_0 + s0_offset；每局 R <- R + K (y - F(R - R_opp))。

    K 可以是标量或形如 (m,1) 的数组（同时模拟多个 K）。返回 (s, R)，形状 (..., n_rep, T)。
    为节省内存，n_rep*T 较大时请改用 track_rmse。
    """
    K = np.asarray(K, dtype=float)
    shape = np.broadcast_shapes(K.shape, (n_rep,))
    s = np.zeros(shape)
    R = s + s0_offset
    S = np.empty(shape + (T,))
    RR = np.empty(shape + (T,))
    for t in range(T):
        if step_at is not None and t == step_at:
            s = s + step_size
        S[..., t] = s
        RR[..., t] = R
        opp = R + sigma_q * rng.standard_normal(shape)
        y = rng.random(shape) < F(s - opp)
        R = R + K * (y - F(R - opp))
        if sigma_w > 0:
            s = s + sigma_w * rng.standard_normal(shape)
    return S, RR


def track_rmse(rng, Ks, sigma_ws, T, burn, n_rep, sigma_q=0.0):
    """对多个 K 与多个漂移强度 sigma_w，返回稳态均方根跟踪误差 RMSE[i_w, i_K]。

    误差 e_t = R_t - s_t 在 t >= burn 后取均方，再对重复取平均后开方。
    """
    Ks = np.asarray(Ks, dtype=float)
    sw = np.asarray(sigma_ws, dtype=float)
    shape = (len(sw), len(Ks), n_rep)
    Kb = Ks[None, :, None]
    swb = sw[:, None, None]
    s = np.zeros(shape)
    R = np.zeros(shape)
    acc = np.zeros(shape)
    n = 0
    for t in range(T):
        opp = R + sigma_q * rng.standard_normal(shape)
        y = rng.random(shape) < F(s - opp)
        R = R + Kb * (y - F(R - opp))
        s = s + swb * rng.standard_normal(shape)
        if t >= burn:
            acc += (R - s) ** 2
            n += 1
    return np.sqrt((acc / n).mean(axis=2))


def rmse_theory(K, sigma_w=0.0, pq=0.25):
    """线性化稳态误差：Var = (K^2 pq + sigma_w^2) / (2a - a^2)，a = K c pq（附录推导）。"""
    K = np.asarray(K, dtype=float)
    a = K * C * pq
    return np.sqrt((K ** 2 * pq + sigma_w ** 2) / (2 * a - a ** 2))


# ---------------------------------------------------------------------------
# 2. 群体模拟：随机匹配 / 按分匹配
# ---------------------------------------------------------------------------

def population_elo(rng, n_players, tau, K, rounds, eval_from, matching="random",
                   sigma_q=25.0, record=True):
    """封闭群体的 Elo。每轮每人恰打一局。

    matching="random"：随机两两配对；"sbmm"：按 (评分 + N(0, sigma_q^2)) 排序后相邻配对。
    返回 dict：skill、最终 rating、eval 阶段每人胜场与局数，以及（record=True 时）eval 阶段
    每局的预测胜率 E（以配对中的第一人为视角）、真实胜率 p、结果 y、评分差 dR。
    """
    s = rng.normal(0.0, tau, n_players)
    R = np.zeros(n_players)
    wins = np.zeros(n_players)
    games = np.zeros(n_players)
    recE, recP, recY, recD = [], [], [], []
    half = n_players // 2
    for r in range(rounds):
        if matching == "random":
            order = rng.permutation(n_players)
        else:
            order = np.argsort(R + sigma_q * rng.standard_normal(n_players))
            # 相邻两两配对；随机决定谁是“第一人”，避免视角偏差
        a = order[0::2][:half]
        b = order[1::2][:half]
        flip = rng.random(half) < 0.5
        a, b = np.where(flip, b, a), np.where(flip, a, b)
        d = R[a] - R[b]
        E = F(d)
        p = F(s[a] - s[b])
        y = rng.random(half) < p
        R[a] += K * (y - E)
        R[b] -= K * (y - E)
        if r >= eval_from:
            wins[a] += y
            wins[b] += ~y
            games[a] += 1
            games[b] += 1
            if record:
                recE.append(E)
                recP.append(p)
                recY.append(y)
                recD.append(d)
    out = {"skill": s, "rating": R, "wins": wins, "games": games}
    if record:
        out.update(E=np.concatenate(recE), p=np.concatenate(recP),
                   y=np.concatenate(recY).astype(float), d=np.concatenate(recD))
    return out


def reliability(pred, y, bins):
    """分箱校准：返回每箱的平均预测、实际频率、样本数。"""
    idx = np.digitize(pred, bins) - 1
    m = len(bins) - 1
    mp = np.full(m, np.nan)
    fr = np.full(m, np.nan)
    n = np.zeros(m, dtype=int)
    for k in range(m):
        sel = idx == k
        n[k] = sel.sum()
        if n[k] > 0:
            mp[k] = pred[sel].mean()
            fr[k] = y[sel].mean()
    return mp, fr, n


def fit_scale(d, y, iters=30):
    """拟合 y ~ Bernoulli(F(gamma * d))，返回 gamma（Newton 法）。gamma<1 表示原预测过于自信。"""
    g = 1.0
    x = C * d
    for _ in range(iters):
        p = 1 / (1 + np.exp(-g * x))
        grad = np.sum((y - p) * x)
        hess = -np.sum(p * (1 - p) * x * x)
        g -= grad / hess
    return g


# ---------------------------------------------------------------------------
# 3. Plackett–Luce 名次模型（8 人）
# ---------------------------------------------------------------------------

def pl_sample(rng, strength, n):
    """按 Plackett–Luce 抽 n 局完整名次。strength 为 log 权重（自然对数刻度），形状 (N,)。
    返回 place[n, N]：每名玩家的名次（1 = 第一）。用 Gumbel 技巧：log w + Gumbel 排序。"""
    N = len(strength)
    g = rng.gumbel(size=(n, N)) + strength[None, :]
    order = np.argsort(-g, axis=1)
    place = np.empty_like(order)
    rows = np.arange(n)[:, None]
    place[rows, order] = np.arange(1, N + 1)[None, :]
    return place


def pl_place_dist_exact(strength, k=0):
    """玩家 k 的名次精确分布（逐个枚举其余玩家顺序的对称性：直接用递推）。

    对“一名玩家 + 其余 N-1 人等强”的情形有闭式；一般情形用全排列（N<=8 时可接受）。"""
    w = np.exp(np.asarray(strength, dtype=float))
    N = len(w)
    others = [i for i in range(N) if i != k]
    if np.allclose(w[others], w[others][0]):
        # 其余等强：第 i 步 k 仍在时被选中的概率 = w_k / (w_k + m*w_o)，m 为剩余对手数
        wk, wo = w[k], w[others][0]
        dist = np.zeros(N)
        alive = 1.0
        for i in range(N):
            m = N - 1 - i
            pk = wk / (wk + m * wo)
            dist[i] = alive * pk
            alive *= (1 - pk)
        return dist
    dist = np.zeros(N)
    for perm in permutations(range(N)):
        pr = 1.0
        rem = w.sum()
        for j in perm:
            pr *= w[j] / rem
            rem -= w[j]
        dist[perm.index(k)] += pr
    return dist


def pl_grad(strength, order):
    """Plackett–Luce 对数似然对每名玩家 log 权重的梯度。order[i] = 第 i+1 名的玩家编号。

    返回 g[k] = 1 - sum_{i <= r_k} P_i(k)（最后一名的“1”项在 i = N 时与 P_N = 1 抵消）。"""
    w = np.exp(np.asarray(strength, dtype=float))
    N = len(w)
    g = np.zeros(N)
    rem = list(order)
    for i in range(N):
        tot = w[rem].sum()
        for j in rem:
            g[j] -= w[j] / tot
        g[rem[0]] += 1.0
        rem = rem[1:]
    return g


def pl_fisher_equal(N):
    """N 人等强时，单局 Plackett–Luce 名次对某一人 log 权重的 Fisher 信息 = 1 - H_N / N。"""
    H = sum(1.0 / m for m in range(1, N + 1))
    return 1.0 - H / N
