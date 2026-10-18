"""Independent adversarial verification of streaks_elo_feeling.md / streaks_sim_results.md.

Written from scratch WITHOUT reading streaks_sim.py (the original author's script).
Part A: exact / analytic streak mathematics (Markov-chain DP, first-win recursion, KMP automaton,
        exact Miller-Sanjurjo DP) + Monte Carlo cross-checks.
Part B: population Monte Carlo of Elo SBMM, tilt, streak bonus, 5v5, manipulation, robustness.

Usage:
  python verify_streaks.py A                 # part A -> partA_out.md
  python verify_streaks.py B name1 name2 ... # part B scenarios -> resultsB.json (appended)
  python verify_streaks.py list              # list scenario names
One process at a time; N=5000 by default keeps peak RSS < ~1 GB.
"""
import numpy as np, json, sys, time, os
from math import log, pi

OUTDIR = os.path.dirname(os.path.abspath(__file__))
EULER = 0.5772156649015329


def f(d):
    return 1.0 / (1.0 + np.power(10.0, -np.asarray(d, dtype=float) / 400.0))

# =====================================================================================
# PART A  exact mathematics
# =====================================================================================

def p_longest_lt(n, q, r):
    """P(longest run of losses < r) in n iid games, P(loss)=q. Markov chain on trailing loss-run length."""
    if r <= 0:
        return 0.0
    v = np.zeros(r); v[0] = 1.0
    p = 1 - q
    for _ in range(n):
        nv = np.empty(r)
        nv[0] = v.sum() * p
        nv[1:] = v[:-1] * q          # a run reaching length r is absorbed (dropped)
        v = nv
    return float(v.sum())


def a_recursion(n, q, r):
    """The notes' first-win recursion a_n = sum_{j<r} q^j p a_{n-j-1}, a_m = 1 for m<r."""
    p = 1 - q
    a = [1.0] * (n + 1)
    for m in range(r, n + 1):
        a[m] = sum(q ** j * p * a[m - j - 1] for j in range(r))
    return a[n]


def longest_dist(n, q, rmax=60):
    lt = np.array([p_longest_lt(n, q, r) for r in range(0, rmax + 2)])   # P(L<r)
    ge = 1 - lt                                                          # P(L>=r)
    pmf = lt[1:] - lt[:-1]
    E = ge[1:].sum()
    E2 = sum((2 * r - 1) * ge[r] for r in range(1, rmax + 2))
    cdf = np.cumsum(pmf)
    return E, (E2 - E * E) ** 0.5, int(np.searchsorted(cdf, 0.5)), int(np.searchsorted(cdf, 0.95)), ge


def schilling(n, q):
    """Gordon-Schilling-Waterman: E[L_n] ~ log_{1/q}(n p) + gamma/ln(1/q) - 1/2."""
    return log(n * (1 - q)) / log(1 / q) + EULER / log(1 / q) - 0.5


def schilling_sd(q):
    return (pi ** 2 / (6 * log(1 / q) ** 2) + 1 / 12) ** 0.5


def expected_runs_ge(n, q, r):
    return q ** r * (1 + (n - r) * (1 - q))


def p_pattern(n, pattern, pw):
    """P(pattern over {W,L} occurs at least once in n iid games) via KMP automaton."""
    m = len(pattern)

    def nxt(state, ch):
        s = pattern[:state] + ch
        for L in range(min(len(s), m), -1, -1):
            if s[len(s) - L:] == pattern[:L]:
                return L
        return 0
    trans = [[nxt(s, 'W'), nxt(s, 'L')] for s in range(m)]
    v = np.zeros(m + 1); v[0] = 1
    for _ in range(n):
        nv = np.zeros(m + 1); nv[m] = v[m]
        for s in range(m):
            nv[trans[s][0]] += v[s] * pw
            nv[trans[s][1]] += v[s] * (1 - pw)
        v = nv
    return float(v[m])


