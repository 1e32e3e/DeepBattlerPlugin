#!/usr/bin/env python3
"""Independent analytic + Monte-Carlo verification of winrate_math.md (written from scratch;
winrate_sim.py was NOT consulted).  Usage:  python3 vsim.py EXPERIMENT [EXPERIMENT ...]
All experiments are single-process, vectorised numpy, N = 2000-4000 players.
Experiments: analytic random sbmm stretch ode trueskill tau team ffa form j0 reset_frozen reset_seeds misc"""
import sys
import time
import numpy as np
from scipy.special import ndtr

LN10 = np.log(10.0)
C = LN10 / 1600.0           # slope of Elo logistic at 0
MU, TAU = 1500.0, 200.0
GUMBEL_SCALE = 400.0 / LN10  # Gumbel performance noise -> pairwise Elo logistic


def F(d):
    return 1.0 / (1.0 + np.power(10.0, -np.asarray(d) / 400.0))


def out(msg=""):
    print(msg, flush=True)


# ----------------------------------------------------------------------------- pairing
def pair_order(R, rng, mode, jitter=0.0, block=2):
    """Return a permutation; consecutive pairs (or groups) of it play each other.
    random : uniform random
    sbmm   : sort by R + N(0, jitter^2), random tie-break
    sbmm_idx: same but deterministic tie-break by player index (artifact test)
    block  : sort by R (random tie-break), then shuffle inside consecutive blocks of size
             `block` whose boundaries move randomly each round (a hard 'window' model)"""
    N = R.size
    if mode == "random":
        return rng.permutation(N)
    key = R + jitter * rng.standard_normal(N) if jitter > 0 else R
    if mode == "sbmm_idx":
        return np.argsort(key, kind="stable")
    order = np.lexsort((rng.random(N), key))
    if mode == "sbmm":
        return order
    if mode == "block":
        off = rng.integers(0, block)
        bid = (np.arange(N) + off) // block
        return order[np.lexsort((rng.random(N), bid))]
    raise ValueError(mode)


def line_fit(s, R):
    lam = np.cov(R, s)[0, 1] / np.var(s, ddof=1)
    a = R.mean() - lam * s.mean()
    resid = R - (a + lam * s)
    return lam, a, resid.std(), np.corrcoef(R, s)[0, 1]


def ranks01(x):
    r = np.empty(x.size)
    r[np.argsort(x)] = np.arange(x.size)
    return r / x.size


def decile_rows(s, cols):
    """cols: dict name->per-player array. Returns list of (decile, mean s, {name: mean})."""
    q = ranks01(s)
    d = np.minimum((q * 10).astype(int), 9)
    rows = []
    for k in range(10):
        m = d == k
        rows.append((k + 1, s[m].mean(), {n: v[m].mean() for n, v in cols.items()}))
    top1 = q >= 0.99
    bot1 = q < 0.01
    return rows, {n: (v[top1].mean(), v[bot1].mean()) for n, v in cols.items()}


# ----------------------------------------------------------------------------- 1v1 engine
def sim_1v1(N=4000, K=16.0, rounds=3000, burn=1000, mode="random", jitter=0.0, block=2,
            seed=1, init="mean", form=None, sx=0.0, su=100.0, phi=0.99,
            checkpoints=(250, 500, 1000, 2000, 3000), store_outcomes=False,
            e_autocorr=None, churn=0.0, verbose=True):
    rng = np.random.default_rng(seed)
    s = MU + TAU * rng.standard_normal(N)
    if init == "mean":
        R = np.full(N, MU)
    elif init == "skill":
        R = s.copy()
    else:  # numeric: start at MU + init * N(0,1) (uncorrelated with skill)
        R = MU + float(init) * rng.standard_normal(N)
    age = np.zeros(N)
    u = su * rng.standard_normal(N) if form == "ar1" else np.zeros(N)
    T = rounds - burn
    wins = np.zeros(N)
    Esum = np.zeros(N)
    nwin = T // 100
    winwin = np.zeros((N, max(nwin, 1)))
    outc = np.zeros((N, T), dtype=np.int8) if store_outcomes else None
    hot_w = hot_n = cold_w = cold_n = 0.0
    absorb_num = absorb_den = 0.0
    R0 = None
    cps = {}
    Splayer = np.empty(N)
    Eplayer = np.empty(N)
    esnap = []
    varR_hist = []
    for t in range(rounds):
        if t == burn:
            R0 = R.copy()
        if form == "ar1":
            sk = s + u
        elif form == "iid":
            sk = s + sx * rng.standard_normal(N)
        else:
            sk = s
        order = pair_order(R, rng, mode, jitter, block)
        a, b = order[0::2], order[1::2]
        P = F(sk[a] - sk[b])
        S = (rng.random(a.size) < P).astype(float)
        E = F(R[a] - R[b])
        dlt = K * (S - E)
        R[a] += dlt
        R[b] -= dlt
        age += 1
        if t >= burn:
            Splayer[a] = S
            Splayer[b] = 1.0 - S
            Eplayer[a] = E
            Eplayer[b] = 1.0 - E
            wins += Splayer
            Esum += Eplayer
            w = (t - burn) // 100
            if w < nwin:
                winwin[:, w] += Splayer
            if store_outcomes:
                outc[:, t - burn] = Splayer.astype(np.int8)
            if form == "ar1":
                h = u > su
                cdm = u < -su
                hot_w += Splayer[h].sum()
                hot_n += h.sum()
                cold_w += Splayer[cdm].sum()
                cold_n += cdm.sum()
                if (t - burn) % 10 == 0:
                    lam, a0, _, _ = line_fit(s, R)
                    res = R - (a0 + lam * s)
                    absorb_num += np.dot(res, u) / lam
                    absorb_den += np.dot(u, u)
        if e_autocorr is not None and e_autocorr[0] <= t < e_autocorr[1]:
            lam, a0, _, _ = line_fit(s, R)
            esnap.append((R - (a0 + lam * s)).astype(np.float32))
        if form == "ar1":
            u = phi * u + np.sqrt(1 - phi * phi) * su * rng.standard_normal(N)
        if churn > 0:
            gone = rng.random(N) < churn
            k = gone.sum()
            if k:
                s[gone] = MU + TAU * rng.standard_normal(k)
                R[gone] = MU
                age[gone] = 0
        if (t + 1) in checkpoints:
            if churn > 0:
                m = age > 300
                cps[t + 1] = line_fit(s[m], R[m]) + (R.std(), R.mean())
            else:
                cps[t + 1] = line_fit(s, R) + (R.std(), R.mean())
        varR_hist.append(R.var())
    res = dict(s=s, R=R, cps=cps, varR=np.array(varR_hist))
    if T > 0:
        W = wins / T
        Eb = Esum / T
        dRterm = (R - R0) / (K * T)
        res.update(W=W, E=Eb, dRterm=dRterm,
                   identity_maxerr=np.max(np.abs(W - (Eb + dRterm))))
        p = W
        varw = (winwin[:, :nwin] / 100.0).var(axis=1, ddof=1)
        binom = p * (1 - p) / 100.0
        res["var_ratio"] = varw.sum() / binom.sum()
        res["share60"] = (winwin[:, :nwin] >= 60).mean()
        res["sdW"] = W.std()
    if form == "ar1" and T > 0:
        res["hot"] = hot_w / max(hot_n, 1)
        res["cold"] = cold_w / max(cold_n, 1)
        res["absorbed"] = absorb_num / absorb_den
    if store_outcomes:
        x = outc.astype(np.float32)
        x -= x.mean(axis=1, keepdims=True)
        den = (x * x).sum()
        res["acf"] = {k: float((x[:, :-k] * x[:, k:]).sum() / den) for k in (1, 5, 20)}
    if esnap:
        Es = np.array(esnap)  # (L, N)
        acf = {}
        for k in (5, 10, 20, 30, 40, 50, 60, 80, 100, 150):
            if k < len(Es):
                x0, x1 = Es[:-k].ravel(), Es[k:].ravel()
                acf[k] = float(np.corrcoef(x0, x1)[0, 1])
        res["e_acf"] = acf
    return res


