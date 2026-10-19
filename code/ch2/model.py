"""第二章（研究二：不干涉匹配时胜率能否计算）共用的模型、解析公式与模拟器。

记号与 docs/STYLE.md 一致（Elo 刻度）：
    F(x) = 1 / (1 + 10^(-x/400))      Elo 胜率曲线
    c    = ln10 / 400                 F'(0) = c / 4
    s    真实实力，R 评分，K K 因子，tau 群体实力标准差，sigma_q 匹配噪声

模型设定（所有模拟共用，正文和附录表 app:ch2-params 中给出同样的参数）：
    * 玩家 N 人，s ~ N(MU, TAU^2)，初始评分全部为 1500（init="flat"）或等于实力（init="true"）。
    * 1v1 真实胜率 P = F(s_i - s_j)（评分模型设定正确）；可加单局独立噪声或 AR(1) 状态。
    * n 对 n 团队：加和模型 P = F((sum s_A - sum s_B)/sqrt(n))，均值模型 P = F(mean s_A - mean s_B)；
      每名队员都按团队期望得分更新 K(y - E)，E 用与结果模型相同的函数形式。
    * N 人自由混战（FFA）：表现 = s + Gumbel(尺度 400/ln10)，名次即 Plackett-Luce，
      评分按两两比较更新，每对步长 K/(N-1)。
    * 匹配：random = 每轮全体随机打乱；sbmm = 按 R + N(0, sigma_q^2) 排序后相邻成组；
      团队在 2n 人组内蛇形分队。不使用任何隐藏变量。
    * 每轮每人恰好一局。

本文件不依赖 research_notes/ 下的任何代码。重模拟结果缓存到 code/ch2/cache/*.npz。
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from scipy import stats

LN10 = math.log(10.0)
C = LN10 / 400.0                  # c = ln10/400，F'(0) = c/4
SLOPE0 = C / 4.0                  # F'(0) ≈ 0.001439 / 分
GUMBEL_SCALE = 400.0 / LN10       # ≈ 173.7，Gumbel 尺度使两两边际恰为 F
PROBIT = 1.702                    # logistic(x) ≈ Φ(x/1.702)
SIGMA_D = PROBIT / C              # ≈ 295.7：F(d) ≈ Φ(d/σ_d)
MU, TAU = 1500.0, 200.0

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"

Phi = stats.norm.cdf
PhiInv = stats.norm.ppf


# ---------------------------------------------------------------------------
# 基本函数
# ---------------------------------------------------------------------------
def F(d):
    """Elo 胜率曲线 F(d) = 1/(1+10^(-d/400))。"""
    return 1.0 / (1.0 + np.power(10.0, -np.asarray(d, dtype=float) / 400.0))


def Finv(p):
    """F 的反函数（概率 -> 分差）。"""
    p = np.asarray(p, dtype=float)
    return 400.0 * np.log10(p / (1.0 - p))


_GH_X, _GH_W = np.polynomial.hermite_e.hermegauss(80)
_GH_W = _GH_W / _GH_W.sum()


def gauss_expect(fun, mean, sd):
    """E[fun(X)]，X ~ N(mean, sd^2)，用 80 点 Gauss-Hermite（mean 可为数组）。"""
    mean = np.asarray(mean, dtype=float)
    x = mean[..., None] + sd * _GH_X
    return (fun(x) * _GH_W).sum(-1)


# ---------------------------------------------------------------------------
# 解析结果（推导见正文与附录 app:ch2-...）
# ---------------------------------------------------------------------------
def winrate_random_probit(s, mu=MU, tau=TAU, sigma_d=SIGMA_D):
    """随机匹配 1v1：W(s) = Φ((s-μ)/sqrt(σ_d^2+τ^2))（逻辑斯蒂→正态近似）。"""
    return Phi((np.asarray(s) - mu) / math.sqrt(sigma_d ** 2 + tau ** 2))


def winrate_random_exact(s, mu=MU, tau=TAU, noise_sd=0.0):
    """随机匹配 1v1 的精确期望胜率：E_t[F(s - t + x_i - x_j)]，t~N(μ,τ²)，x~N(0,σ_x²)。"""
    sd = math.sqrt(tau ** 2 + 2.0 * noise_sd ** 2)
    return gauss_expect(F, np.asarray(s, dtype=float) - mu, sd)


def rho(tau=TAU, sigma_d=SIGMA_D):
    """百分位形式 W(q) = Φ(ρ z_q) 中的 ρ = τ / sqrt(τ² + σ_d²)。"""
    return tau / math.sqrt(tau ** 2 + sigma_d ** 2)


def sigma_e(K, lam=1.0):
    """评分围绕实力的稳态误差标准差（线性化、对手误差同分布）：
    Var(e) = K λ / (2c (1 - K c / (4λ)))；λ=1 时 ≈ 9.32 sqrt(K)。"""
    return np.sqrt(K * lam / (2.0 * C * (1.0 - K * C / (4.0 * lam))))


def sigma_e_simple(K):
    """不含修正项的近似 sqrt(K/(2c)) = sqrt(200K/ln10) ≈ 9.32 sqrt(K)。"""
    return np.sqrt(K / (2.0 * C))


def tau_R_ideal(K):
    """理想时间常数 4/(Kc) = 1600/(K ln10) ≈ 695/K 局（λ=1 且 P(1-P)=1/4）。"""
    return 4.0 / (K * C)


def lambda_star(K, sigma_q):
    """按分匹配下评分刻度的平稳伸缩系数 λ* = 1/(1 - σ_e(1)^2/σ_q^2)；σ_q <= σ_e 时不存在（返回 inf）。"""
    s0 = sigma_e(K, 1.0) ** 2
    sq = np.asarray(sigma_q, dtype=float) ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        lam = np.where(sq > s0, 1.0 / (1.0 - s0 / sq), np.inf)
    return lam


def lambda_ode(K, sigma_q, t_max, lam0=1.0, tau=TAU, dt=1.0):
    """λ(t) 的平均场方程（附录推导）：
    dλ/dt = (Kc/4) [σ_e² + σ_q²(1-λ)] / (λ²τ² + σ_e² + σ_q²)，σ_e² = σ_e(K, λ)²。"""
    n = int(t_max / dt) + 1
    lam = np.empty(n)
    lam[0] = lam0
    for i in range(1, n):
        L = lam[i - 1]
        se2 = sigma_e(K, L) ** 2
        d = (K * C / 4.0) * (se2 + sigma_q ** 2 * (1.0 - L)) / (L ** 2 * tau ** 2 + se2 + sigma_q ** 2)
        lam[i] = L + dt * d
    return np.arange(n) * dt, lam


def sbmm_edge_winrate(z, K, sigma_q, tau=TAU):
    """平稳按分匹配下，评分标准化位置为 z 的玩家的期望胜率（窗口边缘效应，附录推导）：
    R-R' ~ N((1-g)(R-μ), g(1+g)σ_q²)，g = σ_R²/(σ_R²+σ_q²)，W ≈ E[Φ((R-R')/σ_d)]。"""
    lam = float(lambda_star(K, sigma_q))
    if not np.isfinite(lam):
        return np.full_like(np.asarray(z, dtype=float), np.nan)
    se2 = sigma_e(K, lam) ** 2
    sR2 = lam ** 2 * tau ** 2 + se2
    g = sR2 / (sR2 + sigma_q ** 2)
    m = (1.0 - g) * math.sqrt(sR2) * np.asarray(z, dtype=float)
    v = g * (1.0 + g) * sigma_q ** 2
    return Phi(m / math.sqrt(SIGMA_D ** 2 + v))


def tau_R_meanfield(K, sigma_q, tau=TAU):
    """修正后的时间常数 τ_R ≈ 4 / (K c κ)，κ = 4E[P(1-P)] · (λτ² + σ_q²)/(σ_R² + σ_q²)。"""
    lam = float(lambda_star(K, sigma_q))
    se2 = sigma_e(K, lam) ** 2
    sR2 = lam ** 2 * tau ** 2 + se2
    # 配对双方真实实力差：评分差 ~ N(0, 2gσ_q²(1+g))，再除以 λ 并叠加两人的误差
    g = sR2 / (sR2 + sigma_q ** 2)
    sd_ds = math.sqrt(2 * g * sigma_q ** 2 + 2 * se2) / lam
    pq = gauss_expect(lambda x: F(x) * (1 - F(x)), 0.0, sd_ds)
    kappa = 4 * float(pq) * (lam * tau ** 2 + sigma_q ** 2) / (sR2 + sigma_q ** 2)
    return 4.0 / (K * C * kappa)


def pl_top_k(w, n_players, k):
    """Plackett–Luce：焦点玩家 worth=w，其余 N-1 人 worth=1，进入前 k 名的概率。"""
    w = np.asarray(w, dtype=float)
    out = np.ones_like(w)
    for j in range(k):
        out = out * (n_players - 1 - j) / (w + n_players - 1 - j)
    return 1.0 - out


def pl_place_dist(w, n_players):
    """Plackett–Luce 下焦点玩家名次 1..N 的分布（返回形状 (..., N)）。"""
    w = np.asarray(w, dtype=float)
    cum = np.stack([pl_top_k(w, n_players, k) for k in range(0, n_players + 1)], -1)
    return np.diff(cum, axis=-1)


# ---------------------------------------------------------------------------
# 模拟器
# ---------------------------------------------------------------------------
def snake_index(n):
    """2n 人按评分排好序后的蛇形分队：A B B A A B B A ..."""
    A, B = [], []
    for i in range(2 * n):
        (A if (i % 4 in (0, 3)) else B).append(i)
    return np.array(A), np.array(B)


class EloSim:
    """固定 K 的 Elo + 诚实匹配的群体模拟。"""

    def __init__(self, n_players=10000, K=16.0, fmt="1v1", mm="random", sigma_q=100.0,
                 tau=TAU, mu=MU, team_n=5, team_model="sum", ffa_n=8,
                 noise_sd=0.0, ar_sd=0.0, ar_phi=0.99, init="flat", seed=1):
        self.rng = np.random.default_rng(seed)
        self.N, self.K, self.fmt, self.mm = n_players, float(K), fmt, mm
        self.sigma_q, self.noise_sd = float(sigma_q), float(noise_sd)
        self.ar_sd, self.ar_phi = float(ar_sd), float(ar_phi)
        self.team_n, self.team_model, self.ffa_n = team_n, team_model, ffa_n
        self.mu = mu
        self.s = mu + tau * self.rng.standard_normal(n_players)
        self.extra = np.zeros(n_players)        # 确定性的实力变化（进步情景）
        self.u = ar_sd * self.rng.standard_normal(n_players) if ar_sd > 0 else np.zeros(n_players)
        self.R = self.s.copy() if init == "true" else np.full(n_players, 1500.0)
        self.group = {"1v1": 2, "team": 2 * team_n, "ffa": ffa_n}[fmt]
        assert n_players % self.group == 0
        if fmt == "team":
            self.iA, self.iB = snake_index(team_n)

    def skill_now(self):
        return self.s + self.extra + self.u

    def order(self):
        if self.mm == "random":
            return self.rng.permutation(self.N)
        key = self.R + self.sigma_q * self.rng.standard_normal(self.N)
        return np.argsort(key, kind="stable")

    def step(self):
        """进行一轮。返回 dict：y（胜=1；FFA 为第 1 名）、E（系统预测）、p（真实胜率）、place、top。"""
        rng, N = self.rng, self.N
        sk = self.skill_now()
        if self.noise_sd > 0:
            sk = sk + self.noise_sd * rng.standard_normal(N)
        perm = self.order()
        out = {}
        if self.fmt == "1v1":
            a, b = perm[0::2], perm[1::2]
            p = F(sk[a] - sk[b])
            w = (rng.random(a.size) < p).astype(float)
            e = F(self.R[a] - self.R[b])
            d = self.K * (w - e)
            self.R[a] += d
            self.R[b] -= d
            y = np.empty(N); y[a] = w; y[b] = 1 - w
            E = np.empty(N); E[a] = e; E[b] = 1 - e
            P = np.empty(N); P[a] = p; P[b] = 1 - p
            out.update(y=y, E=E, p=P)
        elif self.fmt == "team":
            g = perm.reshape(-1, self.group)
            if self.mm == "random":
                A, B = g[:, :self.team_n], g[:, self.team_n:]
            else:
                A, B = g[:, self.iA], g[:, self.iB]
            if self.team_model == "sum":
                rt = math.sqrt(self.team_n)
                dt = (sk[A].sum(1) - sk[B].sum(1)) / rt
                dr = (self.R[A].sum(1) - self.R[B].sum(1)) / rt
            else:
                dt = sk[A].mean(1) - sk[B].mean(1)
                dr = self.R[A].mean(1) - self.R[B].mean(1)
            p = F(dt)
            w = (rng.random(p.size) < p).astype(float)
            e = F(dr)
            d = self.K * (w - e)
            self.R[A] += d[:, None]
            self.R[B] -= d[:, None]
            y = np.empty(N); y[A] = w[:, None]; y[B] = (1 - w)[:, None]
            E = np.empty(N); E[A] = e[:, None]; E[B] = (1 - e)[:, None]
            P = np.empty(N); P[A] = p[:, None]; P[B] = (1 - p)[:, None]
            out.update(y=y, E=E, p=P)
        else:
            M = self.ffa_n
            g = perm.reshape(-1, M)
            gum = -np.log(-np.log(rng.random(g.shape)))
            perf = sk[g] + GUMBEL_SCALE * gum
            rank = (-perf).argsort(1).argsort(1) + 1
            Rg = self.R[g]
            Sij = (perf[:, :, None] > perf[:, None, :]).astype(float)
            Eij = F(Rg[:, :, None] - Rg[:, None, :])
            idx = np.arange(M)
            Eij[:, idx, idx] = 0.0
            self.R[g] += self.K / (M - 1) * (Sij.sum(2) - Eij.sum(2))
            place = np.empty(N, dtype=np.int8)
            place[g] = rank
            out.update(y=(place == 1).astype(float), place=place,
                       top=(place <= M // 2).astype(float), E=None, p=None)
        if self.ar_sd > 0:
            ph = self.ar_phi
            self.u = ph * self.u + math.sqrt(1 - ph * ph) * self.ar_sd * rng.standard_normal(N)
        return out


def fit_line(s, R):
    """R 对 s 的最小二乘回归：返回 (斜率 λ, 截距, 残差标准差)。"""
    lam, a = np.polyfit(s, R, 1)
    resid = R - (a + lam * s)
    return float(lam), float(a), float(resid.std())


# ---------------------------------------------------------------------------
# 标准实验：3000 轮，前 1000 轮预热，统计第 1001–3000 局
# ---------------------------------------------------------------------------
ROUNDS, BURN = 3000, 1000
N_SEQ = 2000            # 保存逐局结果序列的玩家数（前 N_SEQ 号，彼此独立同分布）
SNAP = (1000, 1400)     # 保存逐轮评分快照的区间（用于误差自相关）

EXPERIMENTS = {
    # 1v1 随机匹配
    "r_k16": dict(fmt="1v1", mm="random", K=16),
    "r_k32": dict(fmt="1v1", mm="random", K=32),
    "r_k16_tau100": dict(fmt="1v1", mm="random", K=16, tau=100.0),
    "r_k16_tau300": dict(fmt="1v1", mm="random", K=16, tau=300.0),
    "r_k16_noise150": dict(fmt="1v1", mm="random", K=16, noise_sd=150.0),
    "r_k16_ar": dict(fmt="1v1", mm="random", K=16, ar_sd=100.0, ar_phi=0.99),
    # 1v1 按分匹配
    "s20_k16": dict(fmt="1v1", mm="sbmm", sigma_q=20, K=16),
    "s50_k16": dict(fmt="1v1", mm="sbmm", sigma_q=50, K=16),
    "s100_k16": dict(fmt="1v1", mm="sbmm", sigma_q=100, K=16),
    "s200_k16": dict(fmt="1v1", mm="sbmm", sigma_q=200, K=16),
    "s20_k32": dict(fmt="1v1", mm="sbmm", sigma_q=20, K=32),
    "s50_k32": dict(fmt="1v1", mm="sbmm", sigma_q=50, K=32),
    "s100_k32": dict(fmt="1v1", mm="sbmm", sigma_q=100, K=32),
    "s200_k32": dict(fmt="1v1", mm="sbmm", sigma_q=200, K=32),
    "s100_k16_noise150": dict(fmt="1v1", mm="sbmm", sigma_q=100, K=16, noise_sd=150.0),
    "s100_k16_ar": dict(fmt="1v1", mm="sbmm", sigma_q=100, K=16, ar_sd=100.0, ar_phi=0.99),
    "s100_k32_ar": dict(fmt="1v1", mm="sbmm", sigma_q=100, K=32, ar_sd=100.0, ar_phi=0.99),
    # 5v5
    "t_r_sum_k16": dict(fmt="team", mm="random", K=16, team_model="sum"),
    "t_r_mean_k16": dict(fmt="team", mm="random", K=16, team_model="mean"),
    "t_s100_sum_k16": dict(fmt="team", mm="sbmm", sigma_q=100, K=16, team_model="sum"),
    "t_s200_sum_k16": dict(fmt="team", mm="sbmm", sigma_q=200, K=16, team_model="sum"),
    "t_s100_mean_k16": dict(fmt="team", mm="sbmm", sigma_q=100, K=16, team_model="mean"),
    # 8 人自由混战
    "f_r_k16": dict(fmt="ffa", mm="random", K=16),
    "f_s100_k16": dict(fmt="ffa", mm="sbmm", sigma_q=100, K=16),
}


def _cache_path(name):
    CACHE.mkdir(parents=True, exist_ok=True)
    return CACHE / f"{name}.npz"


def load_or_run(name, fn, *args, **kw):
    """缓存工具：cache/<name>.npz 存在就读取，否则运行 fn 并保存。"""
    path = _cache_path(name)
    if path.exists():
        with np.load(path, allow_pickle=False) as z:
            return {k: z[k] for k in z.files}
    res = fn(*args, **kw)
    np.savez_compressed(path, **res)
    return res


# 只有这些实验需要逐轮评分快照（误差自相关、状态轨迹），其余不存以减小缓存
SNAP_RUNS = {"r_k16", "r_k32", "s100_k16", "s100_k32", "s200_k16", "s200_k32",
             "s100_k16_ar", "s100_k32_ar", "r_k16_ar"}


def _run_standard(cfg, seed=1, n_players=10000, rounds=ROUNDS, burn=BURN, keep_snaps=True):
    sim = EloSim(n_players=n_players, seed=seed, **cfg)
    N = sim.N
    acc = {k: np.zeros(N) for k in ("wins", "Esum", "psum", "top", "place")}
    seq_y = np.zeros((N_SEQ, rounds - burn), dtype=bool)
    snaps = np.zeros((SNAP[1] - SNAP[0], N_SEQ), dtype=np.float32)
    has_ar = sim.ar_sd > 0
    u_snap = np.zeros((SNAP[1] - SNAP[0], N_SEQ), dtype=np.float32) if has_ar else None
    hot = np.zeros(4)            # [胜场 | u>σ_u, 局数 | u>σ_u, 胜场 | u<-σ_u, 局数 | u<-σ_u]
    checkpoints = np.arange(100, rounds + 1, 100)
    lam_t, resid_t, sdR_t, varR_t = [], [], [], []
    R_burn = None
    for t in range(rounds):
        if t == burn:
            R_burn = sim.R.copy()
        u_before = sim.u.copy() if has_ar else None
        out = sim.step()
        if SNAP[0] <= t < SNAP[1]:
            snaps[t - SNAP[0]] = sim.R[:N_SEQ]
            if has_ar:
                u_snap[t - SNAP[0]] = u_before[:N_SEQ]
        if (t + 1) in checkpoints:
            lam, a, rs = fit_line(sim.s + sim.extra, sim.R)
            lam_t.append(lam); resid_t.append(rs)
            sdR_t.append(float(sim.R.std())); varR_t.append(float(sim.R.var()))
        if t >= burn:
            acc["wins"] += out["y"]
            if out["E"] is not None:
                acc["Esum"] += out["E"]; acc["psum"] += out["p"]
            if sim.fmt == "ffa":
                acc["top"] += out["top"]; acc["place"] += out["place"]
            seq_y[:, t - burn] = out["y"][:N_SEQ] > 0.5
            if has_ar:
                h, c = u_before > sim.ar_sd, u_before < -sim.ar_sd
                hot += [out["y"][h].sum(), h.sum(), out["y"][c].sum(), c.sum()]
    T = rounds - burn
    # 缓存体积：逐局结果按位打包，评分快照存为相对 1500 的 float16（精度约 1 分，远小于 σ_e）
    res = dict(s=sim.s, R_end=sim.R, R_burn=R_burn, games=np.array(T),
               W=acc["wins"] / T, Ebar=acc["Esum"] / T, pbar=acc["psum"] / T,
               top=acc["top"] / T, place=acc["place"] / T,
               seq_y_packed=np.packbits(seq_y, axis=1), seq_len=np.array(T),
               checkpoints=checkpoints,
               lam_t=np.array(lam_t), resid_t=np.array(resid_t), sdR_t=np.array(sdR_t),
               varR_t=np.array(varR_t), K=np.array(sim.K))
    if keep_snaps:
        res["snaps16"] = (snaps - 1500.0).astype(np.float16)
    if has_ar:
        res["u_snap16"] = u_snap.astype(np.float16)
        res["hot_cold"] = hot
    return res


def get(name):
    """读取（或运行并缓存）一个标准实验，并把压缩存储的数组还原：
    seq_y（前 N_SEQ 人第 1001–3000 局的胜负，int8）、snaps（第 1001–1400 轮的评分）、
    u_snap（同期的状态 u，仅 AR 实验）、hot_cold（u>σ_u / u<-σ_u 时的胜场与局数）。"""
    r = load_or_run(name, _run_standard, EXPERIMENTS[name], keep_snaps=name in SNAP_RUNS)
    if "seq_y" not in r:
        r["seq_y"] = np.unpackbits(r["seq_y_packed"], axis=1)[:, :int(r["seq_len"])].astype(np.int8)
        if "snaps16" in r:
            r["snaps"] = r["snaps16"].astype(np.float64) + 1500.0
        if "u_snap16" in r:
            r["u_snap"] = r["u_snap16"].astype(np.float64)
    return r


# ---------------------------------------------------------------------------
# 常用统计量
# ---------------------------------------------------------------------------
def deciles(x):
    q = np.quantile(x, np.linspace(0, 1, 11))
    return np.clip(np.searchsorted(q, x, side="right") - 1, 0, 9)


def by_decile(x, v):
    d = deciles(x)
    return np.array([v[d == k].mean() for k in range(10)])


def window_var_ratio(seq_y, n):
    """逐人把结果序列切成长度 n 的不重叠窗口，计算窗口胜率的人内方差（ddof=1）
    与二项方差 p̂(1-p̂)/n 之比，再对人取平均。"""
    T = seq_y.shape[1] // n * n
    w = seq_y[:, :T].reshape(seq_y.shape[0], -1, n).mean(2)
    p = seq_y[:, :T].mean(1)
    ok = (p > 0.02) & (p < 0.98)
    v = w.var(1, ddof=1)
    return float(np.mean(v[ok] / (p[ok] * (1 - p[ok]) / n)))


def error_autocorr(snaps, s, lags):
    """评分误差（相对评分-实力回归线）的自相关，snaps 形状 (时间, 人)。"""
    e = np.empty_like(snaps, dtype=float)
    for i in range(snaps.shape[0]):
        lam, a = np.polyfit(s, snaps[i], 1)
        e[i] = snaps[i] - (a + lam * s)
    # 不做逐人去均值：误差已相对每轮的横截面回归线计算；逐人去均值会在 400 轮窗口内使自相关系统性偏低
    v = (e * e).mean()
    return np.array([(e[:e.shape[0] - L] * e[L:]).mean() / v if L > 0 else 1.0 for L in lags])


def efold(lags, acf):
    """自相关首次降到 1/e 的滞后（线性插值）。"""
    target = math.exp(-1)
    for i in range(1, len(lags)):
        if acf[i] <= target:
            x0, x1, y0, y1 = lags[i - 1], lags[i], acf[i - 1], acf[i]
            return x0 + (y0 - target) * (x1 - x0) / (y0 - y1)
    return float("nan")


# ---------------------------------------------------------------------------
# 专门实验
# ---------------------------------------------------------------------------
def _run_k_sweep(Ks=(8, 16, 24, 32, 48, 64), sigmas=(None, 200, 100), n_players=4000,
                 rounds=2500, burn=1000, seed=3):
    """稳态评分误差随 K 的变化：每 50 轮取一次残差标准差（相对回归线），对预热后取平均。"""
    out = {"Ks": np.array(Ks, float)}
    for sq in sigmas:
        key = "random" if sq is None else f"s{sq}"
        res, lams = [], []
        for K in Ks:
            cfg = dict(fmt="1v1", K=K, mm="random") if sq is None else \
                dict(fmt="1v1", K=K, mm="sbmm", sigma_q=sq)
            sim = EloSim(n_players=n_players, seed=seed, **cfg)
            rs, ls = [], []
            for t in range(rounds):
                sim.step()
                if t >= burn and (t + 1) % 50 == 0:
                    lam, a, r = fit_line(sim.s, sim.R)
                    rs.append(r); ls.append(lam)
            res.append(np.mean(rs)); lams.append(np.mean(ls))
        out[f"resid_{key}"] = np.array(res)
        out[f"lam_{key}"] = np.array(lams)
    return out


def k_sweep():
    return load_or_run("k_sweep", _run_k_sweep)


def _run_reset(mm, K, sigma_q=100.0, n_players=10000, burn=1000, follow=400, n_reset=500, seed=7):
    """系统平稳后，把 n_reset 名前 10% 实力玩家的评分重置为 1500，跟踪其后 follow 局。
    差距（实力分）= s - (R - a_t)/λ_t，(a_t, λ_t) 每轮在未重置玩家上重新拟合（移动目标）。"""
    sim = EloSim(n_players=n_players, K=K, fmt="1v1", mm=mm, sigma_q=sigma_q, seed=seed)
    for _ in range(burn):
        sim.step()
    top = np.where(sim.s >= np.quantile(sim.s, 0.9))[0]
    cohort = sim.rng.choice(top, n_reset, replace=False)
    others = np.setdiff1d(np.arange(n_players), cohort)
    sim.R[cohort] = 1500.0
    gap, gap_frozen, win, Ec = [], [], [], []
    lam0, a0 = np.polyfit(sim.s[others], sim.R[others], 1)
    for t in range(follow + 1):
        lam, a = np.polyfit(sim.s[others], sim.R[others], 1)
        gap.append(np.mean(sim.s[cohort] - (sim.R[cohort] - a) / lam))
        gap_frozen.append(np.mean(sim.s[cohort] - (sim.R[cohort] - a0) / lam0))
        if t == follow:
            break
        out = sim.step()
        win.append(out["y"][cohort].mean())
        Ec.append(out["E"][cohort].mean())
    return dict(gap=np.array(gap), gap_frozen=np.array(gap_frozen), win=np.array(win),
                E=np.array(Ec), s_cohort=np.array(sim.s[cohort].mean()))


def reset_runs():
    runs = {}
    for mm, K in (("sbmm", 16), ("sbmm", 32), ("random", 16), ("random", 32)):
        runs[(mm, K)] = load_or_run(f"reset_{mm}_k{K}", _run_reset, mm, K)
    return runs


def closure_time(gap, frac):
    """差距缩小到初值的 (1-frac) 所需局数（首次达到）。"""
    target = gap[0] * (1 - frac)
    idx = np.where(gap <= target)[0]
    return int(idx[0]) if idx.size else -1


def _run_stretch(sigma_q, K=16, n_players=2000, rounds=10000, seed=11, every=100):
    """严格按分匹配下评分刻度 λ(t)：初始评分 = 真实实力（λ0 = 1）。"""
    sim = EloSim(n_players=n_players, K=K, fmt="1v1", mm="sbmm", sigma_q=sigma_q, init="true", seed=seed)
    ts, lam, var = [0], [1.0], [float(sim.R.var())]
    for t in range(rounds):
        sim.step()
        if (t + 1) % every == 0:
            l, a, r = fit_line(sim.s, sim.R)
            ts.append(t + 1); lam.append(l); var.append(float(sim.R.var()))
    return dict(t=np.array(ts), lam=np.array(lam), varR=np.array(var), var0=np.array(var[0]))


def stretch_runs(sigmas=(20, 50, 100, 200), K=16):
    return {sq: load_or_run(f"stretch_k{K}_s{sq}", _run_stretch, sq, K) for sq in sigmas}


def _run_improve(v, K, mm="sbmm", sigma_q=100.0, n_players=10000, burn=1000, total=300.0, after=200,
                 frac=0.02, seed=5):
    """2% 玩家（随机抽取）在 total/v 局内每局实力 +v（共 +total），之后停止。
    取 2% 而不是更多，是为了让进步者很少互相匹配（互相对局时零和更新不给群体净分）。"""
    sim = EloSim(n_players=n_players, K=K, fmt="1v1", mm=mm, sigma_q=sigma_q, seed=seed)
    for _ in range(burn):
        sim.step()
    imp = sim.rng.choice(n_players, int(frac * n_players), replace=False)
    others = np.setdiff1d(np.arange(n_players), imp)
    ramp = int(round(total / v))
    W = []; E = []; lag = []; Rm = []
    for t in range(ramp + after):
        if t < ramp:
            sim.extra[imp] += v
        out = sim.step()
        W.append(out["y"][imp].mean()); E.append(out["E"][imp].mean())
        lam, a = np.polyfit(sim.s[others], sim.R[others], 1)
        lag.append(np.mean(sim.s[imp] + sim.extra[imp] - (sim.R[imp] - a) / lam))
        Rm.append(sim.R[imp].mean())
    lam, a = np.polyfit(sim.s[others], sim.R[others], 1)
    return dict(W=np.array(W), E=np.array(E), lag=np.array(lag), Rmean=np.array(Rm),
                lam=np.array(lam), v=np.array(v), K=np.array(K), ramp=np.array(ramp))


def improve_runs(vs=(0.25, 0.5, 1.0), Ks=(16, 32)):
    return {(v, K): load_or_run(f"improve_v{v}_k{K}", _run_improve, v, K) for v in vs for K in Ks}


# ---------------------------------------------------------------------------
# 实力波动：AR(1) 状态与窗口胜率的过度离散（推导见附录 app:ch2-ar1）
# ---------------------------------------------------------------------------
def ar1_mean_var(n, phi, sigma_u):
    """AR(1)（平稳方差 σ_u²）连续 n 局均值的方差。"""
    n = np.asarray(n, dtype=float)
    return sigma_u ** 2 / n * ((1 + phi) / (1 - phi) - 2 * phi * (1 - phi ** n) / (n * (1 - phi) ** 2))


def filtered_acov(k, alpha, phi, sigma_u):
    """x_t = (1-α)x_{t-1} + α u_t（指数平滑），u 为 AR(1)。返回 x 的自协方差 γ_x(k)。"""
    a = 1.0 - alpha
    k = np.asarray(k, dtype=float)
    g0 = alpha ** 2 * sigma_u ** 2 * (1 + a * phi) / ((1 - a ** 2) * (1 - a * phi))
    return a ** k * g0 + alpha ** 2 * sigma_u ** 2 / (1 - a * phi) * (phi ** k - a ** k) * phi / (phi - a)


def absorbed_share(alpha, phi):
    """评分（指数平滑）对当前状态 u_t 的回归系数 Cov(x_t, u_t)/σ_u² = α/(1-(1-α)φ)。"""
    return alpha / (1 - (1 - alpha) * phi)


def _sample_var_factor(D, n, mwin):
    """把"窗口增量方差" D(h) 换成 m 个连续窗口的人内样本方差期望。"""
    return mwin / (mwin - 1) * (D(n) - D(mwin * n) / mwin ** 2)


def var_ratio_sbmm(n, K, sigma_q, T=2000, ar_sd=0.0, ar_phi=0.99, tau=TAU):
    """按分匹配下 n 局窗口胜率方差 / 二项方差的近似（恒等式 W_n = Ē_n + ΔR/(Kn)）：
    比值 ≈ 4 Var(E_t) + 4 E[s²(ΔR)]/(K² n)，ΔR 的自协方差 = λ²γ_x(k) + σ_e²(1-α)^k，α = 1/τ_R。"""
    lam = float(lambda_star(K, sigma_q))
    se2 = sigma_e(K, lam) ** 2
    sR2 = lam ** 2 * tau ** 2 + se2
    g = sR2 / (sR2 + sigma_q ** 2)
    vE = float(gauss_expect(lambda x: F(x) ** 2, 0.0, math.sqrt(g * (1 + g)) * sigma_q)) - 0.25
    alpha = 1.0 / tau_R_meanfield(K, sigma_q)

    def Gam(k):
        out = se2 * (1 - alpha) ** np.asarray(k, dtype=float)
        if ar_sd > 0:
            out = out + lam ** 2 * filtered_acov(k, alpha, ar_phi, ar_sd)
        return out

    D = lambda h: 2 * (Gam(0) - Gam(h))
    n = np.asarray(n, dtype=float)
    mwin = T / n
    return 4 * vE + 4 * _sample_var_factor(D, n, mwin) / (K ** 2 * n)


def var_ratio_random_ar(n, ar_sd, ar_phi=0.99, T=2000, tau=TAU):
    """随机匹配 + AR(1) 状态：比值 ≈ 1 + n β²/(p(1-p)) · E[窗口均值样本方差]，对实力分布取平均。"""
    z = PhiInv((np.arange(2000) + 0.5) / 2000)
    d = tau * z
    h = 0.5
    sd_opp = math.sqrt(tau ** 2 + ar_sd ** 2)
    beta = (gauss_expect(F, d + h, sd_opp) - gauss_expect(F, d - h, sd_opp)) / (2 * h)
    p = gauss_expect(F, d, math.sqrt(tau ** 2 + 2 * ar_sd ** 2))
    k = np.mean(beta ** 2 / (p * (1 - p)))
    n = np.asarray(n, dtype=float)
    mwin = T / n
    Vw = mwin / (mwin - 1) * (ar1_mean_var(n, ar_phi, ar_sd) - ar1_mean_var(mwin * n, ar_phi, ar_sd))
    return 1 + k * n * Vw


def improve_cohort10_runs(v=0.5, Ks=(16, 32)):
    """对照：10% 玩家同时进步（进步者彼此对局更频繁），其余同 improve_runs。"""
    return {K: load_or_run(f"improve10_v{v}_k{K}", _run_improve, v, K, frac=0.1) for K in Ks}