def ms_exact(n, k, p=0.5):
    """Exact Miller-Sanjurjo: E[ #wins after k straight wins / #games after k straight wins | denominator>0 ]
    for one iid history of n games. DP over (capped streak s, trials c, successes w)."""
    q = 1 - p
    D = np.zeros((k + 1, n + 1, n + 1)); D[0, 0, 0] = 1.0
    for _ in range(n):
        N_ = np.zeros_like(D)
        for s in range(k):                       # not a trial
            N_[min(s + 1, k)] += p * D[s]
            N_[0] += q * D[s]
        N_[k, 1:, 1:] += p * D[k, :-1, :-1]      # trial, win
        N_[0, 1:, :] += q * D[k, :-1, :]         # trial, loss
        D = N_
    P = D.sum(0)
    c = np.arange(n + 1)[:, None]; w = np.arange(n + 1)[None, :]
    P0 = P[0].sum()
    with np.errstate(invalid="ignore", divide="ignore"):
        ratio = np.where(c > 0, w / np.maximum(c, 1), 0.0)
    return float((P[1:] * ratio[1:]).sum() / (1 - P0)), float(1 - P0)


def runs_of(x):
    idx = np.flatnonzero(np.diff(x.astype(np.int8))) + 1
    starts = np.r_[0, idx]
    return x[starts], np.diff(np.r_[starts, len(x)])


def count_wk_lk_vec(X, k):
    n = X.shape[1]; m = n - 2 * k + 1
    ok = np.ones((X.shape[0], m), bool)
    for j in range(k):
        ok &= X[:, j:m + j]
        ok &= ~X[:, k + j:m + k + j]
    return ok.sum(1)