def fmt_cps(cps):
    return " ".join(f"t{t}:{v[0]:.2f}({v[2]:.0f})" for t, v in sorted(cps.items()))


def report_1v1(name, r, show_deciles=True):
    out(f"\n### {name}")
    if "W" in r:
        rows, ext = decile_rows(r["s"], {"W": r["W"], "E": r["E"], "dR": r["dRterm"]})
        if show_deciles:
            out("| dec | mean s | W | E | dR/(KT) pp |")
            out("|---|---|---|---|---|")
            for k, ms, v in rows:
                out(f"| {k} | {ms:.0f} | {100*v['W']:.1f}% | {100*v['E']:.1f}% | {100*v['dR']:+.2f} |")
        out(f"decile range {100*rows[0][2]['W']:.1f}%-{100*rows[-1][2]['W']:.1f}%; top1% {100*ext['W'][0]:.1f}%, bottom1% {100*ext['W'][1]:.1f}%; "
            f"sd indiv W {100*r['sdW']:.2f}pp; identity max err {r['identity_maxerr']:.1e}; "
            f"100-game var/binom {r['var_ratio']:.2f}; share windows>=60% {100*r['share60']:.1f}%")
    out("slope(resid sd): " + fmt_cps(r["cps"]))
    lam, a, rsd, corr = line_fit(r["s"], r["R"])
    out(f"final: slope {lam:.3f}, resid sd {rsd:.1f}, raw sd(R-s) {np.std(r['R']-r['s']):.1f}, corr {corr:.3f}, mean R {r['R'].mean():.2f}")
    for k in ("hot", "cold", "absorbed"):
        if k in r:
            out(f"{k}: {r[k]:.3f}")
    if "acf" in r:
        out("outcome acf lag1/5/20: " + " / ".join(f"{v:.4f}" for v in r["acf"].values()))
    if "e_acf" in r:
        out("rating-error acf: " + " ".join(f"k{k}:{v:.3f}" for k, v in r["e_acf"].items()))


# ----------------------------------------------------------------------------- reset / improvement
def sim_reset(N=4000, K=16.0, mode="sbmm", jitter=100.0, seed=7, pre=1000, post=400, nreset=200):
    rng = np.random.default_rng(seed)
    s = MU + TAU * rng.standard_normal(N)
    R = np.full(N, MU)

    def play(R):
        order = pair_order(R, rng, mode, jitter)
        a, b = order[0::2], order[1::2]
        S = (rng.random(a.size) < F(s[a] - s[b])).astype(float)
        dlt = K * (S - F(R[a] - R[b]))
        R[a] += dlt
        R[b] -= dlt
        Sp = np.empty(N)
        Sp[a] = S
        Sp[b] = 1 - S
        return Sp

    for _ in range(pre):
        play(R)
    q = ranks01(s)
    top = np.where(q >= 0.9)[0]
    sel = rng.choice(top, nreset, replace=False)
    others = np.setdiff1d(np.arange(N), sel)
    R[sel] = MU
    gaps = []
    wr = []
    for t in range(post + 1):
        lam, a0, _, _ = line_fit(s[others], R[others])
        gaps.append(np.mean(s[sel] - (R[sel] - a0) / lam))
        if t < post:
            Sp = play(R)
            wr.append(Sp[sel].mean())
    gaps = np.array(gaps)
    wr = np.array(wr)
    g0 = gaps[0]
    half = int(np.argmax(gaps <= 0.5 * g0))
    ninety = int(np.argmax(gaps <= 0.1 * g0)) if (gaps <= 0.1 * g0).any() else -1
    return dict(g0=g0, half=half, ninety=ninety, w50=wr[:50].mean(), w100=wr[:100].mean(),
                w300=wr[300:400].mean(), lam=lam)


def sim_improve(N=4000, K=16.0, mode="sbmm", jitter=100.0, seed=11, pre=1000, ramp=600, v=0.5, frac=0.1, after=200):
    rng = np.random.default_rng(seed)
    s = MU + TAU * rng.standard_normal(N)
    R = np.full(N, MU)
    for t in range(pre + ramp + after):
        if t == pre:
            sel = rng.choice(N, int(frac * N), replace=False)
            others = np.setdiff1d(np.arange(N), sel)
            Wsum = Esum = 0.0
            nG = 0
            lags = []
            Rstart = None
            Wa = Ea = 0.0
            w100 = 0.0
        if pre <= t < pre + ramp:
            s[sel] += v
        order = pair_order(R, rng, mode, jitter)
        a, b = order[0::2], order[1::2]
        S = (rng.random(a.size) < F(s[a] - s[b])).astype(float)
        E = F(R[a] - R[b])
        dlt = K * (S - E)
        R[a] += dlt
        R[b] -= dlt
        if t >= pre:
            Sp = np.empty(N)
            Sp[a] = S
            Sp[b] = 1 - S
            Ep = np.empty(N)
            Ep[a] = E
            Ep[b] = 1 - E
            g = t - pre
            if g < 100:
                w100 += Sp[sel].mean() / 100
            if g == 100:
                Rstart = R[sel].copy()  # after game index 100 -> window games 101..600
            if 100 < g < ramp:
                Wsum += Sp[sel].mean()
                Esum += Ep[sel].mean()
                nG += 1
                if g % 20 == 0:
                    lam, a0, _, _ = line_fit(s[others], R[others])
                    lags.append((np.mean(s[sel]) - np.mean((R[sel] - a0) / lam), lam))
            if g == ramp - 1:
                drift = np.mean(R[sel] - Rstart) / nG
                lam_end = line_fit(s[others], R[others])[0]
            if g >= ramp:
                Wa += Sp[sel].mean() / after
                Ea += Ep[sel].mean() / after
    lagv = np.mean([x[0] for x in lags])
    lamv = np.mean([x[1] for x in lags])
    return dict(w100=w100, W=Wsum / nG, E=Esum / nG, WmE=(Wsum - Esum) / nG, drift=drift,
                drift_over_K=drift / K, lam=lamv, lam_end=lam_end, lag=lagv,
                theory_WmE=lamv * v / K, theory_lag=lamv * v / (K * C), Wafter=Wa, Eafter=Ea)


