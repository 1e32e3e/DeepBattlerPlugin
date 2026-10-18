#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
streaks_sim.py -- "Elo feeling" study (part 3 of 4): can pure randomness and HONEST
rating-based matchmaking produce long losing streaks and "win streak followed by
losing streak" (连胜后连败) without any manipulation?

Part A  (exact math, no simulation):
    * longest losing streak distribution for n iid games with win prob p
      (Markov-chain DP, exact) + Schilling (1990) asymptotic approximation
    * P(at least one losing streak >= r), expected number of such streaks
    * P(pattern  W^k L^k  occurs) exactly (KMP automaton DP)
    * longest streak of EITHER kind (fair coin, exact)
    * sliding-window "Elo hell" probabilities (Monte Carlo)
    * 5v5 team-game win probability vs individual skill edge (closed form)

Part B  (agent-based Monte Carlo of a whole player population):
    scenarios (a)..(f): random matching, honest Elo SBMM with K=10/16/32/64,
    AR(1) form/mood fluctuation, tilt, 5v5 team games, win-streak bonus feeding
    into MMR, and a deliberately MANIPULATED streak-aware matchmaker.
    Metrics: P(win | last k games all W/L) for k=1..6 (pooled, and within-player
    excess that removes the player-mix / composition effect), rating overshoot,
    opponent-rating signature, streak-length distribution vs per-player shuffled
    baseline, runs test (Wald-Wolfowitz), lag-1 autocorrelation, detection power.

Usage:
    python3 streaks_sim.py              # full run (~ a few minutes on 4 cores)
    python3 streaks_sim.py --quick      # small smoke test
    python3 streaks_sim.py --out DIR    # where results.md / results.json go

Model conventions:
    * Elo logistic scale: P(A beats B) = 1 / (1 + 10^(-(sA - sB)/400)).
    * True skill theta_i ~ N(0, 200^2) Elo points, fixed unless AR(1)/tilt is on.
    * Every round all N players play one game (1v1 pairs or 5v5 lobbies).
    * Ratings start at 0 (population mean); burn-in rounds are discarded, so the
      measured phase is a converged / stationary Elo system.
    * Rating-based matching: sort players by (rating + N(0, 25^2) queue noise),
      pair neighbours (1v1) or cut into lobbies of 10 (5v5).
    * Team strength = mean of the 5 members' true strengths; team Elo expectation
      = logistic of the difference of team mean ratings; each member receives
      K*(S - E) (standard "individual Elo from team result").