def partA():
    rng = np.random.default_rng(777001)
    out = []
    pr = lambda s="": (print(s, flush=True), out.append(s))
    pr("## A1 exact longest losing run (Markov DP) vs Gordon-Schilling-Waterman approx")
    pr("| p(win) | n | E exact | approx | SD exact | SD approx | median | p95 | P>=5 | P>=7 | P>=10 | P>=12 | E#runs>=5 | >=7 | >=10 |")
    pr("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    md = 0
    for pw in (0.45, 0.5, 0.55):
        q = 1 - pw
        for n in (50, 100, 500, 1000):
            E, sd, med, p95, ge = longest_dist(n, q)
            S = schilling(n, q); md = max(md, abs(E - S))
            pr(f"| {pw} | {n} | {E:.3f} | {S:.3f} | {sd:.3f} | {schilling_sd(q):.3f} | {med} | {p95} | {ge[5]:.4f} | {ge[7]:.4f} | {ge[10]:.4f} | {ge[12]:.4f} | {expected_runs_ge(n,q,5):.2f} | {expected_runs_ge(n,q,7):.2f} | {expected_runs_ge(n,q,10):.3f} |")
    pr(f"max |E exact - approx| = {md:.3f}")
    for (n, q, r) in ((100, 0.5, 5), (100, 0.5, 7), (1000, 0.5, 7), (1000, 0.5, 10), (1000, 0.55, 10)):
        pr(f"first-win recursion n={n} q={q} r={r}: P(>=r) = {1-a_recursion(n,q,r):.5f}  (DP {1-p_longest_lt(n,q,r):.5f})")
    # MC check (own seed)
    for n, pw in ((100, 0.5), (1000, 0.5), (1000, 0.45)):
        S = 100000 if n == 100 else 30000
        X = rng.random((S, n)) < pw
        L = np.zeros(S, np.int32); cur = np.zeros(S, np.int32)
        for t in range(n):
            cur = np.where(~X[:, t], cur + 1, 0); np.maximum(L, cur, out=L)
        pr(f"MC n={n} p={pw} ({S}): mean {L.mean():.3f}, P>=5 {(L>=5).mean():.4f}, P>=7 {(L>=7).mean():.4f}, P>=10 {(L>=10).mean():.4f}")
    pr(f"rule of thumb log2(n/2): n=100 -> {np.log2(50):.2f}, n=1000 -> {np.log2(500):.2f}")

    pr("\n## A3 P(W^k L^k at least once in n games), exact KMP")
    for pw in (0.5, 0.45):
        for k in (3, 4, 5, 6):
            pat = "W" * k + "L" * k
            pr(f"p={pw} k={k}: " + ", ".join(f"n={n}: {p_pattern(n, pat, pw):.4f}" for n in (50, 100, 500, 1000)))
    # either order
    X = rng.random((200000, 100)) < 0.5
    either = ((count_wk_lk_vec(X, 4) > 0) | (count_wk_lk_vec(~X, 4) > 0)).mean()
    pr(f"either order (W4L4 or L4W4) at least once in 100 (MC 2e5): {either:.4f}; W4L4 MC {(count_wk_lk_vec(X,4)>0).mean():.4f}")

    pr("\n## A4c expected count of (W-run>=k immediately followed by L-run>=k) = (n-2k+1)(pq)^k")
    for pw in (0.5, 0.45):
        for k in (3, 4, 5):
            for n in (100, 1000):
                fml = (n - 2 * k + 1) * (pw * (1 - pw)) ** k
                X = rng.random((20000, n)) < pw
                sub = count_wk_lk_vec(X, k).mean()
                # run-pair count on a subset (literal definition)
                rp = []
                for i in range(1500):
                    v, l = runs_of(X[i])
                    rp.append(int(np.sum(v[:-1] & ~v[1:] & (l[:-1] >= k) & (l[1:] >= k))))
                pr(f"p={pw} k={k} n={n}: formula {fml:.4f} | MC substring {sub:.4f} | MC run-pairs(1500) {np.mean(rp):.4f}")
    # exactly-k variant: W-run of exactly k followed by L-run of exactly k
    n, k = 1000, 4
    X = rng.random((4000, n)) < 0.5
    ex = []
    for i in range(4000):
        v, l = runs_of(X[i])
        ex.append(int(np.sum(v[:-1] & ~v[1:] & (l[:-1] == k) & (l[1:] == k))))
    # analytic exactly-k: interior boundary needs L W^k L^k W  => (n-2k-1) p^(k+1) q^(k+1) + edge terms
    p_ = q_ = 0.5
    exact_k = (n - 2 * k - 1) * p_ ** (k + 1) * q_ ** (k + 1) + 2 * p_ ** (k) * q_ ** (k) * 0.5
    pr(f"EXACTLY 4 W then EXACTLY 4 L per 1000 (p=.5): MC {np.mean(ex):.3f}, analytic {exact_k:.3f}; at-least version 3.879; either order at-least 7.76")

    pr("\n## A4d Miller-Sanjurjo: expected per-history P-hat(W | previous k all W), p=0.5")
    for n in (20, 50, 100, 200):
        row = []
        for k in (1, 2, 3, 4, 5):
            m, frac = ms_exact(n, k)
            row.append(f"{m:.4f}")
        pr(f"n={n} exact DP: k=1..5 " + " ".join(row))
    m, frac = ms_exact(100, 3)
    pr(f"n=100 k=3 exact: {m:.4f}; P(at least one qualifying game) = {frac:.6f}")
    # MC for n=1000 + variants
    S = 40000
    X = rng.random((S, 1000)) < 0.5
    for k in (3, 5):
        cond = np.ones((S, 1000 - k), bool)
        for j in range(k):
            cond &= X[:, j:1000 - k + j]
        cnt = cond.sum(1); wins = (cond & X[:, k:]).sum(1); d = cnt > 0
        pr(f"n=1000 k={k} MC: {np.mean(wins[d]/cnt[d]):.4f} (pooled {wins.sum()/cnt.sum():.4f})")
    # variant: 'last 100 games' of a longer career: streak may have started before window
    S = 200000; n = 100; k = 3
    X = rng.random((S, n + k)) < 0.5
    cond = np.ones((S, n), bool)
    for j in range(k):
        cond &= X[:, j:n + j]
    cnt = cond.sum(1); wins = (cond & X[:, k:]).sum(1); d = cnt > 0
    pr(f"variant: last-100 window of a longer career (prior state known): {np.mean(wins[d]/cnt[d]):.4f}")
    # variant p=0.45/0.55 (player not exactly at 50%)
    for pw in (0.45, 0.55):
        m, _ = ms_exact(100, 3, pw)
        pr(f"n=100 k=3 p={pw}: per-history mean {m:.4f} (true p {pw})  bias {100*(m-pw):+.2f} pp")

    pr("\n## A5 dilution: win prob when you are D Elo above all 9 others")
    from scipy.stats import norm
    beta = 100 / (2 ** .5 * norm.ppf(float(f(100))))
    for D in (50, 100, 200, 400):
        pr(f"D={D}: 1v1 {float(f(D)):.4f} | mean-of-5 logistic {float(f(D/5)):.4f} | sum/sqrt5 logistic {float(f(D/5**.5)):.4f} | Thurstone sum + per-player noise {norm.cdf(D/(10**.5*beta)):.4f}")

    # A7 5v5 attribution with random lobbies, iid N(0,200) skill, random split, mean model (closed-form MC)
    S = 400000
    th = rng.normal(0, 200, (S, 10))
    pA = f(th[:, :5].mean(1) - th[:, 5:].mean(1))
    winA = rng.random(S) < pA
    wk = th.argmin(1)
    me = 0  # I am player 0 on team A
    mate = (wk >= 1) & (wk < 5)
    pr("\n## A7 5v5 attribution (random lobby of iid N(0,200) skills, random split, mean model, closed-form MC)")
    pr(f"P(weakest of 10 is my teammate | loss) {mate[~winA].mean():.4f} | win {mate[winA].mean():.4f} | baseline 4/10")
    pr("\n## A2/A4/A4b either-kind longest run, sliding windows, short sessions")
    for n in (100, 1000):
        E, sd, med, p95, ge = longest_dist(n - 1, 0.5)     # either kind = 1 + longest 'same as previous' run
        pr(f"either-kind longest run n={n}: E={1+E:.3f} median={1+med} p95={1+p95}")
    for n, w, t in ((100, 10, 2), (100, 20, 6), (500, 20, 6), (500, 50, 20)):
        X = (rng.random((100000, n)) < 0.5).astype(np.int16)
        cs = np.concatenate([np.zeros((X.shape[0], 1), np.int16), X.cumsum(1, dtype=np.int16)], 1)
        pr(f"window n={n} w={w}: P(some window with <= {t} wins) = {((cs[:, w:] - cs[:, :-w]).min(1) <= t).mean():.3f}")
    for pw, n in ((0.5, 10), (0.5, 20), (0.5, 30), (0.45, 20)):
        pr(f"session p={pw} n={n}: " + " ".join(f"P>={r} {1-p_longest_lt(n,1-pw,r):.3f}" for r in (3, 4, 5)))
    open(os.path.join(OUTDIR, "partA_out.md"), "w").write("\n".join(out) + "\n")

# =====================================================================================
# PART B  population Monte Carlo
# =====================================================================================

DEFAULT = dict(N=5000, burn=1500, T=2000, K=32.0, sigma=100.0, mode="1v1", match="rating",
               split="random", tilt=0.0, tilt_cap=3, ar_phi=0.0, ar_sd=0.0, bonus=1.0, bonus_from=3,
               bonus_loser=False, manip_k=0, manip_d=0.0, manip_kind="none", init="zero",
               team_model="mean", pairing="noise", bucket=50, seed=1, trace_every=250)


def simulate(**kw):
    c = dict(DEFAULT); c.update(kw)
    rng = np.random.default_rng(c["seed"])
    N, burn, T, K = c["N"], c["burn"], c["T"], c["K"]
    theta = rng.normal(0, 200, N)
    R = theta.copy() if c["init"] == "true" else np.zeros(N)
    ws = np.zeros(N, np.int32); ls = np.zeros(N, np.int32)
    u = rng.normal(0, c["ar_sd"], N) if c["ar_sd"] > 0 else np.zeros(N)
    eps_sd = c["ar_sd"] * np.sqrt(1 - c["ar_phi"] ** 2)
    is5 = c["mode"] == "5v5"
    rec = dict(y=np.zeros((T, N), bool), p=np.zeros((T, N), np.float32),
               ws=np.zeros((T, N), np.int16), ls=np.zeros((T, N), np.int16),
               dR=np.zeros((T, N), np.float32), dS=np.zeros((T, N), np.float32))
    if is5:
        rec.update(mates=np.zeros((T, N), np.float32), weakest_mate=np.zeros((T, N), bool),
                   weakest_me=np.zeros((T, N), bool), team_weaker=np.zeros((T, N), bool))
    trace = []
    for r in range(burn + T):
        s_eff = theta + u - c["tilt"] * np.minimum(ls, c["tilt_cap"])
        streak_sign = (ws >= c["manip_k"]).astype(float) - (ls >= c["manip_k"]).astype(float) if c["manip_k"] > 0 else 0.0
        shift = c["manip_d"] * streak_sign if c["manip_kind"] == "key" else 0.0
        if c["match"] == "random":
            order = rng.permutation(N)
        elif c["pairing"] == "bucket":   # sort by rating (no noise); random order inside fixed consecutive blocks
            o = np.argsort(R + shift + 1e-6 * rng.random(N))
            blk = o.reshape(-1, c["bucket"])
            order = np.take_along_axis(blk, np.argsort(rng.random(blk.shape), axis=1), 1).ravel()
        else:
            order = np.argsort(R + rng.normal(0, c["sigma"], N) + shift)
        if not is5:
            a = order[0::2]; b = order[1::2]
            pa = f(s_eff[a] - s_eff[b])
            win_a = rng.random(a.size) < pa
            delta = K * (win_a - f(R[a] - R[b]))
            if c["bonus"] != 1.0:   # streak bonus multiplies the winner's gain once its streak reaches bonus_from
                ga = np.where(win_a & (ws[a] + 1 >= c["bonus_from"]), c["bonus"], 1.0)
                gb = np.where(~win_a & (ws[b] + 1 >= c["bonus_from"]), c["bonus"], 1.0)
                g = np.where(win_a, ga, gb)
                da = np.where(win_a, delta * g, delta * (g if c["bonus_loser"] else 1.0))
                db = np.where(win_a, -delta * (g if c["bonus_loser"] else 1.0), -delta * g)
            else:
                da = delta; db = -delta
            if r >= burn:
                t = r - burn
                rec["y"][t, a] = win_a; rec["y"][t, b] = ~win_a
                rec["p"][t, a] = pa; rec["p"][t, b] = 1 - pa
                rec["ws"][t] = ws; rec["ls"][t] = ls
                rec["dR"][t, a] = R[b] - R[a]; rec["dR"][t, b] = R[a] - R[b]
                rec["dS"][t, a] = theta[b] - theta[a]; rec["dS"][t, b] = theta[a] - theta[b]
            R[a] += da; R[b] += db
            win = np.empty(N, bool); win[a] = win_a; win[b] = ~win_a
        else:
            lob = order.reshape(-1, 10)
            if c["split"] == "random":
                lob = np.take_along_axis(lob, np.argsort(rng.random(lob.shape), axis=1), 1)
                A = lob[:, :5]; B = lob[:, 5:]
            elif c["split"] == "snake_key":   # snake on the NOISY queue-key order (diagnostic: mimics original script)
                A = lob[:, [0, 3, 4, 7, 8]]; B = lob[:, [1, 2, 5, 6, 9]]
            else:   # snake ABBAABBAAB on (possibly manipulated) MMR
                mmr = R + (c["manip_d"] * streak_sign if c["split"] == "manip" else 0.0)
                srt = np.take_along_axis(lob, np.argsort(-(mmr[lob] + 1e-6 * rng.random(lob.shape)), axis=1), 1)
                A = srt[:, [0, 3, 4, 7, 8]]; B = srt[:, [1, 2, 5, 6, 9]]
            if c["team_model"] == "mean":
                dS_ = s_eff[A].mean(1) - s_eff[B].mean(1); dR_ = R[A].mean(1) - R[B].mean(1)
            else:   # sum model on logistic scale with sqrt(5) normalisation
                dS_ = (s_eff[A].sum(1) - s_eff[B].sum(1)) / np.sqrt(5); dR_ = (R[A].sum(1) - R[B].sum(1)) / np.sqrt(5)
            pA = f(dS_); winA = rng.random(pA.size) < pA
            delta = K * (winA - f(dR_))
            if r >= burn:
                t = r - burn
                rec["y"][t, A] = winA[:, None]; rec["y"][t, B] = ~winA[:, None]
                rec["p"][t, A] = pA[:, None]; rec["p"][t, B] = (1 - pA)[:, None]
                rec["ws"][t] = ws; rec["ls"][t] = ls
                mA = R[A].mean(1); mB = R[B].mean(1)
                rec["dR"][t, A] = (mB - mA)[:, None]; rec["dR"][t, B] = (mA - mB)[:, None]
                tA = theta[A].mean(1); tB = theta[B].mean(1)
                rec["dS"][t, A] = (tB - tA)[:, None]; rec["dS"][t, B] = (tA - tB)[:, None]
                rec["mates"][t, A] = (R[A].sum(1)[:, None] - R[A]) / 4 - R[A]
                rec["mates"][t, B] = (R[B].sum(1)[:, None] - R[B]) / 4 - R[B]
                th = theta[np.concatenate([A, B], 1)]
                wk = th.argmin(1); pos = np.arange(5)[None, :]
                inA = (wk < 5)[:, None]
                rec["weakest_mate"][t, A] = inA & (wk[:, None] != pos)
                rec["weakest_mate"][t, B] = ~inA & ((wk - 5)[:, None] != pos)
                rec["weakest_me"][t, A] = wk[:, None] == pos
                rec["weakest_me"][t, B] = (wk - 5)[:, None] == pos
                rec["team_weaker"][t, A] = (tA < tB)[:, None]; rec["team_weaker"][t, B] = (tB < tA)[:, None]
            R[A] += delta[:, None]; R[B] -= delta[:, None]
            win = np.empty(N, bool); win[A] = winA[:, None]; win[B] = ~winA[:, None]
        ws = np.where(win, ws + 1, 0); ls = np.where(win, 0, ls + 1)
        if c["ar_sd"] > 0:
            u = c["ar_phi"] * u + rng.normal(0, eps_sd, N)
        if (r + 1) % c["trace_every"] == 0:
            trace.append((r + 1, round(float(np.polyfit(theta, R, 1)[0]), 3)))
    return c, theta, R, rec, trace


def excess(val, mask, pbar):
    """within-player excess: mean over qualifying games of (val - that player's own mean of val)"""
    if mask.sum() == 0:
        return float("nan")
    return float((val[mask] - np.broadcast_to(pbar, val.shape)[mask]).mean())


def runs_z(y):
    n = y.shape[0]
    n1 = y.sum(0).astype(float); n2 = n - n1
    runs = 1 + (y[1:] != y[:-1]).sum(0)
    mu = 2 * n1 * n2 / n + 1
    var = 2 * n1 * n2 * (2 * n1 * n2 - n) / (n ** 2 * (n - 1))
    return (runs - mu) / np.sqrt(var)


def streak_stats(y):
    n, N = y.shape
    L = ~y
    cur = np.zeros(N, np.int32); mx = np.zeros(N, np.int32)
    for t in range(n):
        cur = np.where(L[t], cur + 1, 0); np.maximum(mx, cur, out=mx)
    cs = np.vstack([np.zeros((1, N), np.int32), np.cumsum(L, 0, dtype=np.int32)])
    csW = np.vstack([np.zeros((1, N), np.int32), np.cumsum(y, 0, dtype=np.int32)])

    def nruns(r):
        allL = (cs[r:] - cs[:-r]) == r
        prevW = np.vstack([np.ones((1, N), bool), y[:n - r]])
        return float((allL & prevW).sum(0).mean())

    def wl(k):
        m = n - 2 * k + 1
        return float((((csW[k:k + m] - csW[:m]) == k) & ((cs[2 * k:2 * k + m] - cs[k:k + m]) == k)).sum(0).mean())
    return dict(mean_longest=float(mx.mean()), P7=float((mx >= 7).mean()), P10=float((mx >= 10).mean()),
                runs5=nruns(5), wl4=wl(4), wl5=wl(5))


Z2 = (1.959964 + 0.841621) ** 2


def lag1(y):
    x = y - y.mean(0)
    return float((x[:-1] * x[1:]).sum() / (x * x).sum())


def analyse(c, theta, R, rec, rng):
    y = rec["y"]; p = rec["p"]; T, N = y.shape
    pbar = p.mean(0, dtype=np.float64)
    out = {}
    dR = rec["dR"]; dS = rec["dS"]
    dRbar = dR.mean(0, dtype=np.float64); dSbar = dS.mean(0, dtype=np.float64)
    mt = rec.get("mates"); mtb = mt.mean(0, dtype=np.float64) if mt is not None else None
    for k in range(1, 7):
        mW = rec["ws"] >= k; mL = rec["ls"] >= k
        out[f"W{k}"] = 100 * excess(p, mW, pbar); out[f"L{k}"] = 100 * excess(p, mL, pbar)
        out[f"pooledW{k}"] = float(y[mW].mean()); out[f"pooledL{k}"] = float(y[mL].mean())
        out[f"oppR_W{k}"] = excess(dR, mW, dRbar); out[f"oppS_W{k}"] = excess(dS, mW, dSbar)
        out[f"oppR_L{k}"] = excess(dR, mL, dRbar); out[f"oppS_L{k}"] = excess(dS, mL, dSbar)
        if k in (3, 5):
            out[f"overshoot_W{k}"] = float((-dR[mW] + dS[mW]).mean())
        if mt is not None:
            out[f"mates_W{k}"] = excess(mt, mW, mtb); out[f"mates_L{k}"] = excess(mt, mL, mtb)
            out[f"mates_raw_W{k}"] = float(mt[mW].mean())
    if mt is not None:
        out["mates_after_any_win"] = excess(mt[1:], y[:-1], mtb)
        out["mates_raw_after_any_win"] = float(mt[1:][y[:-1]].mean())
    rho = lag1(y)
    perm = np.argsort(rng.random(y.shape), axis=0)
    ysh = np.take_along_axis(y, perm, 0)
    rho_sh = lag1(ysh)
    out["rho1"] = rho; out["rho1_shuffled"] = rho_sh; out["rho1_corr"] = rho - rho_sh
    out["n_detect"] = Z2 / rho ** 2; out["n_detect_corr"] = Z2 / (rho - rho_sh) ** 2
    z = runs_z(y)
    out["runsZ_mean"] = float(np.nanmean(z)); out["pct_alt"] = float(100 * np.nanmean(z > 1.96)); out["pct_streaky"] = float(100 * np.nanmean(z < -1.96))
    # streak stats: two 1000-game halves, real vs within-player shuffle, averaged
    acc = {}
    for h in range(T // 1000):
        yh = y[h * 1000:(h + 1) * 1000]
        sh = np.take_along_axis(yh, np.argsort(rng.random(yh.shape), axis=0), 0)
        for tag, arr in (("real", yh), ("shuf", sh)):
            for kk, vv in streak_stats(arr).items():
                acc.setdefault(f"{tag}_{kk}", []).append(vv)
    out["streak"] = {kk: float(np.mean(vv)) for kk, vv in acc.items()}
    wr = y.mean(0)
    out["sd_wr"] = float(wr.std()); out["pct_45_55"] = float(100 * np.mean((wr >= .45) & (wr <= .55)))
    out["corr_R_theta"] = float(np.corrcoef(R, theta)[0, 1]); out["slope"] = float(np.polyfit(theta, R, 1)[0])
    if "weakest_mate" in rec:
        for nm in ("weakest_mate", "weakest_me", "team_weaker"):
            a = rec[nm]
            out[f"{nm}_loss"] = float(a[~y].mean()); out[f"{nm}_win"] = float(a[y].mean())
    return out


SCEN = {
    # ---- main replication (own seeds, N=5000) ----
    "A_random": dict(match="random", seed=9101),
    "B_K10": dict(K=10, seed=9102), "B_K16": dict(K=16, seed=9103), "B_K32": dict(K=32, seed=9104),
    "B_K64": dict(K=64, seed=9105),
    "C_elo32_tilt30": dict(tilt=30, seed=9106), "C_random_tilt30": dict(match="random", tilt=30, seed=9107),
    "C_elo32_AR60": dict(ar_phi=0.9, ar_sd=60, seed=9108),
    "D_5v5_rand": dict(mode="5v5", sigma=250, seed=9110),
    "D_5v5_bal": dict(mode="5v5", sigma=250, split="balanced", seed=9111),
    "D_5v5_snakekey": dict(mode="5v5", sigma=250, split="snake_key", seed=9117),
    "D_5v5_random_lobby": dict(mode="5v5", match="random", seed=9109),
    "E_bonus": dict(bonus=2.0, seed=9112),
    "F1_manip": dict(manip_k=3, manip_d=100, manip_kind="key", seed=9114),
    "F2_5v5_teammates": dict(mode="5v5", sigma=250, split="manip", manip_k=3, manip_d=300, manip_kind="split", seed=9115),
    "F3_5v5_key": dict(mode="5v5", sigma=250, manip_k=3, manip_d=100, manip_kind="key", seed=9116),
    # ---- second seed / bigger population for headline numbers ----
    "B_K32_seed2_N10k": dict(K=32, seed=9201, N=10000, T=1000),
    "D_5v5_rand_seed2": dict(mode="5v5", sigma=250, seed=9202),
    # ---- robustness: queue noise / window ----
    "R_K32_s25": dict(sigma=25, seed=9301), "R_K32_s50": dict(sigma=50, seed=9302),
    "R_K32_s200": dict(sigma=200, seed=9304), "R_K32_s400": dict(sigma=400, seed=9305),
    "R_K10_s25": dict(K=10, sigma=25, seed=9306),
    "R_K32_bucket10": dict(pairing="bucket", bucket=10, seed=9307),
    "R_K32_bucket500": dict(pairing="bucket", bucket=500, seed=9308),
    # ---- robustness: init / burn-in / N ----
    "R_K32_burn300_inittrue": dict(burn=300, init="true", seed=9309),
    "R_K32_burn300_zero": dict(burn=300, seed=9310),
    "R_K32_N2000": dict(N=2000, seed=9311),
    # ---- robustness: 5v5 ----
    "R_5v5_s100": dict(mode="5v5", sigma=100, seed=9312), "R_5v5_s500": dict(mode="5v5", sigma=500, seed=9313),
    "R_5v5_sum": dict(mode="5v5", sigma=250, team_model="sum", seed=9314),
    "R_5v5_bal_s500": dict(mode="5v5", sigma=500, split="balanced", seed=9315),
    "R_F2_s500": dict(mode="5v5", sigma=500, split="manip", manip_k=3, manip_d=300, manip_kind="split", seed=9316),
    # ---- robustness: manipulation / tilt / bonus under other windows ----
    "R_F1_s25": dict(sigma=25, manip_k=3, manip_d=100, manip_kind="key", seed=9317),
    "R_F1_s200": dict(sigma=200, manip_k=3, manip_d=100, manip_kind="key", seed=9318),
    "R_tilt_s25": dict(sigma=25, tilt=30, seed=9319), "R_tilt_s200": dict(sigma=200, tilt=30, seed=9320),
    "R_bonus_s200": dict(sigma=200, bonus=2.0, seed=9321),
    "R_bonus_loser": dict(bonus=2.0, bonus_loser=True, seed=9322),
    # ---- long scale-drift traces (N=2000, small T) ----
    "S_K32_s25_long": dict(sigma=25, N=2000, burn=8000, T=1000, seed=9401, trace_every=1000),
    "S_K32_s100_long": dict(sigma=100, N=2000, burn=8000, T=1000, seed=9402, trace_every=1000),
    "S_5v5_bal_long": dict(mode="5v5", sigma=250, split="balanced", N=2000, burn=8000, T=1000, seed=9403, trace_every=1000),
    "S_5v5_rand_long": dict(mode="5v5", sigma=250, N=2000, burn=8000, T=1000, seed=9404, trace_every=1000),
}


def runB(names):
    path = os.path.join(OUTDIR, "resultsB.json")
    res = json.load(open(path)) if os.path.exists(path) else {}
    for nm in names:
        t0 = time.time()
        c, theta, R, rec, tr = simulate(**SCEN[nm])
        o = analyse(c, theta, R, rec, np.random.default_rng(c["seed"] + 12345))
        del rec
        o["trace"] = tr; o["cfg"] = c; o["secs"] = time.time() - t0
        res[nm] = o
        json.dump(res, open(path, "w"), indent=1, default=float)
        s = o["streak"]
        print(f"[{nm}] {o['secs']:.0f}s W1..W6 " + " ".join(f"{o[f'W{k}']:+.2f}" for k in range(1, 7)) +
              f" | L3 {o['L3']:+.2f} L5 {o['L5']:+.2f} | oppR_W5 {o['oppR_W5']:+.1f} oppS_W5 {o['oppS_W5']:+.1f}"
              f" | rho {o['rho1']:+.4f} (corr {o['rho1_corr']:+.4f}) n* {o['n_detect']:.0f}/{o['n_detect_corr']:.0f}"
              f" | slope {o['slope']:.2f} | P10 {s['real_P10']:.3f}/{s['shuf_P10']:.3f} longest {s['real_mean_longest']:.2f}/{s['shuf_mean_longest']:.2f}"
              f" | wl4 {s['real_wl4']:.2f}/{s['shuf_wl4']:.2f} wl5 {s['real_wl5']:.3f}/{s['shuf_wl5']:.3f}"
              + (f" | mates_W5 {o['mates_W5']:+.1f} enemy-own_W5 {o['oppR_W5']:+.1f} weakest {o['weakest_mate_loss']:.3f}/{o['weakest_mate_win']:.3f}" if 'mates_W5' in o else "")
              + f" | trace {tr[::max(1,len(tr)//6)]}", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "A":
        partA()
    elif sys.argv[1] == "list":
        print(" ".join(SCEN))
    else:
        runB(sys.argv[2:])
