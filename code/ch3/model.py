"""第三章（连胜/连败与“Elo 感”）的共享模型代码。

内容分四块，全部只依赖 numpy / scipy：

1. 独立同分布（i.i.d.）对局下的精确游程数学：最长连败分布（马尔可夫链动态规划）、
   Schilling / Gordon–Schilling–Waterman 渐近式、"≥k 连胜紧接 ≥k 连败"的计数与概率、
   滑动窗口低谷、Miller–Sanjurjo 有限样本偏差、跨人群合并的构成效应。
2. “马尔可夫调制伯努利”精确计算：隐藏状态 z 决定单局胜率，状态转移可依赖本局胜负。
   上头（连败触发）、两状态隐马尔可夫、局内疲劳都能写成这种形式（评分不动，K=0），
   于是条件胜率、自相关、最长连败分布、模式计数都能精确算出。
3. 单个玩家对“校准良好的对手池”的模拟：对手真实实力 = 对手评分 = 我的评分 + 排队噪声，
   评分按 Elo 更新（K=0 表示评分不动）。实力波动 u_t 有五种形式（i.i.d.、AR(1)、两状态、
   上头、疲劳）。所有玩家统计上相同，所以不存在人群构成效应。
4. 统计量：玩家内部条件胜率超额、最长连败、模式计数、滞后自相关、几种单人检验。

记号与正文一致：F(x)=1/(1+10^{-x/400})，c=ln10/400，F'(0)=c/4；p 为单局胜率，q=1-p。
人群 Monte Carlo（闭合人群、按分匹配、5v5、操纵规则）在 population.py。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import exp, log, pi, sqrt

import numpy as np

C_ELO = log(10.0) / 400.0          # c：Elo 曲线 ln10/400
SLOPE0 = C_ELO / 4.0               # F'(0)
EULER_GAMMA = 0.5772156649015329
Z_TWO_SIDED_80 = (1.959964 + 0.841621) ** 2   # (z_{0.975}+z_{0.8})^2：双侧 5%、检验力 80%


def elo_F(x):
    """Elo 胜率曲线 F(x)=1/(1+10^{-x/400})。"""
    return 1.0 / (1.0 + np.power(10.0, -np.asarray(x, dtype=float) / 400.0))


# 高斯–埃尔米特求积：E[F(u + sigma*Z)]，用于把排队噪声积分掉
_GH_X, _GH_W = np.polynomial.hermite_e.hermegauss(41)
_GH_W = _GH_W / _GH_W.sum()


def win_prob_noisy(u, sigma=0.0):
    """对手实力 = 我的评分 + N(0, sigma^2) 时，有效实力差为 u 的期望胜率 E[F(u - eta)]。"""
    u = np.asarray(u, dtype=float)
    if sigma <= 0:
        return elo_F(u)
    return (elo_F(u[..., None] - sigma * _GH_X) * _GH_W).sum(-1)


# =============================================================================================
# 1. i.i.d. 下的精确游程数学
# =============================================================================================

def prob_longest_lt(n: int, q: float, r: int) -> float:
    """n 局独立对局（每局输的概率 q）中最长连败 < r 的概率。

    状态 = 当前尾部连败长度 0..r-1；连败达到 r 即被吸收（删去）。复杂度 O(n r)。
    """
    if r <= 0:
        return 0.0
    v = np.zeros(r)
    v[0] = 1.0
    p = 1.0 - q
    for _ in range(n):
        nv = np.empty(r)
        nv[0] = v.sum() * p
        nv[1:] = v[:-1] * q
        v = nv
    return float(v.sum())


def prob_longest_ge(n: int, q: float, r: int) -> float:
    return 1.0 - prob_longest_lt(n, q, r)


def first_win_recursion(n: int, q: float, r: int) -> float:
    """首胜分解递推 a_m = sum_{j<r} q^j p a_{m-j-1}（m>=r），a_m=1（m<r）；返回 a_n=P(L_n<r)。"""
    p = 1.0 - q
    a = [1.0] * (n + 1)
    for m in range(r, n + 1):
        a[m] = sum(q ** j * p * a[m - j - 1] for j in range(r))
    return a[n]


def longest_run_distribution(n: int, q: float, rmax: int = 80):
    """返回 (E, SD, 中位数, 95 分位, ge)，ge[r]=P(L_n >= r)。"""
    lt = np.array([prob_longest_lt(n, q, r) for r in range(rmax + 2)])
    ge = 1.0 - lt
    pmf = lt[1:] - lt[:-1]
    mean = ge[1:].sum()
    second = sum((2 * r - 1) * ge[r] for r in range(1, rmax + 2))
    cdf = np.cumsum(pmf)
    return (float(mean), float(np.sqrt(second - mean ** 2)), int(np.searchsorted(cdf, 0.5)),
            int(np.searchsorted(cdf, 0.95)), ge)


def prob_longest_ge_curve(n_max: int, q: float, r: int) -> np.ndarray:
    """P(前 n 局中最长连败 >= r)，n = 0..n_max，一次前向 DP 得到整条曲线。"""
    v = np.zeros(r)
    v[0] = 1.0
    out = np.empty(n_max + 1)
    out[0] = 0.0
    p = 1.0 - q
    for n in range(1, n_max + 1):
        nv = np.empty(r)
        nv[0] = v.sum() * p
        nv[1:] = v[:-1] * q
        v = nv
        out[n] = 1.0 - v.sum()
    return out


def schilling_mean(n: int, q: float) -> float:
    """E[L_n] ≈ log_{1/q}(n p) + γ/ln(1/q) - 1/2（Gordon–Schilling–Waterman）。"""
    return log(n * (1 - q)) / log(1 / q) + EULER_GAMMA / log(1 / q) - 0.5


def schilling_sd(q: float) -> float:
    """SD[L_n] ≈ sqrt(π²/(6 ln²(1/q)) + 1/12)（忽略小的周期项）。"""
    return sqrt(pi ** 2 / (6 * log(1 / q) ** 2) + 1 / 12)


def poisson_longest_ge(n: int, q: float, r: int) -> float:
    """泊松近似 P(L_n >= r) ≈ 1 - exp(-[q^r + (n-r) p q^r])。"""
    return 1.0 - exp(-expected_runs_ge(n, q, r))


def expected_runs_ge(n: int, q: float, r: int) -> float:
    """长度 >= r 的连败段的期望个数 q^r [1 + (n-r) p]（开头一段 + 其后每个“胜后起连败”的位置）。"""
    if r > n:
        return 0.0
    return q ** r * (1 + (n - r) * (1 - q))


def expected_wklk(n: int, p: float, k: int) -> float:
    """“>=k 连胜紧接 >=k 连败”的期望次数 (n-2k+1)(pq)^k（等于子串 W^k L^k 的期望出现次数）。"""
    return max(n - 2 * k + 1, 0) * (p * (1 - p)) ** k


def wklk_automaton(k: int):
    """子串 W^k L^k 的 KMP 自动机：返回 (transW, transL)，状态 0..2k-1，到达 2k 记一次匹配并回到 0。"""
    pat = "W" * k + "L" * k
    m = len(pat)

    def nxt(state, ch):
        s = pat[:state] + ch
        for length in range(min(len(s), m), -1, -1):
            if s[len(s) - length:] == pat[:length]:
                return length
        return 0
    tw = [nxt(s, "W") for s in range(m)]
    tl = [nxt(s, "L") for s in range(m)]
    return tw, tl


def prob_pattern_once(n: int, p: float, k: int) -> float:
    """n 局独立对局中 W^k L^k 至少出现一次的概率（KMP 自动机精确 DP）。"""
    tw, tl = wklk_automaton(k)
    m = 2 * k
    v = np.zeros(m + 1)
    v[0] = 1.0
    for _ in range(n):
        nv = np.zeros(m + 1)
        nv[m] = v[m]
        for s in range(m):
            nv[tw[s]] += v[s] * p
            nv[tl[s]] += v[s] * (1 - p)
        v = nv
    return float(v[m])


def prob_window_slump(n: int, w: int, max_wins: int, p: float = 0.5) -> float:
    return float(prob_window_slump_curve(n, w, max_wins, p)[n])


def prob_window_slump_curve(n_max: int, w: int, max_wins: int, p: float = 0.5) -> np.ndarray:
    """n 局中存在某个连续 w 局只赢 <= max_wins 局的概率（精确 DP，状态为最近 w-1 局，w <= 20）。"""
    if w > 20:
        raise ValueError("w <= 20：状态数 2^(w-1)")
    nstate = 1 << (w - 1)
    pop = np.array([bin(s).count("1") for s in range(nstate)])
    # 前 w-1 局：直接枚举（不检查窗口）
    v = np.zeros(nstate)
    for s in range(nstate):
        k = pop[s]
        v[s] = p ** k * (1 - p) ** (w - 1 - k)
    hit = 0.0
    mask = nstate - 1
    curve = np.zeros(n_max + 1)
    for n in range(w, n_max + 1):
        nv = np.zeros(nstate)
        for bit, pr in ((1, p), (0, 1 - p)):
            wins = pop + bit                     # 本窗口（最近 w-1 局 + 本局）胜场数
            bad = wins <= max_wins
            hit += (v[bad] * pr).sum()
            ok = ~bad
            ns = ((np.arange(nstate) << 1) | bit) & mask
            np.add.at(nv, ns[ok], v[ok] * pr)
        v = nv
        curve[n] = hit
    return curve


def miller_sanjurjo(n: int, k: int, p: float = 0.5):
    """一段 n 局 i.i.d. 历史里“连胜 k 局后下一局的胜率”估计量的精确期望（只取该比率有定义的历史）。

    状态 = (截断到 k 的当前连胜长度, 合格局数 c, 其中胜场 w)。返回 (期望, 有定义的概率)。
    """
    q = 1 - p
    D = np.zeros((k + 1, n + 1, n + 1))
    D[0, 0, 0] = 1.0
    for _ in range(n):
        N_ = np.zeros_like(D)
        for s in range(k):
            N_[min(s + 1, k)] += p * D[s]
            N_[0] += q * D[s]
        N_[k, 1:, 1:] += p * D[k, :-1, :-1]
        N_[0, 1:, :] += q * D[k, :-1, :]
        D = N_
    P = D.sum(0)
    c = np.arange(n + 1)[:, None]
    w = np.arange(n + 1)[None, :]
    ratio = np.where(c > 0, w / np.maximum(c, 1), 0.0)
    defined = 1 - P[0].sum()
    return float((P[1:] * ratio[1:]).sum() / defined), float(defined)


def miller_sanjurjo_curve(n_max: int, k: int, p: float = 0.5, checkpoints=None):
    """miller_sanjurjo 的整条曲线：一次前向 DP，在 checkpoints（局数）处读出期望。"""
    q = 1 - p
    cps = set(checkpoints if checkpoints is not None else range(k + 1, n_max + 1))
    D = np.zeros((k + 1, n_max + 1, n_max + 1))
    D[0, 0, 0] = 1.0
    c = np.arange(n_max + 1)[:, None]
    w = np.arange(n_max + 1)[None, :]
    ratio = np.where(c > 0, w / np.maximum(c, 1), 0.0)
    res = {}
    for n in range(1, n_max + 1):
        N_ = np.zeros_like(D)
        for s in range(k):
            N_[min(s + 1, k)] += p * D[s]
            N_[0] += q * D[s]
        N_[k, 1:, 1:] += p * D[k, :-1, :-1]
        N_[0, 1:, :] += q * D[k, :-1, :]
        D = N_
        if n in cps:
            P = D.sum(0)
            defined = 1 - P[0].sum()
            res[n] = float((P[1:] * ratio[1:]).sum() / defined) if defined > 0 else np.nan
    return res


def miller_sanjurjo_k1(n: int, p: float = 0.5) -> float:
    """k=1 的闭式：给定 n1 场胜利，序列是均匀随机排列，E[P̂ | N1=n1, 有定义]=(n1-1)/(n-1)。

    有定义 ⇔ 前 n-1 局至少一胜；对 n1 的分布加权。用于核对 miller_sanjurjo(n, 1)。
    """
    from math import comb
    num = den = 0.0
    for n1 in range(1, n + 1):
        prob_seq = p ** n1 * (1 - p) ** (n - n1)
        n_seq = comb(n, n1)
        if n1 == 1:
            n_def = n - 1                       # 唯一一胜不在最后一局
        else:
            n_def = n_seq
        num += prob_seq * n_def * (n1 - 1) / (n - 1) if n1 > 1 else 0.0
        den += prob_seq * n_def
    return num / den


def pooled_streak_winrate(k: int, tau: float = 200.0, nodes: int = 201) -> float:
    """随机匹配、实力固定 ~ N(0, tau²) 的人群中，合并所有人统计的 P(胜 | 最近 k 局全胜)=E[p^{k+1}]/E[p^k]。

    p_i = E_j F(s_i - s_j) 是玩家 i 对随机对手的单局胜率；k=0 时为 1/2。负 k 表示最近 |k| 局全败。
    """
    x, w = np.polynomial.hermite_e.hermegauss(nodes)
    w = w / w.sum()
    s = tau * x
    # p(s) = E_{s'} F(s - s')，s' ~ N(0, tau²)
    pi_ = (elo_F(s[:, None] - tau * x[None, :]) * w[None, :]).sum(1)
    if k >= 0:
        return float((w * pi_ ** (k + 1)).sum() / (w * pi_ ** k).sum())
    kk = -k
    return float((w * pi_ * (1 - pi_) ** kk).sum() / (w * (1 - pi_) ** kk).sum())


# =============================================================================================
# 2. 马尔可夫调制伯努利：评分不动（K=0）时的精确计算
# =============================================================================================

@dataclass
class ModulatedChain:
    """隐藏状态链 + 每状态单局胜率。

    TW[z, z'] = P(本局胜, 下一状态 z' | 当前状态 z)，TL 同理（本局负）。
    pwin[z] = TW[z].sum()。所有精确量都从这两个矩阵出发。
    """
    TW: np.ndarray
    TL: np.ndarray
    labels: list = field(default_factory=list)

    @property
    def pwin(self):
        return self.TW.sum(1)

    @property
    def M(self):
        return self.TW + self.TL

    def stationary(self) -> np.ndarray:
        vals, vecs = np.linalg.eig(self.M.T)
        i = np.argmin(np.abs(vals - 1))
        pi_ = np.real(vecs[:, i])
        return pi_ / pi_.sum()

    def mean_winrate(self) -> float:
        return float(self.stationary() @ self.pwin)

    def cond_after_losses(self, k: int) -> float:
        """P(下一局胜 | 最近 k 局全负)，平稳状态下。"""
        v = self.stationary()
        for _ in range(k):
            v = v @ self.TL
        return float(v @ self.pwin / v.sum())

    def cond_after_wins(self, k: int) -> float:
        v = self.stationary()
        for _ in range(k):
            v = v @ self.TW
        return float(v @ self.pwin / v.sum())

    def autocorr(self, h: int) -> float:
        """结果的滞后 h 自相关 Corr(y_t, y_{t+h})。"""
        pi_ = self.stationary()
        pbar = pi_ @ self.pwin
        v = pi_ @ self.TW
        for _ in range(h - 1):
            v = v @ self.M
        joint = v @ self.pwin
        return float((joint - pbar ** 2) / (pbar * (1 - pbar)))

    def longest_loss_lt(self, n: int, r: int, start=None) -> float:
        """n 局中最长连败 < r 的概率：增广状态 (z, 当前连败 ℓ<r)。"""
        Z = self.TW.shape[0]
        v = np.zeros((r, Z))
        v[0] = self.stationary() if start is None else start
        for _ in range(n):
            nv = np.zeros((r, Z))
            nv[0] = v.sum(0) @ self.TW
            nv[1:] = v[:-1] @ self.TL
            v = nv
        return float(v.sum())

    def expected_wklk(self, n: int, k: int) -> float:
        """“>=k 连胜紧接 >=k 连败”在 n 局中的期望次数（联合 (z, 自动机) 的前向 DP）。"""
        tw, tl = wklk_automaton(k)
        m = 2 * k
        Z = self.TW.shape[0]
        v = np.zeros((m, Z))
        v[0] = self.stationary()
        total = 0.0
        for _ in range(n):
            nv = np.zeros((m, Z))
            for s in range(m):
                if v[s].sum() == 0:
                    continue
                a = v[s] @ self.TW
                nv[tw[s]] += a
                b = v[s] @ self.TL
                if tl[s] == m:
                    total += b.sum()
                    nv[0] += b
                else:
                    nv[tl[s]] += b
            v = nv
        return float(total)

    def loss_run_survival(self, rmax: int) -> np.ndarray:
        """一段连败开始后其长度 >= r 的概率（r=1..rmax），在平稳状态下按“胜后首负”起算。"""
        pi_ = self.stationary()
        # 一段连败的起点：上一局胜（或序列开头，忽略）后本局负
        v = (pi_ @ self.TW) @ self.TL       # 胜 → 负：连败长度 >= 1
        start = v.sum()
        out = np.empty(rmax)
        for r in range(1, rmax + 1):
            out[r - 1] = v.sum() / start
            v = v @ self.TL
        return out


def chain_iid(p: float = 0.5) -> ModulatedChain:
    return ModulatedChain(np.array([[p]]), np.array([[1 - p]]), ["iid"])


def chain_tilt(theta: float, m: int, sigma_q: float = 0.0, break_prob: float = 0.0,
               lmax: int = None) -> ModulatedChain:
    """上头：状态 L = 当前连败（截断到 m），有效实力 u = -θ·min(L, m)。

    赢一局 L 归零；输一局 L+1（截断到 m）。每局结束后以 break_prob 的概率下线休息，L 也归零。
    """
    Z = m + 1
    p = win_prob_noisy(-theta * np.arange(Z), sigma_q)
    TW = np.zeros((Z, Z))
    TL = np.zeros((Z, Z))
    for L in range(Z):
        TW[L, 0] = p[L]
        nxt = min(L + 1, m)
        TL[L, nxt] += (1 - p[L]) * (1 - break_prob)
        TL[L, 0] += (1 - p[L]) * break_prob
    return ModulatedChain(TW, TL, [f"L={L}" for L in range(Z)])


def chain_hmm(u_states, P, sigma_q: float = 0.0) -> ModulatedChain:
    """两状态（或多状态）隐马尔可夫：状态转移与胜负无关，P[z, z'] 为转移矩阵。"""
    u_states = np.asarray(u_states, float)
    p = win_prob_noisy(u_states, sigma_q)
    P = np.asarray(P, float)
    TW = p[:, None] * P
    TL = (1 - p)[:, None] * P
    return ModulatedChain(TW, TL, [f"u={u:g}" for u in u_states])


def chain_fatigue(phi: float, end_prob: float, jmax: int = 80, sigma_q: float = 0.0,
                  floor: float = None) -> ModulatedChain:
    """局内疲劳：状态 j = 本次连续游玩中的第几局（1..jmax），u = -φ (j-1)（可设下限）。

    每局后以 end_prob 的概率结束本次游玩，下一局回到 j=1。
    """
    j = np.arange(1, jmax + 1)
    u = -phi * (j - 1)
    if floor is not None:
        u = np.maximum(u, floor)
    p = win_prob_noisy(u, sigma_q)
    Z = jmax
    P = np.zeros((Z, Z))
    for a in range(Z):
        P[a, 0] += end_prob
        P[a, min(a + 1, Z - 1)] += 1 - end_prob
    TW = p[:, None] * P
    TL = (1 - p)[:, None] * P
    return ModulatedChain(TW, TL, [f"j={x}" for x in j])


# =============================================================================================
# 3. 单个玩家对校准对手池的模拟
# =============================================================================================

@dataclass
class PlayerModel:
    """实力波动模型 u_t 的参数。kind ∈ {none, iid, ar1, hmm, tilt, fatigue}。"""
    kind: str = "none"
    sd: float = 0.0               # iid / ar1：平稳标准差
    rho: float = 0.0              # ar1：自回归系数
    u_states: tuple = (0.0, 0.0)  # hmm：两个状态的 u
    trans: tuple = (0.0, 0.0)     # hmm：(P(0→1), P(1→0))
    theta: float = 0.0            # tilt：每多输一局实力下降
    cap: int = 3                  # tilt：上限 m
    phi: float = 0.0              # fatigue：每多打一局实力下降
    end_prob: float = 0.0         # 每局后结束本次游玩（休息）的概率；上头在休息后归零
    label: str = ""


def simulate_player(model: PlayerModel, M: int, T: int, K: float = 0.0, sigma_q: float = 50.0,
                    burn: int = 400, seed: int = 0, record_R: bool = False):
    """M 个统计上相同的玩家（真实平均实力 s=0）各打 burn+T 局，返回后 T 局的记录。

    对手真实实力 = 对手评分 = R_t + η，η ~ N(0, sigma_q²)（对手池已校准，κ=1）。
    单局胜率 p_t = F(u_t - (R_t + η))；评分 R_{t+1} = R_t + K (y_t - F(-η))。K=0 时评分固定在 0。
    返回 dict：y (T×M bool)、p (T×M float32)、ws/ls（赛前当前连胜/连败，int16）、
    j（赛前本次游玩中的局序号，int16）、u（float32），可选 R（赛前评分）。
    """
    rng = np.random.default_rng(seed)
    R = np.zeros(M)
    ws = np.zeros(M, np.int32)
    ls = np.zeros(M, np.int32)
    tilt_L = np.zeros(M, np.int32)      # 上头计数：休息后归零
    j = np.ones(M, np.int32)
    kind = model.kind
    if kind == "ar1":
        u_ar = rng.normal(0, model.sd, M)
        eps_sd = model.sd * sqrt(1 - model.rho ** 2)
    if kind == "hmm":
        P01, P10 = model.trans
        pi1 = P01 / (P01 + P10)
        z = (rng.random(M) < pi1).astype(np.int8)
        ust = np.asarray(model.u_states, float)
    rec = dict(y=np.zeros((T, M), bool), p=np.zeros((T, M), np.float32),
               ws=np.zeros((T, M), np.int16), ls=np.zeros((T, M), np.int16),
               j=np.zeros((T, M), np.int16), u=np.zeros((T, M), np.float32))
    if record_R:
        rec["R"] = np.zeros((T, M), np.float32)
    for t in range(burn + T):
        if kind == "none":
            u = np.zeros(M)
        elif kind == "iid":
            u = rng.normal(0, model.sd, M)
        elif kind == "ar1":
            u = u_ar
        elif kind == "hmm":
            u = ust[z]
        elif kind == "tilt":
            u = -model.theta * np.minimum(tilt_L, model.cap)
        elif kind == "fatigue":
            u = -model.phi * (j - 1)
        else:
            raise ValueError(kind)
        eta = rng.normal(0, sigma_q, M) if sigma_q > 0 else np.zeros(M)
        p = elo_F(u - (R + eta))
        y = rng.random(M) < p
        if t >= burn:
            i = t - burn
            rec["y"][i] = y
            rec["p"][i] = p
            rec["ws"][i] = ws
            rec["ls"][i] = ls
            rec["j"][i] = j
            rec["u"][i] = u
            if record_R:
                rec["R"][i] = R
        if K:
            R = R + K * (y - elo_F(-eta))
        ws = np.where(y, ws + 1, 0)
        ls = np.where(y, 0, ls + 1)
        tilt_L = np.where(y, 0, tilt_L + 1)
        # 休息：本次游玩结束（所有模型共用同一个休息过程，只有上头和疲劳会用到它）
        if model.end_prob > 0:
            brk = rng.random(M) < model.end_prob
            j = np.where(brk, 1, j + 1)
            tilt_L = np.where(brk, 0, tilt_L)
        else:
            j = j + 1
        if kind == "ar1":
            u_ar = model.rho * u_ar + rng.normal(0, eps_sd, M)
        elif kind == "hmm":
            r_ = rng.random(M)
            z = np.where(z == 0, (r_ < P01).astype(np.int8), (r_ >= P10).astype(np.int8))
    return rec


# =============================================================================================
# 4. 统计量
# =============================================================================================

def cond_excess(p, ws, ls, kmax=6, pbar=None):
    """玩家内部超额：E[p | 最近 k 局全胜] - 该玩家自身平均 p（k=1..kmax），连败同理。单位：概率。"""
    if pbar is None:
        pbar = p.mean(0, dtype=np.float64)
    W = np.empty(kmax)
    L = np.empty(kmax)
    for k in range(1, kmax + 1):
        mW = ws >= k
        mL = ls >= k
        W[k - 1] = (p[mW] - np.broadcast_to(pbar, p.shape)[mW]).mean() if mW.any() else np.nan
        L[k - 1] = (p[mL] - np.broadcast_to(pbar, p.shape)[mL]).mean() if mL.any() else np.nan
    return W, L


def longest_loss_runs(y):
    """每列（每名玩家）的最长连败。y: T×M bool（True=胜）。"""
    T, M = y.shape
    cur = np.zeros(M, np.int32)
    mx = np.zeros(M, np.int32)
    for t in range(T):
        cur = np.where(y[t], 0, cur + 1)
        np.maximum(mx, cur, out=mx)
    return mx


def count_wklk(y, k):
    """每列中子串 W^k L^k 的出现次数（= “>=k 连胜紧接 >=k 连败”的边界数）。"""
    T, M = y.shape
    csW = np.vstack([np.zeros((1, M), np.int32), np.cumsum(y, 0, dtype=np.int32)])
    csL = np.vstack([np.zeros((1, M), np.int32), np.cumsum(~y, 0, dtype=np.int32)])
    m = T - 2 * k + 1
    hit = ((csW[k:k + m] - csW[:m]) == k) & ((csL[2 * k:2 * k + m] - csL[k:k + m]) == k)
    return hit.sum(0)


def shuffle_within(y, rng):
    """每名玩家的结果在时间上随机打乱（保留其胜场数），作为“独立”基线。"""
    return np.take_along_axis(y, np.argsort(rng.random(y.shape), axis=0), 0)


def lag_autocorr(y, h=1):
    """按玩家去均值后合并的滞后 h 自相关。"""
    x = y - y.mean(0)
    return float((x[:-h] * x[h:]).sum() / (x * x).sum())


def detect_games(rho):
    """单个玩家用滞后 1 自相关检验（双侧 5%、检验力 80%）所需局数 (z_.975+z_.8)²/ρ²。"""
    return Z_TWO_SIDED_80 / rho ** 2


# ---- 单人检验统计量（每列一个值），零分布另用 i.i.d. 模拟校准 ----

def stat_lag1(y):
    x = y.astype(np.float64)
    x = x - x.mean(0)
    den = (x * x).sum(0)
    return np.where(den > 0, (x[:-1] * x[1:]).sum(0) / np.maximum(den, 1e-12), 0.0)


def stat_tilt_slope(y, ls, cap=3):
    """y_t 对 min(赛前连败, cap) 的最小二乘斜率（每列）。"""
    x = np.minimum(ls, cap).astype(np.float64)
    yy = y.astype(np.float64)
    xm = x - x.mean(0)
    den = (xm * xm).sum(0)
    return np.where(den > 0, (xm * (yy - yy.mean(0))).sum(0) / np.maximum(den, 1e-12), 0.0)


def stat_block_dispersion(y, block=10):
    """非重叠 block 局胜场数的方差 / 二项方差（每列）：慢变化的状态会让它 > 1。"""
    T, M = y.shape
    nb = T // block
    w = y[:nb * block].reshape(nb, block, M).sum(1).astype(np.float64)
    pbar = w.mean(0) / block
    binv = block * pbar * (1 - pbar)
    return np.where(binv > 0, w.var(0, ddof=1) / np.maximum(binv, 1e-12), 1.0)


def stat_session_slope(y, j, jcap=15):
    """y_t 对“本次游玩中的局序号”（截断到 jcap）的斜率（每列）。"""
    x = np.minimum(j, jcap).astype(np.float64)
    yy = y.astype(np.float64)
    xm = x - x.mean(0)
    den = (xm * xm).sum(0)
    return np.where(den > 0, (xm * (yy - yy.mean(0))).sum(0) / np.maximum(den, 1e-12), 0.0)


# =============================================================================================
# 5. 诚实 Elo 均值回归的线性高斯近似
# =============================================================================================

def elo_gain(K: float, kappa: float = 1.0, team_size: int = 1) -> float:
    """评分误差每局被纠正的比例 b = κ c K / (4 n)。"""
    return kappa * C_ELO * K / (4.0 * team_size)


def elo_error_sd(K: float, kappa: float = 1.0, team_size: int = 1) -> float:
    """稳态评分误差 SD：σ_e² ≈ K² / (4 b (2-b))（n=1、κ=1 时 ≈ 9.3√K）。"""
    b = elo_gain(K, kappa, team_size)
    return sqrt(K ** 2 / (4.0 * b * (2.0 - b)))


def elo_streak_excess(k, K: float, kappa: float = 1.0, team_size: int = 1):
    """连胜 k 局后下一局胜率相对自身平均的超额（线性高斯近似，推导见附录）。

    评分误差 e 满足 e_{t+1}=(1-b)e_t+Kξ_t，σ_e²=K²/(4b(2-b))，b=κcK/(4n)。
    连胜 k 局：评分涨了约 kK/2；同时这 k 场胜利说明起点时 e 偏低，后验平移 -(kκc/(2n))σ_e²。
    两者相减得过冲 E[e_t | 最近 k 局全胜] = kK(1-b)/(2(2-b)) ≈ kK/4，
    超额 Δ_k = -(κc/(4n))·过冲 ≈ -κcKk/(16n)。返回 (Δ_k, 过冲)。
    """
    b = elo_gain(K, kappa, team_size)
    k = np.asarray(k, float)
    var_e = K ** 2 / (4.0 * b * (2.0 - b))
    overshoot = k * K / 2.0 - k * kappa * C_ELO / (2.0 * team_size) * var_e
    return -kappa * C_ELO / (4.0 * team_size) * overshoot, overshoot


def elo_lag1(K: float, kappa: float = 1.0, team_size: int = 1) -> float:
    """诚实 Elo 下结果的滞后 1 自相关（线性化）：ρ_1 ≈ -κcK/(4n(2-b)) ≈ -κcK/(8n)。"""
    b = elo_gain(K, kappa, team_size)
    return -kappa * C_ELO * K / (4.0 * team_size * (2.0 - b))


def slope_attenuation(sd: float) -> float:
    """E[F'(X)]/F'(0)，X ~ N(0, sd²)：实力差分散时 Elo 曲线的平均斜率相对 0 点斜率的比例。"""
    x = sd * _GH_X
    f = elo_F(x)
    return float((_GH_W * f * (1 - f)).sum() / 0.25)


def ar1_retained(rho: float, b: float) -> float:
    """AR(1) 状态 u 经评分指数平滑后，残留在 u_t - x_t 里的方差比例 2(1-ρ)/((2-b)(1-(1-b)ρ))。"""
    return 2.0 * (1.0 - rho) / ((2.0 - b) * (1.0 - (1.0 - b) * rho))


def linear_outcome_acf(rho: float, sd_u: float, K: float, hmax: int = 30, kappa: float = 1.0,
                       n_terms: int = 4000):
    """线性化系统的结果自相关 Corr(y_t, y_{t+h})，h=1..hmax。

    x_{t+1} = (1-b) x_t + b u_t + K ξ_t（x = 评分 - 平均实力），u 为 AR(1)，ξ 为结果噪声（方差 1/4）；
    p_t - 1/2 = κ (c/4)(u_t - x_t)。用 MA(∞) 截断表示精确算出自协方差。K=0 时退化为
    (c/4)² Var(u) ρ^h / (1/4)。
    """
    a = 1.0 - elo_gain(K, kappa)
    b = 1.0 - a
    g = kappa * SLOPE0
    j = np.arange(n_terms)
    # u_t = sum_j psi_j ε_{t-j}，ε 方差 sd_u²(1-ρ²)
    var_eps = sd_u ** 2 * (1 - rho ** 2)
    psi = rho ** j
    # x_t 对 ε 的脉冲响应：x_t = b sum_{i>=1} a^{i-1} u_{t-i}
    x_eps = np.zeros(n_terms)
    if b > 0:
        conv = np.convolve(a ** j, psi)[:n_terms]     # sum_{i} a^{i} psi_{m-i}
        x_eps[1:] = b * conv[:-1]
    d_eps = psi - x_eps                               # D_t = u_t - x_t 对 ε 的脉冲
    # D_t 对结果噪声 ξ 的脉冲：-K a^{i-1}（i>=1），ξ 方差 1/4
    d_xi = np.zeros(n_terms)
    d_xi[1:] = -K * a ** j[:-1]
    out = np.empty(hmax)
    for h in range(1, hmax + 1):
        cov_DD = var_eps * (d_eps[:-h] * d_eps[h:]).sum() + 0.25 * (d_xi[:-h] * d_xi[h:]).sum()
        cov_xiD = 0.25 * d_xi[h]                      # Cov(ξ_t, D_{t+h})
        out[h - 1] = (g ** 2 * cov_DD + g * cov_xiD) / 0.25
    return out