Requires: numpy >= 1.20
"""
import argparse
import json
import math
import os
import time
from multiprocessing import Pool

import numpy as np

GAMMA = 0.5772156649015329
KMAX = 6


# =====================================================================
# Part A: exact run-length mathematics
# =====================================================================
def p_no_run(n, q, r):
    """P(no run of >= r consecutive losses in n iid games), loss prob q. Exact DP."""
    if r <= 0:
        return 0.0
    if r > n:
        return 1.0
    p = 1.0 - q
    s = np.zeros(r)
    s[0] = 1.0
    for _ in range(n):
        tot = s.sum()
        new = np.empty(r)
        new[0] = p * tot
        new[1:] = q * s[:-1]
        s = new
    return float(s.sum())


def longest_run_stats(n, q, rmax=80):
    """Exact distribution summary of the longest losing run L_n."""
    cdf_lt = {r: p_no_run(n, q, r) for r in range(1, rmax + 2)}  # P(L < r)
    tail = {r: 1.0 - cdf_lt[r] for r in cdf_lt}                   # P(L >= r)
    mean = sum(tail[r] for r in range(1, rmax + 1))
    second = sum((2 * r - 1) * tail[r] for r in range(1, rmax + 1))  # E[L^2]
    var = second - mean ** 2
    # quantiles: P(L <= r) = P(L < r+1)
    def quant(a):
        for r in range(0, rmax + 1):
            if cdf_lt[r + 1] >= a:
                return r
        return rmax
    return dict(mean=mean, sd=math.sqrt(max(var, 0)), median=quant(0.5),
                q05=quant(0.05), q95=quant(0.95), tail=tail)


def schilling_approx(n, q):
    """Schilling (1990) / Gordon-Schilling-Waterman (1986) approximation for the
    expected longest run of an event with prob q in n trials:
        E[R_n] ~ log_{1/q}(n(1-q)) + gamma/ln(1/q) - 1/2
        Var[R_n] ~ pi^2 / (6 ln^2(1/q)) + 1/12
    (small periodic terms r1(n), r2(n) are ignored)."""
    l = math.log(1.0 / q)
    e = math.log(n * (1 - q)) / l + GAMMA / l - 0.5
    v = math.pi ** 2 / (6 * l * l) + 1.0 / 12
    return e, math.sqrt(v), math.log(n * (1 - q)) / l


def expected_num_runs(n, q, r):
    """E[# maximal losing runs of length >= r] in n iid games = q^r [1 + (n-r) p]."""
    if r > n:
        return 0.0
    return q ** r * (1 + (n - r) * (1 - q))


def p_pattern(n, pattern, p_win):
    """Exact P(pattern, a string over {W,L}, appears as a contiguous block in n games)."""
    m = len(pattern)
    fail = [0] * m
    j = 0
    for i in range(1, m):
        while j > 0 and pattern[i] != pattern[j]:
            j = fail[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
        fail[i] = j

    def step(s, c):
        while s > 0 and pattern[s] != c:
            s = fail[s - 1]
        if pattern[s] == c:
            s += 1
        return s
    tw = [step(s, 'W') for s in range(m)]
    tl = [step(s, 'L') for s in range(m)]
    dist = np.zeros(m + 1)
    dist[0] = 1.0
    for _ in range(n):
        new = np.zeros(m + 1)
        new[m] = dist[m]
        for s in range(m):
            d = dist[s]
            if d:
                new[tw[s]] += d * p_win
                new[tl[s]] += d * (1 - p_win)
        dist = new
    return float(dist[m])


def window_probs(n, w, thresh_low, p, sims, rng):
    """MC: P(exists a window of w consecutive games with <= thresh_low wins)."""
    x = (rng.random((sims, n)) < p).astype(np.int16)
    cs = np.concatenate([np.zeros((sims, 1), np.int32), np.cumsum(x, axis=1, dtype=np.int32)], axis=1)
    ws = cs[:, w:] - cs[:, :-w]
    lo = (ws.min(axis=1) <= thresh_low).mean()
    hi = (ws.max(axis=1) >= w - thresh_low).mean()
    return float(lo), float(hi)


def mc_check_longest(n, q, sims, rng):
    """Monte Carlo cross-check of exact DP: mean longest losing run, P(>=5)."""
    loss = rng.random((sims, n)) < q
    cur = np.zeros(sims, np.int32)
    best = np.zeros(sims, np.int32)
    for t in range(n):
        cur = np.where(loss[:, t], cur + 1, 0)
        np.maximum(best, cur, out=best)
    return float(best.mean()), float((best >= 5).mean())


def part_a(quick=False):
    rng = np.random.default_rng(20261018)
    res = {}
    ps = [0.45, 0.50, 0.55]
    ns = [50, 100, 500, 1000]
    rows = []
    for p in ps:
        q = 1 - p
        for n in ns:
            st = longest_run_stats(n, q)
            ea, sda, lead = schilling_approx(n, q)
            rows.append(dict(p=p, n=n, mean=st['mean'], sd=st['sd'], median=st['median'],
                             q05=st['q05'], q95=st['q95'], schilling=ea, schilling_sd=sda,
                             schilling_lead=lead,
                             P5=st['tail'][5], P7=st['tail'][7], P10=st['tail'][10],
                             P12=st['tail'][12], P15=st['tail'][15],
                             E5=expected_num_runs(n, q, 5), E7=expected_num_runs(n, q, 7),
                             E10=expected_num_runs(n, q, 10)))
    res['longest'] = rows

    # Monte Carlo cross-check
    sims = 20000 if quick else 100000
    chk = []
    for p, n in [(0.5, 100), (0.45, 1000)]:
        m, p5 = mc_check_longest(n, 1 - p, sims, rng)
        exact = longest_run_stats(n, 1 - p)
        chk.append(dict(p=p, n=n, mc_mean=m, exact_mean=exact['mean'], mc_P5=p5, exact_P5=exact['tail'][5], sims=sims))
    res['mc_check'] = chk

    # longest run of EITHER kind (fair coin): 1 + longest run of "same-as-previous" in n-1 fair bits
    either = []
    for n in ns:
        st = longest_run_stats(n - 1, 0.5)
        either.append(dict(n=n, mean=st['mean'] + 1, median=st['median'] + 1, q95=st['q95'] + 1))
    res['either'] = either

    # pattern W^k L^k (a >=k win streak immediately followed by a >=k losing streak)
    pat = []
    for p in ps:
        for k in [3, 4, 5, 6]:
            for n in [50, 100, 500, 1000]:
                pat.append(dict(p=p, k=k, n=n, P=p_pattern(n, 'W' * k + 'L' * k, p)))
    res['pattern'] = pat

    # sliding windows ("Elo hell" stretches) at p = 0.5
    sims = 20000 if quick else 100000
    win = []
    for n in [100, 500, 1000]:
        for (w, t) in [(10, 2), (10, 3), (20, 6), (20, 7), (50, 20)]:
            lo, hi = window_probs(n, w, t, 0.5, sims if n < 1000 else sims // 2, rng)
            win.append(dict(n=n, w=w, t=t, P_low=lo, P_high=hi))
    res['windows'] = win

    # 5v5: win prob of a player who is D Elo better than each of the 9 others
    team = []
    for D in [50, 100, 200, 300, 400, 800]:
        p1 = 1 / (1 + 10 ** (-D / 400))
        p5 = 1 / (1 + 10 ** (-(D / 5) / 400))
        team.append(dict(D=D, p_1v1=p1, p_5v5=p5))
    res['team_edge'] = team

    # short sessions (one evening): P(at least one losing streak >= r)
    sess = []
    for p in ps:
        for n in [5, 10, 20, 30]:
            sess.append(dict(p=p, n=n, P3=1 - p_no_run(n, 1 - p, 3), P4=1 - p_no_run(n, 1 - p, 4), P5=1 - p_no_run(n, 1 - p, 5)))
    res['sessions'] = sess

    # expected number of "W>=k immediately followed by L>=k" episodes: (n-2k+1)(pq)^k
    res['wl_expected'] = [dict(p=p, k=k, n=n, E=max(n - 2 * k + 1, 0) * (p * (1 - p)) ** k)
                          for p in ps for k in [3, 4, 5] for n in [100, 1000]]

    # Miller & Sanjurjo (2018) streak-selection bias: a player looks at ONE finite history and
    # computes (#wins right after k straight wins) / (#times k straight wins occurred).
    # Under pure iid p = 0.5 the EXPECTED value of this per-history proportion is < 0.5.
    ms = []
    for n in [20, 50, 100, 200, 1000]:
        sims_ms = (5000 if quick else 40000) if n < 1000 else (2000 if quick else 10000)
        x = rng.random((sims_ms, n)) < 0.5
        for k in [1, 2, 3, 4, 5]:
            run = np.zeros(sims_ms, np.int32)
            hit = np.zeros(sims_ms, np.int32)
            succ = np.zeros(sims_ms, np.int32)
            for t in range(n):
                if t > 0:
                    cond = run >= k
                    hit += cond
                    succ += cond & x[:, t]
                run = np.where(x[:, t], run + 1, 0)
            ok = hit > 0
            ms.append(dict(n=n, k=k, E_phat=float((succ[ok] / hit[ok]).mean()), frac_defined=float(ok.mean()),
                           pooled=float(succ.sum() / hit.sum())))
    res['miller_sanjurjo'] = ms
    return res


# =====================================================================
# Part B: population Monte Carlo
# =====================================================================
def logistic10(d):
    return 1.0 / (1.0 + np.power(10.0, -d / 400.0))


def simulate(cfg):
    """Run one scenario; return a dict of summary statistics."""
    name = cfg['name']
    seed = cfg.get('seed', 1)
    rng = np.random.default_rng(seed)
    N = cfg.get('N', 10000)
    T = cfg.get('T', 2000)
    burn = cfg.get('burn', 1000)
    team = cfg.get('team', 1)
    match = cfg.get('match', 'rating')          # 'random' | 'rating'
    split = cfg.get('split', 'random')          # 5v5 team split: 'random' | 'balanced'
    K = cfg.get('K', 32.0)
    skill_sd = cfg.get('skill_sd', 200.0)
    match_noise = cfg.get('match_noise', 100.0)
    phi = cfg.get('ar_phi', 0.0)
    ar_sd = cfg.get('ar_sd', 0.0)
    tilt_delta = cfg.get('tilt_delta', 0.0)
    tilt_cap = cfg.get('tilt_cap', 3)
    bonus_thr = cfg.get('bonus_thr', 0)         # e.g. 3 -> 3rd+ consecutive win gets bonus
    bonus_mult = cfg.get('bonus_mult', 1.0)
    manip_k = cfg.get('manip_k', 0)             # streak length that triggers manipulation
    manip_delta = cfg.get('manip_delta', 0.0)   # matchmaking-key offset (Elo)
    manip_mode = cfg.get('manip_mode', 'key')   # 'key': shift whom you are queued with;
                                                # 'split' (5v5): balance teams on a streak-inflated MMR
                                                # so a win-streaker gets weaker teammates ("loser queue")

    assert N % (10 if team == 5 else 2) == 0
    theta = rng.normal(0.0, skill_sd, N)
    R = np.zeros(N)
    u = rng.normal(0.0, ar_sd, N) if ar_sd > 0 else np.zeros(N)
    eps_sd = ar_sd * math.sqrt(1 - phi ** 2) if ar_sd > 0 else 0.0
    streak = np.zeros(N, np.int32)

    O = np.zeros((T, N), np.int8)
    nb = 2 * KMAX + 1
    acc = {k: np.zeros(nb) for k in ['n', 'win', 'p', 'err', 'oppR', 'oppS', 'mateR', 'rel']}
    rel_ss = 0.0
    occ = np.zeros(nb * N, np.int64)
    psum = np.zeros(N)
    oRsum = np.zeros(N)
    oSsum = np.zeros(N)
    mRsum = np.zeros(N)
    ar_idx = np.arange(N)
    team_acc = dict(loss=0, loss_worstmate=0, win=0, win_worstmate=0,
                    loss_selfworst=0, win_selfworst=0, loss_weaker=0, win_weaker=0,
                    loss_bestopp=0, win_bestopp=0)
    half = N // 2

    own_p = np.empty(N)
    out = np.empty(N, bool)
    Eown = np.empty(N)
    oppR = np.empty(N)
    oppS = np.empty(N)
    mateR = np.zeros(N)

    for t in range(burn + T):
        tilt = tilt_delta * np.minimum(np.maximum(-streak, 0), tilt_cap) if tilt_delta > 0 else 0.0
        s = theta + u - tilt
        if match == 'random':
            order = rng.permutation(N)
        else:
            key = R + match_noise * rng.standard_normal(N)
            if manip_k > 0 and manip_mode == 'key':
                key = key + manip_delta * (streak >= manip_k) - manip_delta * (streak <= -manip_k)
            order = np.argsort(key, kind='stable')

        if team == 1:
            a = order[0::2]
            b = order[1::2]
            pa = logistic10(s[a] - s[b])
            wa = rng.random(half) < pa
            Ea = logistic10(R[a] - R[b])
            own_p[a] = pa; own_p[b] = 1 - pa
            out[a] = wa; out[b] = ~wa
            Eown[a] = Ea; Eown[b] = 1 - Ea
            oppR[a] = R[b] - R[a]; oppR[b] = R[a] - R[b]
            oppS[a] = s[b] - s[a]; oppS[b] = s[a] - s[b]
        else:
            lob = order.reshape(-1, 10)
            L = lob.shape[0]
            if split == 'random':
                perm = np.argsort(rng.random(lob.shape), axis=1)
                lob = np.take_along_axis(lob, perm, axis=1)
                A, B = lob[:, :5], lob[:, 5:]
            elif split == 'balanced_manip':  # snake draft on streak-ADJUSTED rating (manipulated)
                adj = R + manip_delta * (streak >= manip_k) - manip_delta * (streak <= -manip_k)
                ordl = np.argsort(adj[lob], axis=1)
                lob2 = np.take_along_axis(lob, ordl, axis=1)
                A, B = lob2[:, [0, 3, 4, 7, 8]], lob2[:, [1, 2, 5, 6, 9]]
            else:  # snake draft on the (noisy-)rating order inside the lobby
                A, B = lob[:, [0, 3, 4, 7, 8]], lob[:, [1, 2, 5, 6, 9]]
            sA, sB = s[A].mean(1), s[B].mean(1)
            pA = logistic10(sA - sB)
            wA = rng.random(L) < pA
            RA, RB = R[A].mean(1), R[B].mean(1)
            EA = logistic10(RA - RB)
            own_p[A] = pA[:, None]; own_p[B] = (1 - pA)[:, None]
            out[A] = wA[:, None]; out[B] = ~wA[:, None]
            Eown[A] = EA[:, None]; Eown[B] = (1 - EA)[:, None]
            oppR[A] = (RB - RA)[:, None]; oppR[B] = (RA - RB)[:, None]
            oppS[A] = (sB - sA)[:, None]; oppS[B] = (sA - sB)[:, None]
            # teammates' mean rating minus own rating
            sumRA, sumRB = R[A].sum(1), R[B].sum(1)
            mateR[A] = (sumRA[:, None] - R[A]) / 4 - R[A]
            mateR[B] = (sumRB[:, None] - R[B]) / 4 - R[B]
            if t >= burn:
                T10 = np.concatenate([A, B], axis=1)
                st10 = s[T10]
                wpos = st10.argmin(1)
                bpos = st10.argmax(1)
                cols = np.arange(10)[None, :]
                same_team = (wpos[:, None] < 5) == (cols < 5)
                worst_mate = same_team & (wpos[:, None] != cols)
                self_worst = (wpos[:, None] == cols)
                best_opp = ((bpos[:, None] < 5) != (cols < 5))
                won = np.concatenate([np.repeat(wA[:, None], 5, 1), np.repeat(~wA[:, None], 5, 1)], axis=1)
                weaker = np.concatenate([np.repeat((sA < sB)[:, None], 5, 1), np.repeat((sB < sA)[:, None], 5, 1)], axis=1)
                lost = ~won
                team_acc['loss'] += int(lost.sum()); team_acc['win'] += int(won.sum())
                team_acc['loss_worstmate'] += int((worst_mate & lost).sum())
                team_acc['win_worstmate'] += int((worst_mate & won).sum())
                team_acc['loss_selfworst'] += int((self_worst & lost).sum())
                team_acc['win_selfworst'] += int((self_worst & won).sum())
                team_acc['loss_weaker'] += int((weaker & lost).sum())
                team_acc['win_weaker'] += int((weaker & won).sum())
                team_acc['loss_bestopp'] += int((best_opp & lost).sum())
                team_acc['win_bestopp'] += int((best_opp & won).sum())

        if t >= burn:
            tt = t - burn
            O[tt] = out
            sidx = np.clip(streak, -KMAX, KMAX) + KMAX
            err = R - theta
            err = err - err.mean()
            acc['n'] += np.bincount(sidx, minlength=nb)
            acc['win'] += np.bincount(sidx, weights=out.astype(float), minlength=nb)
            acc['p'] += np.bincount(sidx, weights=own_p, minlength=nb)
            acc['err'] += np.bincount(sidx, weights=err, minlength=nb)
            acc['oppR'] += np.bincount(sidx, weights=oppR, minlength=nb)
            acc['oppS'] += np.bincount(sidx, weights=oppS, minlength=nb)
            acc['mateR'] += np.bincount(sidx, weights=mateR, minlength=nb)
            rel = oppS - oppR   # (R_self - R_opp) - (s_self - s_opp): how overrated I am vs my opponent(s)
            acc['rel'] += np.bincount(sidx, weights=rel, minlength=nb)
            rel_ss += float((rel * rel).sum())
            occ += np.bincount(sidx * N + ar_idx, minlength=nb * N)
            psum += own_p
            oRsum += oppR
            oSsum += oppS
            mRsum += mateR

        # rating update
        mult = 1.0
        if bonus_thr > 0:
            mult = np.where(out & (streak >= bonus_thr - 1), bonus_mult, 1.0)
        R = R + K * (out - Eown) * mult
        # streak update
        streak = np.where(out, np.where(streak > 0, streak + 1, 1), np.where(streak < 0, streak - 1, -1)).astype(np.int32)
        # AR(1) form update
        if ar_sd > 0:
            u = phi * u + eps_sd * rng.standard_normal(N)

    # ------------------------------------------------------------ summarise
    occ = occ.reshape(nb, N)
    pbar = psum / T
    wr = O.mean(axis=0)
    res = dict(name=name, cfg={k: v for k, v in cfg.items()})
    cond = []
    for state in ['W', 'L']:
        for k in range(1, KMAX + 1):
            idx = list(range(KMAX + k, nb)) if state == 'W' else list(range(0, KMAX - k + 1))
            n_ = acc['n'][idx].sum()
            o_ = occ[idx].sum(axis=0)
            base_p = float((o_ * pbar).sum() / o_.sum())
            base_w = float((o_ * wr).sum() / o_.sum())
            base_oR = float((o_ * oRsum / T).sum() / o_.sum())
            base_oS = float((o_ * oSsum / T).sum() / o_.sum())
            base_mR = float((o_ * mRsum / T).sum() / o_.sum())
            row = dict(state=state, k=k, n=int(n_),
                       P_win=float(acc['win'][idx].sum() / n_),
                       E_ptrue=float(acc['p'][idx].sum() / n_),
                       base_p=base_p, base_w=base_w,
                       excess=float(acc['p'][idx].sum() / n_ - base_p),
                       excess_emp=float(acc['win'][idx].sum() / n_ - base_w),
                       overshoot=float(acc['err'][idx].sum() / n_),
                       oppR=float(acc['oppR'][idx].sum() / n_),
                       oppS=float(acc['oppS'][idx].sum() / n_),
                       mateR=float(acc['mateR'][idx].sum() / n_),
                       rel_over=float(acc['rel'][idx].sum() / n_),
                       oppR_excess=float(acc['oppR'][idx].sum() / n_ - base_oR),
                       oppS_excess=float(acc['oppS'][idx].sum() / n_ - base_oS),
                       mateR_excess=float(acc['mateR'][idx].sum() / n_ - base_mR))
            cond.append(row)
    res['cond'] = cond
    res['overall_win'] = float(O.mean())

    # within-player lag-1 autocorrelation (pooled, centred by player mean)
    X = O.astype(np.float32) - wr[None, :].astype(np.float32)
    num = float((X[1:] * X[:-1]).sum())
    den = float((X * X).sum())
    rho = num / den if den > 0 else 0.0
    res['lag1_pooled'] = rho
    # per-player runs test (Wald-Wolfowitz)
    n1 = O.sum(axis=0).astype(float)
    n2 = T - n1
    runs = 1 + (O[1:] != O[:-1]).sum(axis=0)
    mu = 2 * n1 * n2 / T + 1
    var = 2 * n1 * n2 * (2 * n1 * n2 - T) / (T ** 2 * (T - 1))
    ok = var > 0
    Z = (runs[ok] - mu[ok]) / np.sqrt(var[ok])
    res['runs_Z_mean'] = float(Z.mean())
    res['runs_frac_sig'] = float((np.abs(Z) > 1.96).mean())
    res['runs_frac_streaky'] = float((Z < -1.96).mean())
    res['runs_frac_alternating'] = float((Z > 1.96).mean())
    res['n_detect_single_player'] = float(((1.959964 + 0.841621) / rho) ** 2) if abs(rho) > 1e-6 else float('inf')

    # streak-length distribution (first 1000 measured games) vs per-player shuffle
    Wn = min(1000, T)
    def streak_stats(M):
        cur_l = np.zeros(N, np.int32); cur_w = np.zeros(N, np.int32)
        prevw = np.zeros(N, np.int32); prevl = np.zeros(N, np.int32)
        best_l = np.zeros(N, np.int32); best_w = np.zeros(N, np.int32)
        cnt = {r: 0 for r in (3, 5, 7, 10)}
        pat_wl = {k: 0 for k in (3, 4, 5)}
        pat_lw = {k: 0 for k in (3, 4, 5)}
        for t in range(Wn):
            w = M[t] == 1
            to_l = (~w) & (cur_w > 0)
            prevw[to_l] = cur_w[to_l]
            to_w = w & (cur_l > 0)
            prevl[to_w] = cur_l[to_w]
            cur_w = np.where(w, cur_w + 1, 0)
            cur_l = np.where(w, 0, cur_l + 1)
            np.maximum(best_l, cur_l, out=best_l)
            np.maximum(best_w, cur_w, out=best_w)
            for r in cnt:
                cnt[r] += int(np.count_nonzero(cur_l == r))
            for k in pat_wl:
                pat_wl[k] += int(np.count_nonzero((cur_l == k) & (prevw >= k)))
                pat_lw[k] += int(np.count_nonzero((cur_w == k) & (prevl >= k)))
        scale = 1000.0 / Wn / N
        return dict(mean_longest_L=float(best_l.mean()), mean_longest_W=float(best_w.mean()),
                    p95_longest_L=float(np.percentile(best_l, 95)),
                    **{f'Lruns_ge{r}_per1000': cnt[r] * scale for r in cnt},
                    **{f'W{k}L{k}_per1000': pat_wl[k] * scale for k in pat_wl},
                    **{f'L{k}W{k}_per1000': pat_lw[k] * scale for k in pat_lw},
                    **{f'P_Lge{r}': float((best_l >= r).mean()) for r in (5, 7, 10)})
    st_real = streak_stats(O[:Wn])
    O_sh = rng.permuted(O[:Wn], axis=0)
    st_sh = streak_stats(O_sh)
    res['streaks_real'] = st_real
    res['streaks_shuffled'] = st_sh

    # individual win-rate dispersion
    res['wr_sd_T'] = float(wr.std())
    res['wr_frac_45_55'] = float(((wr >= 0.45) & (wr <= 0.55)).mean())
    res['wr_min_max'] = [float(wr.min()), float(wr.max())]
    w100 = O[:100].mean(axis=0)
    res['wr100_frac_le40'] = float((w100 <= 0.40).mean())
    res['wr100_frac_ge60'] = float((w100 >= 0.60).mean())
    res['corr_R_theta'] = float(np.corrcoef(R, theta)[0, 1])
    res['slope_R_on_theta'] = float(np.polyfit(theta, R, 1)[0])
    res['rel_err_sd'] = math.sqrt(rel_ss / (T * N))
    e = R - theta
    res['rating_err_sd'] = float((e - e.mean()).std())
    res['binom_sd_T'] = math.sqrt(0.25 / T)
    if team == 5:
        ta = team_acc
        res['team'] = dict(
            P_worst_is_teammate_given_loss=ta['loss_worstmate'] / ta['loss'],
            P_worst_is_teammate_given_win=ta['win_worstmate'] / ta['win'],
            P_self_is_worst_given_loss=ta['loss_selfworst'] / ta['loss'],
            P_self_is_worst_given_win=ta['win_selfworst'] / ta['win'],
            P_own_team_weaker_given_loss=ta['loss_weaker'] / ta['loss'],
            P_own_team_weaker_given_win=ta['win_weaker'] / ta['win'],
            P_best_is_opponent_given_loss=ta['loss_bestopp'] / ta['loss'],
            P_best_is_opponent_given_win=ta['win_bestopp'] / ta['win'])
    return res


def scenarios(quick=False):
    base = dict(N=2000 if quick else 10000, T=600 if quick else 2000, burn=400 if quick else 1500)
    S = [
        dict(name='A_random_fixed', match='random', K=32, seed=11),
        dict(name='B_elo_K10', match='rating', K=10, seed=12),
        dict(name='B_elo_K16', match='rating', K=16, seed=13),
        dict(name='B_elo_K32', match='rating', K=32, seed=14),
        dict(name='B_elo_K64', match='rating', K=64, seed=15),
        dict(name='C_random_AR60', match='random', K=32, ar_phi=0.9, ar_sd=60, seed=16),
        dict(name='C_elo32_AR60', match='rating', K=32, ar_phi=0.9, ar_sd=60, seed=17),
        dict(name='C_elo32_AR100', match='rating', K=32, ar_phi=0.95, ar_sd=100, seed=18),
        dict(name='C_random_tilt30', match='random', K=32, tilt_delta=30, tilt_cap=3, seed=19),
        dict(name='C_elo32_tilt30', match='rating', K=32, tilt_delta=30, tilt_cap=3, seed=20),
        dict(name='D_5v5_random_lobby', match='random', team=5, K=32, seed=21),
        dict(name='D_5v5_elo32_randsplit', match='rating', team=5, K=32, split='random', seed=22),
        dict(name='D_5v5_elo32_balanced', match='rating', team=5, K=32, split='balanced', seed=23),
        dict(name='E_elo32_streakbonus', match='rating', K=32, bonus_thr=3, bonus_mult=2.0, seed=24),
        dict(name='F_manip_elo32_k3_d100', match='rating', K=32, manip_k=3, manip_delta=100, seed=25),
        dict(name='F_manip_5v5_k3_d100', match='rating', team=5, K=32, split='random', manip_k=3, manip_delta=100, seed=26),
        dict(name='F_manip_5v5_teammates_k3_d300', match='rating', team=5, K=32, split='balanced_manip', manip_mode='split', manip_k=3, manip_delta=300, seed=27),
    ]
    for s in S:
        for k, v in base.items():
            s.setdefault(k, v)
        # 1v1: key noise 100 Elo; 5v5 lobbies: key noise 250 Elo. Both chosen because they give a
        # stationary rating scale (slope of rating on true skill stable between 1000 and 4000 burn-in
        # rounds); tighter windows let the global rating scale diffuse (neutral mode).
        s.setdefault('match_noise', 250.0 if s.get('team', 1) == 5 else 100.0)
    if quick:
        for s in S:
            if s.get('team', 1) == 5:
                s['N'] = 2000
    return S


# =====================================================================
# Reporting
# =====================================================================
def fmt_part_a(A):
    L = []
    L.append('### A1. Longest losing streak in n iid games (exact DP) vs Schilling approximation\n')
    L.append('| p(win) | n | E[longest L-streak] exact | Schilling approx | SD | median | 95th pct | P(>=5) | P(>=7) | P(>=10) | P(>=12) | E[#L-streaks>=5] | E[#>=7] | E[#>=10] |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for r in A['longest']:
        L.append(f"| {r['p']:.2f} | {r['n']} | {r['mean']:.2f} | {r['schilling']:.2f} | {r['sd']:.2f} | {r['median']} | {r['q95']} | "
                 f"{r['P5']:.3f} | {r['P7']:.3f} | {r['P10']:.4f} | {r['P12']:.4f} | {r['E5']:.2f} | {r['E7']:.2f} | {r['E10']:.3f} |")
    L.append('\nMonte Carlo cross-check of the exact DP:')
    for c in A['mc_check']:
        L.append(f"- p={c['p']}, n={c['n']}: MC mean {c['mc_mean']:.3f} vs exact {c['exact_mean']:.3f}; MC P(>=5) {c['mc_P5']:.4f} vs exact {c['exact_P5']:.4f} ({c['sims']} sims)")
    L.append('\n### A2. Longest streak of EITHER kind (W or L), p = 0.5 (exact)\n')
    L.append('| n | E[longest streak, either kind] | median | 95th pct |')
    L.append('|---|---|---|---|')
    for r in A['either']:
        L.append(f"| {r['n']} | {r['mean']:.2f} | {r['median']} | {r['q95']} |")
    L.append('\n### A3. P(a >=k win streak immediately followed by a >=k losing streak somewhere in n games) (exact, pattern W^k L^k)\n')
    L.append('| p(win) | k | n=50 | n=100 | n=500 | n=1000 |')
    L.append('|---|---|---|---|---|---|')
    pat = A['pattern']
    for p in [0.45, 0.5, 0.55]:
        for k in [3, 4, 5, 6]:
            vals = [x['P'] for x in pat if x['p'] == p and x['k'] == k]
            L.append(f"| {p:.2f} | {k} | " + ' | '.join(f'{v:.3f}' for v in vals) + ' |')
    L.append('\n### A4. Sliding-window "Elo hell" stretches at p = 0.5 (Monte Carlo)\n')
    L.append('| n games | window w | P(some window with <= t wins) | P(some window with >= w-t wins) | t |')
    L.append('|---|---|---|---|---|')
    for r in A['windows']:
        L.append(f"| {r['n']} | {r['w']} | {r['P_low']:.3f} | {r['P_high']:.3f} | {r['t']} |")
    L.append('\n### A4b. Short sessions: P(at least one losing streak >= r within one session of n games), exact\n')
    L.append('| p(win) | n | P(>=3) | P(>=4) | P(>=5) |')
    L.append('|---|---|---|---|---|')
    for r in A['sessions']:
        L.append(f"| {r['p']:.2f} | {r['n']} | {r['P3']:.3f} | {r['P4']:.3f} | {r['P5']:.3f} |")
    L.append('\n### A4c. Expected number of "W>=k immediately followed by L>=k" episodes = (n-2k+1)(pq)^k\n')
    L.append('| p(win) | k | per 100 games | per 1000 games |')
    L.append('|---|---|---|---|')
    for p in [0.45, 0.5, 0.55]:
        for k in [3, 4, 5]:
            v = {x['n']: x['E'] for x in A['wl_expected'] if x['p'] == p and x['k'] == k}
            L.append(f"| {p:.2f} | {k} | {v[100]:.3f} | {v[1000]:.2f} |")
    L.append('\n### A4d. Miller-Sanjurjo bias: expected per-history P-hat(win | previous k wins) under iid p = 0.5 (Monte Carlo)\n')
    L.append('| n games in history | k=1 | k=2 | k=3 | k=4 | k=5 | (pooled over all histories, k=3) |')
    L.append('|---|---|---|---|---|---|---|')
    for n in [20, 50, 100, 200, 1000]:
        v = {x['k']: x for x in A['miller_sanjurjo'] if x['n'] == n}
        L.append(f"| {n} | " + ' | '.join(f"{v[k]['E_phat']:.3f}" for k in [1, 2, 3, 4, 5]) + f" | {v[3]['pooled']:.3f} |")
    L.append('\n### A5. How much one player matters: win prob when you are D Elo better than every other player\n')
    L.append('| D | 1v1 | 5v5 (team strength = mean of 5) |')
    L.append('|---|---|---|')
    for r in A['team_edge']:
        L.append(f"| {r['D']} | {r['p_1v1']:.3f} | {r['p_5v5']:.3f} |")
    return '\n'.join(L)


def fmt_part_b(B):
    L = []
    L.append('### B1. P(win next | last k games all wins / all losses), pooled over all players (empirical frequency)\n')
    L.append('| scenario | overall | W1 | W2 | W3 | W4 | W5 | W6 | L1 | L2 | L3 | L4 | L5 | L6 |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for r in B:
        c = {(x['state'], x['k']): x for x in r['cond']}
        L.append(f"| {r['name']} | {r['overall_win']:.3f} | " + ' | '.join(f"{c[('W', k)]['P_win']:.3f}" for k in range(1, 7)) + ' | ' +
                 ' | '.join(f"{c[('L', k)]['P_win']:.3f}" for k in range(1, 7)) + ' |')
    L.append('\n### B2. Within-player EXCESS win probability after streaks (E[true p | state] minus the same players\' own average; removes the player-mix effect), percentage points\n')
    L.append('| scenario | W1 | W2 | W3 | W4 | W5 | W6 | L1 | L2 | L3 | L4 | L5 | L6 |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for r in B:
        c = {(x['state'], x['k']): x for x in r['cond']}
        L.append(f"| {r['name']} | " + ' | '.join(f"{100 * c[('W', k)]['excess']:+.1f}" for k in range(1, 7)) + ' | ' +
                 ' | '.join(f"{100 * c[('L', k)]['excess']:+.1f}" for k in range(1, 7)) + ' |')
    L.append('\n### B3. Mechanism / manipulation signature after streaks (Elo points, means)\n')
    L.append('| scenario | relative overshoot (R_me-R_opp)-(s_me-s_opp) after W3 | after W5 | after L3 | after L5 | opp rating minus own, within-player excess, after W3 | after W5 | after L3 | after L5 | opp TRUE strength minus own, within-player excess, after W5 | after L5 |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|')
    for r in B:
        c = {(x['state'], x['k']): x for x in r['cond']}
        L.append(f"| {r['name']} | {c[('W', 3)]['rel_over']:+.0f} | {c[('W', 5)]['rel_over']:+.0f} | {c[('L', 3)]['rel_over']:+.0f} | {c[('L', 5)]['rel_over']:+.0f} | "
                 f"{c[('W', 3)]['oppR_excess']:+.1f} | {c[('W', 5)]['oppR_excess']:+.1f} | {c[('L', 3)]['oppR_excess']:+.1f} | {c[('L', 5)]['oppR_excess']:+.1f} | "
                 f"{c[('W', 5)]['oppS_excess']:+.1f} | {c[('L', 5)]['oppS_excess']:+.1f} |")
    L.append('\n### B4. Streak-length distribution (per player, first 1000 measured games) vs. the SAME outcomes shuffled within player (iid baseline)\n')
    L.append('| scenario | mean longest L-streak (real / shuffled) | P(L-streak>=7) | P(L-streak>=10) | #L-streaks>=5 per 1000 | #L-streaks>=7 per 1000 | #"W>=4 then L>=4" per 1000 | #"W>=5 then L>=5" per 1000 |')
    L.append('|---|---|---|---|---|---|---|---|')
    for r in B:
        a, b = r['streaks_real'], r['streaks_shuffled']
        L.append(f"| {r['name']} | {a['mean_longest_L']:.2f} / {b['mean_longest_L']:.2f} | {a['P_Lge7']:.3f} / {b['P_Lge7']:.3f} | {a['P_Lge10']:.3f} / {b['P_Lge10']:.3f} | "
                 f"{a['Lruns_ge5_per1000']:.2f} / {b['Lruns_ge5_per1000']:.2f} | {a['Lruns_ge7_per1000']:.2f} / {b['Lruns_ge7_per1000']:.2f} | "
                 f"{a['W4L4_per1000']:.2f} / {b['W4L4_per1000']:.2f} | {a['W5L5_per1000']:.3f} / {b['W5L5_per1000']:.3f} |")
    L.append('\n### B5. Statistical tests within player (T measured games per player)\n')
    L.append('| scenario | lag-1 autocorr (pooled within-player) | runs-test mean Z | % players |Z|>1.96 | % streaky (Z<-1.96) | % alternating (Z>1.96) | games one player needs to detect rho (alpha .05, power .8) |')
    L.append('|---|---|---|---|---|---|---|')
    for r in B:
        L.append(f"| {r['name']} | {r['lag1_pooled']:+.4f} | {r['runs_Z_mean']:+.2f} | {100 * r['runs_frac_sig']:.1f} | {100 * r['runs_frac_streaky']:.1f} | {100 * r['runs_frac_alternating']:.1f} | {r['n_detect_single_player']:.0f} |")
    L.append('\n### B6. Individual win-rate dispersion & rating quality\n')
    L.append('| scenario | SD of player win rate over T games (binomial SD) | % players with 45-55% over T | % players <=40% in first 100 games | % >=60% in first 100 | corr(rating, true skill) | slope of rating on true skill | SD of relative error vs opponent |')
    L.append('|---|---|---|---|---|---|---|---|')
    for r in B:
        L.append(f"| {r['name']} | {r['wr_sd_T']:.3f} ({r['binom_sd_T']:.3f}) | {100 * r['wr_frac_45_55']:.1f} | {100 * r['wr100_frac_le40']:.1f} | {100 * r['wr100_frac_ge60']:.1f} | {r['corr_R_theta']:.3f} | {r['slope_R_on_theta']:.2f} | {r['rel_err_sd']:.0f} |")
    tm = [r for r in B if 'team' in r]
    if tm:
        L.append('\n### B3b. 5v5 teammate signature (within-player excess, Elo points): teammates\' mean rating minus my rating; enemy-team mean rating minus my-team mean rating\n')
        L.append('| scenario | teammates-minus-me after W3 | after W5 | after L3 | after L5 | enemy-minus-my-team after W3 | after W5 | after L3 | after L5 |')
        L.append('|---|---|---|---|---|---|---|---|---|')
        for r in tm:
            c = {(x['state'], x['k']): x for x in r['cond']}
            L.append(f"| {r['name']} | " + ' | '.join(f"{c[(st, k)]['mateR_excess']:+.1f}" for st, k in [('W', 3), ('W', 5), ('L', 3), ('L', 5)]) + ' | ' +
                     ' | '.join(f"{c[(st, k)]['oppR_excess']:+.1f}" for st, k in [('W', 3), ('W', 5), ('L', 3), ('L', 5)]) + ' |')
        L.append('\n### B7. 5v5 attribution: who is the weakest / strongest player in the lobby?\n')
        L.append('| scenario | P(weakest of 10 is MY TEAMMATE given loss) | given win | P(I am the weakest given loss) | given win | P(my team truly weaker given loss) | given win | P(strongest of 10 is an OPPONENT given loss) | given win |')
        L.append('|---|---|---|---|---|---|---|---|---|')
        for r in tm:
            t = r['team']
            L.append(f"| {r['name']} | {t['P_worst_is_teammate_given_loss']:.3f} | {t['P_worst_is_teammate_given_win']:.3f} | {t['P_self_is_worst_given_loss']:.3f} | {t['P_self_is_worst_given_win']:.3f} | "
                     f"{t['P_own_team_weaker_given_loss']:.3f} | {t['P_own_team_weaker_given_win']:.3f} | {t['P_best_is_opponent_given_loss']:.3f} | {t['P_best_is_opponent_given_win']:.3f} |")
    L.append('\n### Scenario parameters\n')
    L.append('| scenario | match | team | K | queue noise (Elo) | AR(1) phi / sd | tilt (Elo per loss, cap) | streak bonus | manipulation | N | burn-in | T |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|---|')
    for r in B:
        c = r['cfg']
        L.append(f"| {r['name']} | {c.get('match')} | {'5v5 ' + c.get('split', 'random') if c.get('team', 1) == 5 else '1v1'} | {c.get('K')} | {c.get('match_noise')} | "
                 f"{c.get('ar_phi', 0)} / {c.get('ar_sd', 0)} | {c.get('tilt_delta', 0)}, {c.get('tilt_cap', 3) if c.get('tilt_delta', 0) else '-'} | "
                 f"{('x' + str(c.get('bonus_mult')) + ' from win #' + str(c.get('bonus_thr'))) if c.get('bonus_thr', 0) else '-'} | "
                 f"{((('key +/-' if c.get('manip_mode', 'key') == 'key' else 'team-split MMR +/-') + str(c.get('manip_delta')) + ' when streak>=' + str(c.get('manip_k')))) if c.get('manip_k', 0) else '-'} | {c.get('N')} | {c.get('burn')} | {c.get('T')} |")
    return '\n'.join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quick', action='store_true')
    ap.add_argument('--out', default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument('--procs', type=int, default=4)
    args = ap.parse_args()
    t0 = time.time()
    A = part_a(args.quick)
    print(f'Part A done in {time.time() - t0:.1f}s', flush=True)
    S = scenarios(args.quick)
    with Pool(args.procs) as pool:
        B = pool.map(simulate, S)
    print(f'Part B done in {time.time() - t0:.1f}s', flush=True)
    md = '## Part A (exact math)\n\n' + fmt_part_a(A) + '\n\n## Part B (population Monte Carlo)\n\n' + fmt_part_b(B) + '\n'
    with open(os.path.join(args.out, 'results.md'), 'w') as f:
        f.write(md)
    with open(os.path.join(args.out, 'results.json'), 'w') as f:
        json.dump(dict(A=A, B=B), f, indent=1, default=lambda o: None)
    print(md)


if __name__ == '__main__':
    main()