# ----------------------------------------------------------------------------- teams
def sim_team(N=4000, n=5, K=16.0, rounds=3000, burn=1000, mode="random", jitter=100.0,
             model="sum", seed=21, upd="consistent"):
    rng = np.random.default_rng(seed)
    s = MU + TAU * rng.standard_normal(N)
    R = np.full(N, MU)
    G = 2 * n
    assert N % G == 0
    scale = np.sqrt(n) if model == "sum" else float(n)
    if mode == "random":
        posA = np.arange(n)
        posB = np.arange(n, G)
    else:  # snake draft on sorted (ascending) group
        A_, B_ = [], []
        for j in range(G):
            k, r = divmod(j, 2)
            (A_ if (r == 0) == (k % 2 == 0) else B_).append(j)
        posA, posB = np.array(A_), np.array(B_)
    T = rounds - burn
    wins = np.zeros(N)
    Esum = np.zeros(N)
    winwin = np.zeros((N, T // 100))
    cps = {}
    for t in range(rounds):
        if t == burn:
            R0 = R.copy()
        order = pair_order(R, rng, mode, jitter)
        g = order.reshape(-1, G)
        A, B = g[:, posA], g[:, posB]
        P = F((s[A].sum(1) - s[B].sum(1)) / scale)
        S = (rng.random(P.size) < P).astype(float)
        if upd == "consistent":
            E = F((R[A].sum(1) - R[B].sum(1)) / scale)
        else:  # 'mean': Elo on team mean rating regardless of outcome model
            E = F((R[A].sum(1) - R[B].sum(1)) / n)
        d = K * (S - E)
        R[A] += d[:, None]
        R[B] -= d[:, None]
        if t >= burn:
            Sp = np.empty(N)
            Ep = np.empty(N)
            Sp[A] = S[:, None]
            Sp[B] = 1 - S[:, None]
            Ep[A] = E[:, None]
            Ep[B] = 1 - E[:, None]
            wins += Sp
            Esum += Ep
            winwin[:, (t - burn) // 100] += Sp
        if (t + 1) in (1000, 2000, 3000):
            cps[t + 1] = line_fit(s, R) + (R.std(), R.mean())
    W = wins / T
    varw = (winwin / 100).var(axis=1, ddof=1)
    return dict(s=s, R=R, W=W, E=Esum / T, dRterm=(R - R0) / (K * T), cps=cps,
                identity_maxerr=np.max(np.abs(W - (Esum / T + (R - R0) / (K * T)))),
                var_ratio=varw.sum() / (W * (1 - W) / 100).sum(), share60=(winwin >= 60).mean(),
                sdW=W.std())


# ----------------------------------------------------------------------------- FFA
def sim_ffa(N=4000, M=8, K=16.0, rounds=3000, burn=1000, mode="random", jitter=100.0, seed=31):
    rng = np.random.default_rng(seed)
    s = MU + TAU * rng.standard_normal(N)
    R = np.full(N, MU)
    T = rounds - burn
    first = np.zeros(N)
    top4 = np.zeros(N)
    place_sum = np.zeros(N)
    eye = np.eye(M, dtype=bool)
    for t in range(rounds):
        order = pair_order(R, rng, mode, jitter)
        g = order.reshape(-1, M)
        perf = s[g] + rng.gumbel(0.0, GUMBEL_SCALE, g.shape)
        Sij = (perf[:, :, None] > perf[:, None, :]).astype(float)
        Rg = R[g]
        Eij = F(Rg[:, :, None] - Rg[:, None, :])
        D = np.where(eye, 0.0, Sij - Eij).sum(2)
        R[g] += K / (M - 1) * D
        if t >= burn:
            place = (M - 1) - Sij.sum(2)  # 0 = first
            first[g] += place == 0
            top4[g] += place < 4
            place_sum[g] += place + 1
    lam, a, rsd, corr = line_fit(s, R)
    return dict(s=s, R=R, first=first / T, top4=top4 / T, place=place_sum / T, lam=lam, rsd=rsd, corr=corr)


# ----------------------------------------------------------------------------- TrueSkill 1v1 (Thurstone truth)
def sim_trueskill(N=4000, rounds=6000, mode="sbmm", jitter=20.0, tau_dyn=None, seed=41,
                  checkpoints=(1000, 2000, 3000, 6000, 10000), sigma0=None):
    """TrueSkill-style Gaussian filter in Elo-like units.  Truth: P = Phi((s_i-s_j)/(sqrt2*beta)),
    beta = 295.7/sqrt2 (same slope as Elo).  mu0=1500, sigma0=2*beta (Xbox ratio), tau_dyn=sigma0/100."""
    rng = np.random.default_rng(seed)
    beta = 1.702 * 400 / LN10 / np.sqrt(2)
    s = MU + TAU * rng.standard_normal(N)
    m = np.full(N, MU)
    if sigma0 is None:
        sigma0 = 2 * beta
    sig2 = np.full(N, sigma0 ** 2)
    if tau_dyn is None:
        tau_dyn = sigma0 / 100
    cps = {}
    for t in range(rounds):
        sig2 += tau_dyn ** 2
        order = pair_order(m, rng, mode, jitter)
        a, b = order[0::2], order[1::2]
        S = rng.random(a.size) < ndtr((s[a] - s[b]) / (np.sqrt(2) * beta))
        w = np.where(S, a, b)
        l = np.where(S, b, a)
        c2 = 2 * beta ** 2 + sig2[w] + sig2[l]
        c = np.sqrt(c2)
        x = (m[w] - m[l]) / c
        v = np.exp(-0.5 * x * x) / np.sqrt(2 * np.pi) / np.maximum(ndtr(x), 1e-300)
        ww = v * (v + x)
        m[w] += sig2[w] / c * v
        m[l] -= sig2[l] / c * v
        sig2[w] *= np.maximum(1 - sig2[w] / c2 * ww, 1e-6)
        sig2[l] *= np.maximum(1 - sig2[l] / c2 * ww, 1e-6)
        if (t + 1) in checkpoints:
            cps[t + 1] = line_fit(s, m) + (np.sqrt(sig2.mean()), m.std())
    return cps


# ----------------------------------------------------------------------------- experiments
def exp_analytic():
    """Analytic checks (closed forms, quadrature, small MC)."""
    from scipy import stats, optimize

    LN10 = np.log(10.0)
    c = LN10 / 1600.0  # slope of Elo logistic at 0


    def F(d):
        return 1.0 / (1.0 + 10.0 ** (-np.asarray(d) / 400.0))


    mu, tau = 1500.0, 200.0
    sig_d = 1.702 * 400 / LN10
    print("== constants ==")
    print(f"c = {c:.7f}; sigma_d(probit approx) = {sig_d:.2f}; Elo normal 200*sqrt2 = {200*np.sqrt(2):.1f}")
    print("F(100,200,300,400,800) =", [f"{F(x):.4f}" for x in (100, 200, 300, 400, 800)])
    print(f"Phi(200/283)={stats.norm.cdf(200/282.84):.4f}  Phi(400/283)={stats.norm.cdf(400/282.84):.4f}")
    # best probit scale matching logistic in least squares over typical differences
    xs = np.linspace(-800, 800, 4001)
    best = optimize.minimize_scalar(lambda s: np.sum((F(xs) - stats.norm.cdf(xs / s)) ** 2), bounds=(200, 400), method="bounded")
    print(f"LS-best probit scale for F over |d|<=800: {best.x:.1f}; max |F - Phi(d/295.7)| = {np.max(np.abs(F(xs)-stats.norm.cdf(xs/sig_d))):.4f}")

    # ---------- Random matching 1v1 -------------
    gh_x, gh_w = np.polynomial.hermite_e.hermegauss(200)  # probabilists' Hermite
    gh_w = gh_w / gh_w.sum()


    def W_exact(s, tau=tau, extra_var=0.0):
        """Exact win prob vs random opponent t~N(mu,tau^2), logistic F, optional extra gaussian noise var on the diff."""
        sd = np.sqrt(tau ** 2 + extra_var)
        return np.sum(gh_w * F(np.asarray(s)[..., None] - (mu + sd * gh_x)), axis=-1)


    rho = tau / np.sqrt(tau ** 2 + sig_d ** 2)
    print(f"\n== Q2 random 1v1: rho = {rho:.4f}, rho^2 = {rho**2:.3f}")


    def decile_mean(fun, lo_q, hi_q, n=4001):
        z = np.linspace(stats.norm.ppf(max(lo_q, 1e-9)), stats.norm.ppf(min(hi_q, 1 - 1e-9)), n)
        w = stats.norm.pdf(z)
        return np.trapezoid(fun(z) * w, z) / np.trapezoid(w, z)


    rows = []
    for d in range(10):
        lo, hi = d / 10, (d + 1) / 10
        ez = decile_mean(lambda z: z, lo, hi)
        at_mean = stats.norm.cdf(rho * ez)
        avg_probit = decile_mean(lambda z: stats.norm.cdf(rho * z), lo, hi)
        avg_exact = decile_mean(lambda z: W_exact(mu + tau * z), lo, hi)
        rows.append((d + 1, ez, at_mean, avg_probit, avg_exact))
    print("decile | E[z] | Phi(rho*E[z]) (note's 'formula') | decile-avg Phi(rho z) | decile-avg exact logistic")
    for r in rows:
        print(f"{r[0]:2d} | {r[1]:+.3f} | {100*r[2]:.1f}% | {100*r[3]:.1f}% | {100*r[4]:.1f}%")
    for lo, hi, name in ((0.99, 1.0, "top1%"), (0.0, 0.01, "bottom1%")):
        ez = decile_mean(lambda z: z, lo, hi)
        print(f"{name}: E[z]={ez:.3f}  Phi(rho E z)={100*stats.norm.cdf(rho*ez):.1f}%  avg probit={100*decile_mean(lambda z: stats.norm.cdf(rho*z), lo, hi):.1f}%  avg exact={100*decile_mean(lambda z: W_exact(mu+tau*z), lo, hi):.1f}%")

    print("\n tau table (note uses Phi(rho*E[z]); also decile-average exact logistic)")
    for t in (100, 150, 200, 300, 400):
        r = t / np.sqrt(t ** 2 + sig_d ** 2)
        p75 = stats.norm.cdf(r * stats.norm.ppf(0.75)); p90 = stats.norm.cdf(r * stats.norm.ppf(0.9))
        top10 = stats.norm.cdf(r * 1.755); top1 = stats.norm.cdf(r * 2.665)
        top10x = decile_mean(lambda z: W_exact(mu + t * z, tau=t), 0.9, 1.0)
        top1x = decile_mean(lambda z: W_exact(mu + t * z, tau=t), 0.99, 1.0)
        print(f"tau={t}: rho={r:.3f} rho2={r*r:.2f} p75={100*p75:.1f} p90={100*p90:.1f} top10(at mean z)={100*top10:.1f} top1={100*top1:.1f} | exact decile-avg top10={100*top10x:.1f} top1={100*top1x:.1f}")

    # ---------- Elo stationary error ----------
    print("\n== Q3 linearised Elo error ==")
    for K in (10, 16, 20, 32, 40):
        v0 = K / (8 * c)
        v1 = K / (4 * c * (2 - K * c))
        v2 = K / (8 * c * (1 - K * c))
        print(f"K={K}: Kc={K*c:.4f} tau_R={1/(K*c):.1f} half-life={np.log(2)/(K*c):.1f}  sd sqrt(200K/ln10)={np.sqrt(v0):.1f}  K/(4c(2-Kc))={np.sqrt(v1):.1f}  with opp-noise K/(8c(1-Kc))={np.sqrt(v2):.1f}  9.3*sqrt(K)={9.3*np.sqrt(K):.1f}")

    # time constant under random matching for player at skill offset d: tau = 400/(K ln10 E[P(1-P)])
    for K in (16,):
        for d in (0, 350):
            t = mu + tau * gh_x
            p = F(mu + d - t)
            q = np.sum(gh_w * p * (1 - p))
            print(f"random matching K={K}, d={d}: E[P(1-P)]={q:.4f}, tau_R={400/(K*LN10*q):.1f} games")

    # ---------- scale stretching theory ----------
    print("\n== Q3 scale stretching: mean-field ODE (my derivation) ==")
    # dlam/dt = K c [sig_e^2 + sig_q^2 (1 - lam)] / (lam^2 tau^2 + sig_e^2 + sig_q^2), sig_e^2 = K lam /(8c(1-Kc/lam))
    def sig_e2(K, lam):
        return K * lam / (8 * c * max(1 - K * c / lam, 1e-3))


    def lam_path(K, sq, lam0, T, dt=1.0):
        lam = lam0
        out = {}
        for t in range(1, T + 1):
            se2 = sig_e2(K, lam)
            lam += dt * K * c * (se2 + sq ** 2 * (1 - lam)) / (lam ** 2 * tau ** 2 + se2 + sq ** 2)
            if t in (250, 500, 1000, 2000, 3000, 5000, 10000, 20000, 50000):
                out[t] = lam
        return out


    def lam_star(K, sq):
        if sq == 0:
            return np.inf
        f = lambda lam: lam - 1 - sig_e2(K, lam) / sq ** 2
        # equilibrium exists iff f has root > 1
        grid = np.linspace(1.0001, 200, 200000)
        vals = np.array([f(g) for g in grid[::100]])
        idx = np.where(np.sign(vals[:-1]) != np.sign(vals[1:]))[0]
        if len(idx) == 0:
            return np.inf
        return optimize.brentq(f, grid[::100][idx[0]], grid[::100][idx[0] + 1])


    for K in (16, 32):
        print(f"K={K}: critical window sd (sig_q at which A=1, lam=1): {np.sqrt(sig_e2(K,1.0)):.1f}")
        for sq in (0, 20, 30, 40, 50, 70, 100, 150, 200):
            ls = lam_star(K, sq)
            p1 = lam_path(K, sq, 1.0, 20000)
            print(f"  sig_q={sq:3d}: lam*={ls:6.2f}  ODE from lam0=1: " + " ".join(f"t{t}={v:.2f}" for t, v in p1.items()))
        print(f"  note formula sqrt(1+K^2 t/(4tau^2)): t1000={np.sqrt(1+K*K*1000/(4*tau**2)):.2f} t3000={np.sqrt(1+K*K*3000/(4*tau**2)):.2f}; from lam0=0: t1000={np.sqrt(K*K*1000/(4*tau**2)):.2f} t3000={np.sqrt(K*K*3000/(4*tau**2)):.2f}")

    # ---------- Teams ----------
    print("\n== Q4 teams (random teammates/opponents), focal top-decile; exact-ish via MC with logistic F ==")
    rng = np.random.default_rng(12345)
    M = 400000
    for n in (1, 2, 3, 5, 6, 8):
        zf = stats.norm.ppf(rng.uniform(0.9, 1.0, M))
        d = tau * zf
        others = rng.normal(0, tau, (M, 2 * n - 1))
        diff_sum = d + others[:, : n - 1].sum(1) - others[:, n - 1:].sum(1)
        w_sum = F(diff_sum / np.sqrt(n)).mean()
        w_mean = F(diff_sum / n).mean()
        # normal-approx closed forms at E[z]=1.755
        dd = 1.755 * tau
        f_sum = stats.norm.cdf((dd / np.sqrt(n)) / np.sqrt(sig_d ** 2 + (2 * n - 1) * tau ** 2 / n))
        f_mean = stats.norm.cdf((dd / n) / np.sqrt(sig_d ** 2 + (2 * n - 1) * tau ** 2 / n ** 2))
        sl_sum = stats.norm.pdf(0) * (1 / np.sqrt(n)) / np.sqrt(sig_d ** 2 + (2 * n - 1) * tau ** 2 / n) * 1e4
        sl_mean = stats.norm.pdf(0) * (1 / n) / np.sqrt(sig_d ** 2 + (2 * n - 1) * tau ** 2 / n ** 2) * 1e4
        sl_eq = stats.norm.pdf(0) / np.sqrt(n) / sig_d * 1e4
        print(f"n={n}: sum-model top10 MC={100*w_sum:.1f}% (formula@E[z] {100*f_sum:.1f}%), mean-model MC={100*w_mean:.1f}% (formula {100*f_mean:.1f}%); slope/100pts sum={sl_sum:.1f}pp mean={sl_mean:.1f}pp equal-mates={sl_eq:.1f}pp")
    sl1 = stats.norm.pdf(0) / np.sqrt(sig_d ** 2 + tau ** 2)
    print(f"dilution ratios n=5: sum {stats.norm.pdf(0)*(1/np.sqrt(5))/np.sqrt(sig_d**2+9*tau**2/5)/sl1:.3f}, mean {stats.norm.pdf(0)*(1/5)/np.sqrt(sig_d**2+9*tau**2/25)/sl1:.3f}")

    # ---------- Plackett-Luce ----------
    print("\n== Q4 Plackett-Luce ==")
    def pl_top_k(w, N, k):
        p_not = 1.0
        for j in range(k):
            p_not *= (N - 1 - j) / (w + N - 1 - j)
        return 1 - p_not
    for d in (-200, 0, 100, 200, 400):
        w = 10 ** (d / 400)
        print(f"d={d:+d}: w={w:.2f} 1v1={100*F(d):.1f}% 8FFA 1st={100*w/(w+7):.1f}% top4={100*pl_top_k(w,8,4):.1f}% 100BR 1st={100*w/(w+99):.2f}% top10={100*pl_top_k(w,100,10):.1f}% top50={100*pl_top_k(w,100,50):.1f}%")
    # MC check of PL formula with Gumbel performances
    G = rng.gumbel(0, 400 / LN10, (200000, 8))
    G[:, 0] += 200
    place = (G > G[:, [0]]).sum(1)
    print(f"MC Gumbel check d=+200: P(1st)={100*(place==0).mean():.1f}% P(top4)={100*(place<4).mean():.1f}%  pairwise P(beat one)={100*(G[:,0]>G[:,1]).mean():.1f}%")
    # top-decile focal vs 7 random opponents (random matching), true skills
    M = 400000
    sf = tau * stats.norm.ppf(rng.uniform(0.9, 1.0, M))
    so = rng.normal(0, tau, (M, 7))
    wf = 10 ** (sf / 400); wo = 10 ** (so / 400)
    p1 = (wf / (wf + wo.sum(1))).mean()
    # P(top4) by MC of gumbels
    perf_f = sf + rng.gumbel(0, 400 / LN10, M)
    perf_o = so + rng.gumbel(0, 400 / LN10, (M, 7))
    pl = (perf_o > perf_f[:, None]).sum(1)
    print(f"random 8-FFA, top-decile focal: P(1st)={100*p1:.1f}%, P(top4)={100*(pl<4).mean():.1f}%, avg place={1+pl.mean():.2f}")
    sb = -tau * stats.norm.ppf(rng.uniform(0.9, 1.0, M))
    wb = 10 ** (sb / 400)
    print(f"random 8-FFA, bottom-decile focal: P(1st)={100*(wb/(wb+wo.sum(1))).mean():.1f}%")

    # ---------- per-game noise ----------
    print("\n== Q5 per-game noise sx=150 ==")
    se = np.sqrt(sig_d ** 2 + 2 * 150 ** 2)
    print(f"effective sigma_d={se:.1f}, ratio {sig_d/se:.3f}")
    # exact: diff noise N(0, 2*150^2) convolved with logistic
    xg = 150 * np.sqrt(2) * gh_x
    def F_noisy(d):
        return np.sum(gh_w * F(np.asarray(d)[..., None] + xg), axis=-1)
    # local slope of F_noisy at 0 relative to F
    h = 1.0
    print(f"exact slope ratio at 0: {(F_noisy(h)-F_noisy(-h))/(F(h)-F(-h)):.3f}")
    # the rating-scale that Elo would converge to under random matching: solve for lambda s.t. average calibration holds (approx = slope ratio over matched distribution)
    top10_noisy = decile_mean(lambda z: np.array([np.sum(gh_w * F_noisy(mu + tau * zz - (mu + tau * gh_x))) for zz in np.atleast_1d(z)]), 0.9, 1.0, n=301)
    print(f"random matching top-decile win rate with noise 150 (exact): {100*top10_noisy:.1f}% (normal approx at E[z]: {100*stats.norm.cdf(1.755*tau/np.sqrt(se**2+tau**2)):.1f}%)")

    # ---------- AR(1) absorption & window variance theory ----------
    print("\n== Q5 AR(1) state ==")
    phi = 0.99
    for K in (16, 32):
        a = K * c
        print(f"K={K}: absorbed share alpha/(1-(1-alpha)phi) = {a/(1-(1-a)*phi):.3f}")
    n = 100
    k = np.arange(1, n)
    var_ubar = (n + 2 * np.sum((n - k) * phi ** k)) / n ** 2
    print(f"Var(mean of u over 100 games)/sigma_u^2 = {var_ubar:.3f}")

    # ---------- improvement ----------
    print("\n== Q5 improvement ==")
    for K in (16, 32):
        for v in (0.1, 0.5, 1.0):
            print(f"K={K} v={v}: v/K={100*v/K:.2f}pp  lag v/(Kc)={v/(K*c):.1f}")

    # ---------- binomial ----------
    print("\n== Q6 binomial ==")
    for nn in (20, 50, 100, 200, 500, 1000, 2000, 5000):
        se_ = np.sqrt(0.25 / nn)
        z = stats.norm.ppf(0.975)
        ph = 0.52
        centre = (ph + z * z / (2 * nn)) / (1 + z * z / nn)
        half = z * np.sqrt(ph * (1 - ph) / nn + z * z / (4 * nn * nn)) / (1 + z * z / nn)
        print(f"n={nn}: SE={100*se_:.2f}pp Wald95=+/-{100*z*se_:.2f}pp Wilson(52%)={100*(centre-half):.1f}-{100*(centre+half):.1f}%")
    def n_req(p0, p1, alpha, power, two_sided=True):
        za = stats.norm.ppf(1 - alpha / 2) if two_sided else stats.norm.ppf(1 - alpha)
        zb = stats.norm.ppf(power)
        return ((za * np.sqrt(p0 * (1 - p0)) + zb * np.sqrt(p1 * (1 - p1))) / (p1 - p0)) ** 2
    print(f"n(52 vs 50, 2-sided .05, 80%) = {n_req(.5,.52,.05,.8):.2f}; 1-sided = {n_req(.5,.52,.05,.8,False):.2f}; 2-sided 90% = {n_req(.5,.52,.05,.9):.2f}")
    # exact binomial power check for n=4903/4904
    for nn in (4903, 4904):
        crit_hi = stats.binom.ppf(0.975, nn, 0.5)
        # reject if X > crit_hi or X < crit_lo
        lo = stats.binom.ppf(0.025, nn, 0.5)
        pw = stats.binom.sf(crit_hi, nn, 0.52) + stats.binom.cdf(lo - 1, nn, 0.52)
        print(f"  exact-binomial power at n={nn} (normal-ish critical values): {pw:.4f}")
    z = stats.norm.ppf(0.975)
    print(f"observed 52%: score/Wilson test excludes 50% iff n > {0.25*(z/0.02)**2:.1f}; Wald with p_hat: n > {0.52*0.48*(z/0.02)**2:.1f}; z=1.96 exactly -> {0.25*(1.96/0.02)**2:.1f}")
    print(f"P(X>=60|100)={stats.binom.sf(59,100,.5):.4f}; P(X>=14|20)={stats.binom.sf(13,20,.5):.4f}; P(X>=15|20)={stats.binom.sf(14,20,.5):.4f}; P(X>=275|500)={stats.binom.sf(274,500,.5):.4f}")


def exp_j0():
    for j in (0, 1, 5, 20):
        r = sim_1v1(N=4000, K=16, rounds=3000, burn=3000, mode="sbmm", jitter=j, seed=77, checkpoints=(3000,))
        s, R = r["s"], r["R"]
        lam, a, rsd, corr = line_fit(s, R)
        p = np.polyfit(s, R, 3); rc = (R - np.polyval(p, s)).std()
        # local sd: sd of R within 40 skill-quantile bins
        q = ranks01(s); b = (q*40).astype(int)
        loc = np.sqrt(np.mean([R[b==k].var() - lam**2*s[b==k].var() for k in range(40)]))
        nuniq = np.unique(np.round(R, 6)).size
        out(f"jitter={j}: slope {lam:.2f} linear-resid {rsd:.0f} cubic-resid {rc:.0f} local-sd {loc:.0f} unique ratings {nuniq} sdR {R.std():.0f} cubic coefs {p[0]*200**3:.1f},{p[1]*200**2:.1f}")


def exp_reset_frozen():
    def reset(K, mode, jitter, seed, N=4000, pre=1000, post=400, nreset=200):
        rng = np.random.default_rng(seed)
        s = MU + TAU * rng.standard_normal(N); R = np.full(N, MU)
        def play():
            o = pair_order(R, rng, mode, jitter); a, b = o[0::2], o[1::2]
            S = (rng.random(a.size) < F(s[a] - s[b])).astype(float)
            d = K * (S - F(R[a] - R[b])); R[a] += d; R[b] -= d
        for _ in range(pre): play()
        top = np.where(ranks01(s) >= 0.9)[0]; sel = rng.choice(top, nreset, replace=False)
        oth = np.setdiff1d(np.arange(N), sel)
        lam0, a0, _, _ = line_fit(s[oth], R[oth]); target = a0 + lam0 * s[sel]
        drop = np.mean(R[sel] - MU) * nreset / N
        R[sel] = MU
        gm, gf, meanR_oth = [], [], []
        for t in range(post + 1):
            lam, a, _, _ = line_fit(s[oth], R[oth])
            gm.append(np.mean(s[sel] - (R[sel] - a) / lam)); gf.append(np.mean(target - R[sel]) / lam0)
            if t < post: play()
        gm, gf = np.array(gm), np.array(gf)
        f = lambda g, q: int(np.argmax(g <= q * g[0])) if (g <= q*g[0]).any() else -1
        out(f"{mode} K={K}: population-mean drop from reset {drop:.1f} rating pts; moving-target 50%/90%: {f(gm,.5)}/{f(gm,.1)}; "
              f"frozen-target (note's definition) 50%/90%: {f(gf,.5)}/{f(gf,.1)}; frozen-target residual gap at t=400: {gf[-1]:.1f} skill pts; intercept shift {a-a0:+.1f}")
    for K in (16, 32):
        reset(K, "sbmm", 100, 900 + K)
    for K in (16, 32):
        reset(K, "random", 0, 950 + K)


def exp_misc():
    # (a) error autocorrelation K=32
    for mode, j in (("random", 0), ("sbmm", 100)):
        r = sim_1v1(N=4000, K=32, rounds=1600, burn=1600, mode=mode, jitter=j, seed=611 + j, e_autocorr=(1200, 1600))
        acf = r["e_acf"]
        out(f"K=32 {mode} jitter={j}: " + " ".join(f"k{k}:{v:.3f}" for k, v in acf.items() if k <= 60) +
              " | implied tau k=10/20/40: " + ", ".join(f"{-k/np.log(acf[k]):.0f}" for k in (10, 20, 40)))
    # (b) cold start RMSE(R-s) under random matching
    for K in (16, 32):
        rng = np.random.default_rng(1300 + K)
        N = 4000
        s = MU + TAU * rng.standard_normal(N); R = np.full(N, MU); rm = []
        for t in range(1500):
            o = rng.permutation(N); a, b = o[0::2], o[1::2]
            S = (rng.random(a.size) < F(s[a] - s[b])).astype(float)
            d = K * (S - F(R[a] - R[b])); R[a] += d; R[b] -= d
            rm.append(np.sqrt(np.mean((R - s - (R - s).mean()) ** 2)))
        rm = np.array(rm); st = rm[1000:].mean()
        out(f"cold start random K={K}: stationary RMSE {st:.1f}; games to <=2x: {np.argmax(rm <= 2*st)+1}, <=1.1x: {np.argmax(rm <= 1.1*st)+1}")


def exp_reset_seeds():
    for seed in (1, 2):
        for K in (16, 32):
            r = sim_reset(N=4000, K=K, mode="sbmm", jitter=100, seed=seed*100+K)
            out(f"seed{seed} sbmm K={K}: half={r['half']} 90%={r['ninety']} W50 {100*r['w50']:.1f}% W100 {100*r['w100']:.1f}% lam {r['lam']:.2f}")
    r = sim_reset(N=4000, K=16, mode="sbmm", jitter=100, seed=5, pre=3000)
    out(f"pre=3000 sbmm K=16: half={r['half']} 90%={r['ninety']} W50 {100*r['w50']:.1f}%")



def exp_random():
    for K in (16, 32):
        r = sim_1v1(K=K, mode="random", seed=100 + K)
        report_1v1(f"1v1 random K={K} N=4000 (window games 1001-3000)", r)
    r = sim_1v1(N=2000, K=16, mode="random", seed=5, rounds=1500, burn=500, init="skill")
    report_1v1("1v1 random K=16 N=2000, init at true skill, window 501-1500 (robustness)", r)


def exp_sbmm():
    for K in (16, 32):
        for j in (100, 20):
            r = sim_1v1(K=K, mode="sbmm", jitter=j, seed=200 + K + j)
            report_1v1(f"1v1 SBMM jitter={j} K={K}", r)


def exp_stretch():
    out("\n## Scale stretching robustness (1v1, slope lambda (resid sd) at checkpoints)")
    cp = (250, 500, 1000, 2000, 3000)
    for K in (16, 32):
        for j in (0, 20, 50, 100, 200):
            r = sim_1v1(N=4000, K=K, rounds=3000, burn=3000, mode="sbmm", jitter=j, seed=300 + K + j, checkpoints=cp)
            v = r["varR"]
            out(f"K={K} jitter={j:3d} init=1500: {fmt_cps(r['cps'])} | VarR(3000)={v[-1]:.0f} vs K^2 t/4={K*K*3000/4:.0f}")
    K = 16
    r = sim_1v1(N=4000, K=K, rounds=3000, burn=3000, mode="sbmm_idx", jitter=0, seed=399, checkpoints=cp)
    out(f"K=16 jitter=0 DETERMINISTIC index tie-break: {fmt_cps(r['cps'])}")
    for init in ("skill", 200.0):
        r = sim_1v1(N=4000, K=K, rounds=3000, burn=3000, mode="sbmm", jitter=20, seed=401, init=init, checkpoints=cp)
        v = r["varR"]
        out(f"K=16 jitter=20 init={init}: {fmt_cps(r['cps'])} | VarR(0)->VarR(3000) growth {v[-1]-v[0]:.0f} vs K^2 t/4 {K*K*2999/4:.0f}")
    for blk in (2, 4, 16, 64):
        r = sim_1v1(N=4000, K=K, rounds=3000, burn=3000, mode="block", block=blk, seed=410 + blk, checkpoints=cp)
        out(f"K=16 block-window size {blk:3d} (shuffle within moving rating blocks): {fmt_cps(r['cps'])}")
    out("long runs N=2000, K=16:")
    cpl = (1000, 3000, 6000, 10000)
    for j in (20, 50, 100):
        r = sim_1v1(N=2000, K=16, rounds=10000, burn=10000, mode="sbmm", jitter=j, seed=420 + j, init="skill", checkpoints=cpl)
        out(f"  jitter={j:3d} init=skill: {fmt_cps(r['cps'])}")
    r = sim_1v1(N=2000, K=16, rounds=6000, burn=6000, mode="sbmm", jitter=20, seed=430, churn=1e-3,
                checkpoints=(1000, 3000, 6000))
    out(f"  jitter=20 with churn 0.1%/game (new players at 1500), players age>300: {fmt_cps(r['cps'])}")


def exp_ode():
    out("\n## Mean-field ODE for lambda(t) (my derivation): dlam/dt = Kc[se2 + sq^2(1-lam)]/(lam^2 tau^2 + se2 + sq^2), se2=K lam/(8c(1-Kc/lam))")
    for K in (16, 32):
        thr = np.sqrt(K / (8 * C * (1 - K * C)))
        out(f"K={K}: threshold jitter sd for a finite equilibrium ~ sqrt(K/(8c(1-Kc))) = {thr:.1f}")
        for sq in (0, 20, 50, 100, 200):
            for lam0 in (0.05, 1.0):
                lam = lam0
                res = {}
                for t in range(1, 10001):
                    se2 = K * lam / (8 * C * max(1 - K * C / lam, 1e-3)) if lam > 2 * K * C else K * lam / (8 * C)
                    lam += K * C * (se2 + sq * sq * (1 - lam)) / (lam * lam * TAU * TAU + se2 + sq * sq)
                    if t in (1000, 3000, 10000):
                        res[t] = lam
                st = 1 / (1 - K / (8 * C * (1 - K * C) * sq * sq)) if sq > thr else np.inf
                out(f"  jitter={sq:3d} lam0={lam0}: " + " ".join(f"t{t}={v:.2f}" for t, v in res.items()) + f"  lam*~{st:.2f}")
        out(f"  closed form sqrt(lam0^2+K^2 t/(4tau^2)): lam0=0: t1000={K*np.sqrt(1000)/(2*TAU):.2f} t3000={K*np.sqrt(3000)/(2*TAU):.2f}; lam0=1: t1000={np.sqrt(1+K*K*1000/(4*TAU*TAU)):.2f} t3000={np.sqrt(1+K*K*3000/(4*TAU*TAU)):.2f}")


def exp_trueskill():
    out("\n## TrueSkill-style filter (Elo-equivalent units), slope(resid sd)[mean posterior sd, sd(mu)]")
    for mode, j in (("sbmm", 20), ("sbmm", 100), ("random", 0)):
        for td, lab in ((None, "tau_dyn=sigma0/100"), (0.0, "tau_dyn=0")):
            cps = sim_trueskill(N=2000, rounds=10000, mode=mode, jitter=j, tau_dyn=td, seed=500 + j)
            out(f"{mode} jitter={j} {lab}: " + " ".join(f"t{t}:{v[0]:.2f}({v[2]:.0f})[{v[4]:.0f},{v[5]:.0f}]" for t, v in sorted(cps.items())))
    out("prior sigma0 = true population sd (200), tau_dyn = 4.18 (same absolute dynamics as above):")
    for mode, j in (("sbmm", 20), ("sbmm", 100)):
        cps = sim_trueskill(N=2000, rounds=10000, mode=mode, jitter=j, tau_dyn=4.18, sigma0=200.0, seed=550 + j)
        out(f"{mode} jitter={j} sigma0=200: " + " ".join(f"t{t}:{v[0]:.2f}({v[2]:.0f})[{v[4]:.0f},{v[5]:.0f}]" for t, v in sorted(cps.items())))


def exp_tau():
    out("\n## Rating-error autocorrelation (time constant)")
    for mode, j in (("random", 0), ("sbmm", 100), ("sbmm", 200)):
        r = sim_1v1(N=4000, K=16, rounds=1600, burn=1600, mode=mode, jitter=j, seed=600 + j, e_autocorr=(1200, 1600))
        acf = r["e_acf"]
        ks = np.array(list(acf.keys()))
        vals = np.array(list(acf.values()))
        tau_fit = -ks[vals > 0.05] / np.log(vals[vals > 0.05])
        out(f"K=16 {mode} jitter={j}: " + " ".join(f"k{k}:{v:.3f}" for k, v in acf.items()) +
            f" | implied tau from k=20/50/100: {', '.join(f'{-k/np.log(acf[k]):.0f}' for k in (20, 50, 100))}")
    out("\n## Reset experiment (200 of 400 top-decile players reset to 1500 after 1000 rounds), N=4000")
    for mode, j in (("sbmm", 100), ("random", 0)):
        for K in (16, 32):
            r = sim_reset(K=K, mode=mode, jitter=j, seed=700 + K)
            out(f"{mode} K={K}: gap0={r['g0']:.0f} half={r['half']} 90%={r['ninety']} | W first50 {100*r['w50']:.1f}% first100 {100*r['w100']:.1f}% g300-400 {100*r['w300']:.1f}% | lam {r['lam']:.2f}")
    r = sim_reset(K=16, mode="sbmm", jitter=50, seed=777)
    out(f"sbmm jitter=50 K=16: half={r['half']} 90%={r['ninety']} W50 {100*r['w50']:.1f}%")


def exp_team():
    out("\n## 5v5 teams")
    for mode in ("random", "sbmm"):
        for model in ("sum", "mean"):
            for K in ((16, 32) if model == "sum" else (16,)):
                r = sim_team(K=K, mode=mode, model=model, seed=800 + K + (mode == "sbmm") * 10 + (model == "mean"))
                report_1v1(f"5v5 {mode} {model}-model K={K}", r, show_deciles=False)
    r = sim_team(K=16, mode="sbmm", model="sum", jitter=200, seed=850)
    report_1v1("5v5 sbmm sum-model K=16 jitter=200 (sensitivity)", r, show_deciles=False)


def exp_ffa():
    out("\n## 8-player FFA (Plackett-Luce truth, pairwise Elo K/7)")
    for mode in ("random", "sbmm"):
        for K in (16, 32):
            r = sim_ffa(K=K, mode=mode, seed=900 + K + (mode == "sbmm"))
            rows, ext = decile_rows(r["s"], {"first": r["first"], "top4": r["top4"], "place": r["place"]})
            t, bt = rows[-1][2], rows[0][2]
            out(f"{mode} K={K}: top10% P1st {100*t['first']:.1f}% top4 {100*t['top4']:.1f}% place {t['place']:.2f} | bottom10% P1st {100*bt['first']:.1f}% top4 {100*bt['top4']:.1f}% place {bt['place']:.2f} | top1% P1st {100*ext['first'][0]:.1f}% | slope {r['lam']:.3f} resid {r['rsd']:.1f}")


def exp_form():
    out("\n## Skill fluctuation")
    for mode, j in (("random", 0), ("sbmm", 100)):
        r = sim_1v1(K=16, mode=mode, jitter=j, form="iid", sx=150, seed=1000 + j)
        report_1v1(f"1v1 {mode} per-game noise sd150 K=16", r, show_deciles=False)
    for mode, j in (("random", 0), ("sbmm", 100)):
        for K in (16, 32):
            r = sim_1v1(K=K, mode=mode, jitter=j, form="ar1", su=100, phi=0.99, seed=1100 + K + j,
                        store_outcomes=(mode == "sbmm"))
            report_1v1(f"1v1 {mode} AR(1) form sd100 phi0.99 K={K}", r, show_deciles=False)
    out("\n## Improvement (10% of players +0.5/game for 600 games)")
    for mode, j in (("sbmm", 100), ("random", 0)):
        for K in (16, 32):
            r = sim_improve(K=K, mode=mode, jitter=j, seed=1200 + K + j)
            out(f"{mode} K={K}: first100 W {100*r['w100']:.1f}% | games101-600 W {100*r['W']:.1f}% E {100*r['E']:.1f}% W-E {100*r['WmE']:+.2f}pp "
                f"(=drift/K {100*r['drift_over_K']:+.2f}pp; theory lam v/K {100*r['theory_WmE']:+.2f}pp, v/K {100*0.5/K:.2f}pp) | "
                f"lag {r['lag']:.1f} skill pts (theory lam v/(Kc) {r['theory_lag']:.1f}) lam {r['lam']:.2f} | after stop W {100*r['Wafter']:.1f}% E {100*r['Eafter']:.1f}%")


EXPS = dict(analytic=exp_analytic, j0=exp_j0, reset_frozen=exp_reset_frozen, misc=exp_misc, reset_seeds=exp_reset_seeds, random=exp_random, sbmm=exp_sbmm, stretch=exp_stretch, ode=exp_ode, trueskill=exp_trueskill,
            tau=exp_tau, team=exp_team, ffa=exp_ffa, form=exp_form)

if __name__ == "__main__":
    for name in sys.argv[1:]:
        t0 = time.time()
        EXPS[name]()
        out(f"[{name} done in {time.time()-t0:.0f}s]")
