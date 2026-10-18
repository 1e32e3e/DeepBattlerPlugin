#!/usr/bin/env python3
"""
winrate_sim.py -- Monte Carlo study of win rates under NON-manipulated matchmaking.

Part 2 of the "Elo mechanisms in games" study.

Model (all quantities on the Elo scale, 400 points = 10:1 odds):
  * N players, true (latent) skill s_i ~ Normal(1500, SKILL_SD^2), fixed unless a
    scenario adds drift / improvement.
  * 1v1 truth model (Bradley-Terry / Elo logistic, i.e. the rating model is well specified):
        P(i beats j) = F(s_i - s_j),   F(d) = 1 / (1 + 10^(-d/400)).
    Optional extra per-game "form" noise: s_i is replaced by s_i + x_i, x_i ~ N(0, NOISE_SD^2)
    drawn independently for every player in every game.
    Optional autocorrelated form (tilt/fatigue/mood): s_i(t) = s_i + u_i(t),
        u_i(t+1) = phi*u_i(t) + sqrt(1-phi^2)*DRIFT_SD*z,  z ~ N(0,1)  (AR(1), stationary sd DRIFT_SD).
  * n-v-n team truth model ("additive performance", logistic analogue of TrueSkill's sum of
    performances):  P(team A wins) = F( (sum_A s - sum_B s) / sqrt(n) ).
    Variant "mean": P(A wins) = F( mean_A s - mean_B s ).
  * 8-player free-for-all: performance = s_i + Gumbel noise with scale 400/ln10, so the finishing
    order is exactly Plackett-Luce with worths 10^(s_i/400) and every pairwise marginal is Elo.
  * Rating system: plain Elo, everyone starts at 1500, K in {16, 32}.
      1v1:   R_a += K (S - F(R_a - R_b))
      team:  each member gets K (S - F((sum_A R - sum_B R)/sqrt(n)))   (or mean variant)
      FFA:   R_i += K/(M-1) * sum_j (S_ij - F(R_i - R_j)),  S_ij = 1 if i finished ahead of j.
  * Matchmaking (no manipulation):
      'random' : opponents (and teammates) drawn uniformly from the whole population each round.
      'sbmm'   : honest rating-based matchmaking: sort by R + N(0, QUEUE_SD^2) (queue jitter),
                 group adjacent players; 5v5 teams are formed by snake draft inside the group of 10
                 (so the expected score is ~0.5); no hidden variables are used.
                 Main runs use QUEUE_SD = 100 ("normal SBMM"); "strict SBMM" uses QUEUE_SD = 20.
  * Every round every player plays exactly one game.

Outputs markdown tables to stdout (and results.md next to this script).
Run:  python3 winrate_sim.py            (full run, ~ a few minutes)
      python3 winrate_sim.py --quick    (smaller run for testing)
"""
import argparse
import math
import os
import sys
import time

import numpy as np

LN10 = math.log(10.0)
SCALE = 400.0 / LN10           # logistic scale of Elo, 173.72 points
C0 = LN10 / 1600.0             # F'(0) = slope of Elo expectation at d = 0, per point


def F(d):
    return 1.0 / (1.0 + np.power(10.0, -d / 400.0))


def Phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


# ----------------------------------------------------------------------------------------------
# core simulator
# ----------------------------------------------------------------------------------------------
class Sim:
    def __init__(self, n_players=10000, skill_sd=200.0, K=16.0, fmt='1v1', mm='random',
                 noise_sd=0.0, drift_sd=0.0, drift_phi=0.99, team_model='sum', queue_sd=100.0,
                 seed=1):
        self.N = n_players
        self.K = K
        self.fmt = fmt
        self.mm = mm
        self.noise_sd = noise_sd
        self.drift_sd = drift_sd
        self.drift_phi = drift_phi
        self.team_model = team_model
        self.queue_sd = queue_sd
        self.rng = np.random.default_rng(seed)
        self.s = 1500.0 + skill_sd * self.rng.standard_normal(self.N)
        self.u = (drift_sd * self.rng.standard_normal(self.N)) if drift_sd > 0 else np.zeros(self.N)
        self.R = np.full(self.N, 1500.0)
        self.extra = np.zeros(self.N)          # deterministic skill change (improvement scenario)
        self.group = {'1v1': 2, '5v5': 10, 'ffa8': 8}[fmt]
        assert self.N % self.group == 0

    def cur_skill(self):
        return self.s + self.extra + self.u

    def order(self):
        if self.mm == 'random':
            return self.rng.permutation(self.N)
        return np.argsort(self.R + self.queue_sd * self.rng.standard_normal(self.N))

    def step(self):
        """Play one round. Returns (score array S in [0,1] per player, aux dict)."""
        rng = self.rng
        sk = self.cur_skill()
        if self.noise_sd > 0:
            sk = sk + self.noise_sd * rng.standard_normal(self.N)
        perm = self.order()
        S = np.zeros(self.N)
        aux = {}
        if self.fmt == '1v1':
            a, b = perm[0::2], perm[1::2]
            p = F(sk[a] - sk[b])
            w = (rng.random(a.size) < p).astype(float)
            e = F(self.R[a] - self.R[b])
            d = self.K * (w - e)
            self.R[a] += d
            self.R[b] -= d
            S[a] = w
            S[b] = 1.0 - w
            E = np.zeros(self.N); E[a] = e; E[b] = 1 - e
            aux['E'] = E
        elif self.fmt == '5v5':
            g = perm.reshape(-1, 10)
            if self.mm == 'random':
                A, B = g[:, :5], g[:, 5:]
            else:  # snake draft on (noisy-sorted) rating -> balanced teams
                A, B = g[:, [0, 3, 4, 7, 8]], g[:, [1, 2, 5, 6, 9]]
            if self.team_model == 'sum':
                dt = (sk[A].sum(1) - sk[B].sum(1)) / math.sqrt(5.0)
                dr = (self.R[A].sum(1) - self.R[B].sum(1)) / math.sqrt(5.0)
            else:
                dt = sk[A].mean(1) - sk[B].mean(1)
                dr = self.R[A].mean(1) - self.R[B].mean(1)
            p = F(dt)
            w = (rng.random(p.size) < p).astype(float)
            e = F(dr)
            d = self.K * (w - e)
            self.R[A] += d[:, None]
            self.R[B] -= d[:, None]
            S[A] = w[:, None]
            S[B] = 1.0 - w[:, None]
            E = np.zeros(self.N); E[A] = e[:, None]; E[B] = (1 - e)[:, None]
            aux['E'] = E
        else:  # ffa8
            g = perm.reshape(-1, 8)
            gum = -np.log(-np.log(rng.random(g.shape)))           # standard Gumbel
            perf = sk[g] + SCALE * gum
            # place: 1 = best
            rank = (-perf).argsort(1).argsort(1) + 1
            Rg = self.R[g]
            Sij = (perf[:, :, None] > perf[:, None, :]).astype(float)
            Eij = F(Rg[:, :, None] - Rg[:, None, :])
            idx = np.arange(8)
            Sij[:, idx, idx] = 0.0
            Eij[:, idx, idx] = 0.0
            dR = self.K / 7.0 * (Sij.sum(2) - Eij.sum(2))
            self.R[g] += dR
            place = np.zeros(self.N, dtype=int)
            place[g] = rank
            aux['place'] = place
            S = (place == 1).astype(float)                          # "win" = 1st place
            aux['top4'] = (place <= 4).astype(float)
        # skill drift update (after the game)
        if self.drift_sd > 0:
            ph = self.drift_phi
            self.u = ph * self.u + math.sqrt(1 - ph * ph) * self.drift_sd * rng.standard_normal(self.N)
        return S, aux


def rating_error(sim, ref=None):
    """Centered rating error R - s (Elo is zero-sum so only differences are identified)."""
    ref = sim.s + sim.extra if ref is None else ref
    e = sim.R - ref
    return e - e.mean()


def deciles(x):
    q = np.quantile(x, np.linspace(0, 1, 11))
    return np.clip(np.searchsorted(q, x, side='right') - 1, 0, 9)


# ----------------------------------------------------------------------------------------------
# experiments
# ----------------------------------------------------------------------------------------------
def run_standard(label, rounds, burn, **kw):
    t0 = time.time()
    sim = Sim(**kw)
    N = sim.N
    wins = np.zeros(N); games = 0; top4 = np.zeros(N); place_sum = np.zeros(N)
    rmse = []
    err_acc = []
    ewin = np.zeros(N)
    # for drift scenario: outcome series for autocorr / window variance
    win_windows = []
    wwin = np.zeros(N)
    R_burn = None
    slope_traj = {}
    for t in range(rounds):
        if t == burn:
            R_burn = sim.R.copy()
        S, aux = sim.step()
        if (t + 1) in (250, 500, 1000, 2000, 3000):
            slope_traj[t + 1] = float(np.polyfit(sim.s, sim.R, 1)[0])
        e = rating_error(sim)
        rmse.append(math.sqrt(np.mean(e * e)))
        if t >= burn:
            wins += S; games += 1
            if 'top4' in aux:
                top4 += aux['top4']; place_sum += aux['place']
            if 'E' in aux:
                ewin += aux['E']
            if (t - burn) % 50 == 0:
                if kw.get('drift_sd', 0) > 0:
                    err_acc.append(rating_error(sim, sim.cur_skill()).std())
                else:
                    err_acc.append(e.std())
            wwin += S
            if (t - burn + 1) % 100 == 0:
                win_windows.append(wwin / 100.0)
                wwin = np.zeros(N)
    wr = wins / games
    dec = deciles(sim.s)
    rows = []
    for d in range(10):
        m = dec == d
        r = {'dec': d + 1, 'skill': sim.s[m].mean(), 'wr': wr[m].mean(),
             'p10': np.quantile(wr[m], 0.1), 'p90': np.quantile(wr[m], 0.9),
             'rating': sim.R[m].mean(),
             'E': (ewin / games)[m].mean() if sim.fmt != 'ffa8' else float('nan'),
             'dRKT': ((sim.R - R_burn) / (sim.K * games))[m].mean()}
        if sim.fmt == 'ffa8':
            r['top4'] = (top4 / games)[m].mean()
            r['place'] = (place_sum / games)[m].mean()
        rows.append(r)
    top1 = sim.s >= np.quantile(sim.s, 0.99)
    bot1 = sim.s <= np.quantile(sim.s, 0.01)
    stat_rmse = float(np.mean(rmse[burn:]))
    # convergence: first round where rmse <= 1.1 * stationary level; and e-folding of the excess
    conv = next((i + 1 for i, v in enumerate(rmse) if v <= 1.1 * stat_rmse), None)
    conv2 = next((i + 1 for i, v in enumerate(rmse) if v <= 2.0 * stat_rmse), None)
    slope, icpt = np.polyfit(sim.s, sim.R, 1)
    corr = np.corrcoef(sim.s, sim.R)[0, 1]
    resid_sd = float((sim.R - (slope * sim.s + icpt)).std())
    res = dict(label=label, rows=rows, games=games, stat_err_sd=float(np.mean(err_acc)),
               stat_rmse=stat_rmse, conv11=conv, conv2=conv2, slope=slope, corr=corr,
               top1=wr[top1].mean(), bot1=wr[bot1].mean(), rmse=rmse, kw=kw,
               wr_sd=wr.std(), secs=time.time() - t0, resid_sd=resid_sd, slope_traj=slope_traj,
               mean_E=(ewin / games).mean() if (games and sim.fmt != 'ffa8') else None)
    if win_windows:
        W = np.array(win_windows)        # (windows, N)
        # within-player variance of 100-game win rates, relative to binomial with the player's own p
        p = wr
        var_obs = W.var(0, ddof=1)
        var_bin = p * (1 - p) / 100.0
        res['var_ratio'] = float(np.mean(var_obs) / np.mean(var_bin))
        res['frac60'] = float(np.mean(W >= 0.60))
        res['frac40'] = float(np.mean(W <= 0.40))
    return res, sim


def calib(sim, ref, mask=None):
    """Fit R = a*ref + b on the players in mask (default: all). Returns (a, b).
    Needed because under tight SBMM the global rating scale is only weakly identified (it stretches),
    so errors are measured against the population's own rating-vs-skill line."""
    m = slice(None) if mask is None else mask
    a, b = np.polyfit(ref[m], sim.R[m], 1)
    return a, b


def run_drift_extra(K, rounds, burn, seed=7, phi=0.99, sd=100.0, n_players=10000, queue_sd=100.0):
    """Autocorrelated form u(t) under SBMM: outcome autocorrelation, hot/cold win rates,
    and how much of u the rating tracks."""
    sim = Sim(n_players=n_players, K=K, fmt='1v1', mm='sbmm', drift_sd=sd, drift_phi=phi, seed=seed,
              queue_sd=queue_sd)
    sub = np.arange(min(2000, n_players))
    Ws, Us, Es = [], [], []
    for t in range(rounds):
        u_before = sim.u.copy()
        S, aux = sim.step()
        if t >= burn:
            Ws.append(S[sub]); Us.append(u_before[sub])
            if (t - burn) % 10 == 0:
                cur = sim.s + u_before
                a, b = calib(sim, sim.s)          # line fitted on long-run skill
                # rating error (in skill units) relative to CURRENT skill
                Es.append(((sim.R - b) / a - cur)[sub])
    W = np.array(Ws); U = np.array(Us); E = np.array(Es)
    x = W - W.mean(0)
    ac = [float(np.mean(x[lag:] * x[:-lag]) / np.mean(x * x)) for lag in (1, 5, 20)]
    hot = U > sd; cold = U < -sd
    Usub = U[::10][:E.shape[0]]
    # regression of (rating-implied skill - long-run skill) on u: share of the form the rating has absorbed
    absorbed = float(np.polyfit(Usub.ravel(), (E + Usub).ravel(), 1)[0])
    return dict(K=K, ac=ac, wr_hot=float(W[hot].mean()), wr_cold=float(W[cold].mean()),
                err_sd_cur=float(E.std()), absorbed=absorbed)


def run_improve(K, rounds=2600, burn=1000, imp_games=600, imp_total=300.0, frac=0.1, seed=11,
                n_players=10000, queue_sd=100.0):
    """A random 10% cohort improves linearly by imp_total points over imp_games games (SBMM 1v1)."""
    sim = Sim(n_players=n_players, K=K, fmt='1v1', mm='sbmm', seed=seed, queue_sd=queue_sd)
    rng = np.random.default_rng(seed + 1)
    coh = rng.choice(sim.N, int(frac * sim.N), replace=False)
    mask = np.zeros(sim.N, bool); mask[coh] = True
    v = imp_total / imp_games
    acc = {'trans': [], 'steady': [], 'after': [], 'E': [], 'Eafter': []}
    lags, lams = [], []
    for t in range(rounds):
        if burn <= t < burn + imp_games:
            sim.extra[mask] += v
        S, aux = sim.step()
        if burn <= t < burn + 100:
            acc['trans'].append(S[mask].mean())
        elif burn + 100 <= t < burn + imp_games:
            acc['steady'].append(S[mask].mean())
            acc['E'].append(aux['E'][mask].mean())
            if t % 10 == 0:
                cur = sim.s + sim.extra
                a, b = calib(sim, cur, ~mask)    # rating-vs-skill line of the NON-improving players
                lags.append(float(np.mean(cur[mask] - (sim.R[mask] - b) / a)))   # in skill points
                lams.append(a)
        elif burn + imp_games <= t < burn + imp_games + 200:
            acc['after'].append(S[mask].mean())
            acc['Eafter'].append(aux['E'][mask].mean())
    lam = float(np.mean(lams))
    return dict(K=K, v=v, wr_trans=float(np.mean(acc['trans'])), wr_steady=float(np.mean(acc['steady'])),
                wr_after=float(np.mean(acc['after'])), lag=float(np.mean(lags)), lam=lam,
                E_steady=float(np.mean(acc['E'])), E_after=float(np.mean(acc['Eafter'])),
                theory_excess=lam * v / K, theory_lag=lam * v / (K * C0))


def run_reset(K, rounds_burn=1000, follow=400, seed=21, n_players=10000, mm='sbmm', queue_sd=100.0):
    """Equilibrate, then reset the ratings of 500 top-decile players to 1500 ("new account"/"smurf")."""
    sim = Sim(n_players=n_players, K=K, fmt='1v1', mm=mm, seed=seed, queue_sd=queue_sd)
    for t in range(rounds_burn):
        sim.step()
    rng = np.random.default_rng(seed + 5)
    topdec = np.where(sim.s >= np.quantile(sim.s, 0.9))[0]
    coh = rng.choice(topdec, min(500, topdec.size), replace=False)
    mask = np.zeros(sim.N, bool); mask[coh] = True
    a, b = calib(sim, sim.s, ~mask)
    target = a * sim.s[coh] + b              # where these players' ratings were calibrated to be
    sim.R[coh] = 1500.0
    traj, wins = [], []
    for t in range(follow):
        traj.append(float(np.mean(target - sim.R[coh])) / a)          # remaining gap, skill units
        S, aux = sim.step()
        wins.append(S[coh].mean())
    traj = np.array(traj); gap0 = traj[0]
    g50 = int(np.argmax(traj <= 0.5 * gap0))
    g90 = int(np.argmax(traj <= 0.1 * gap0))
    return dict(K=K, gap0=gap0, g50=g50, g90=g90, wr50=float(np.mean(wins[:50])),
                wr100=float(np.mean(wins[:100])), wr_last=float(np.mean(wins[-100:])),
                tau=1.0 / (K * C0))


def run_stretch(K, queue_sd, rounds, n_players, seed=5):
    """Rating-scale identifiability: slope of R on s over time for a given matchmaking tightness."""
    sim = Sim(n_players=n_players, K=K, fmt='1v1', mm='sbmm', queue_sd=queue_sd, seed=seed)
    out = {}
    for t in range(1, rounds + 1):
        sim.step()
        if t in (250, 500, 1000, 2000, 3000):
            a, b = np.polyfit(sim.s, sim.R, 1)
            out[t] = (a, float((sim.R - (a * sim.s + b)).std()))
    return out


# ----------------------------------------------------------------------------------------------
# analytic helpers
# ----------------------------------------------------------------------------------------------
def analytic_random_1v1(z, skill_sd=200.0, noise_sd=0.0):
    """Normal approximation: F(d) ~ Phi(d/295.7); opponents ~ N(mu, skill_sd^2)."""
    s_eff = math.sqrt((SCALE * 1.702) ** 2 + 2 * noise_sd ** 2)
    return Phi(z * skill_sd / math.sqrt(s_eff ** 2 + skill_sd ** 2))


def analytic_random_team(z, n=5, skill_sd=200.0, model='sum'):
    """Additive model: P = F(D/sqrt(n)), D ~ N(z*sd, (2n-1) sd^2)."""
    s_eff = SCALE * 1.702
    if model == 'sum':
        mean, var = z * skill_sd / math.sqrt(n), (2 * n - 1) * skill_sd ** 2 / n
    else:
        mean, var = z * skill_sd / n, (2 * n - 1) * skill_sd ** 2 / n ** 2
    return Phi(mean / math.sqrt(s_eff ** 2 + var))


def decile_mid_z():
    """E[Z | Z in decile k] for a standard normal (exact)."""
    from statistics import NormalDist
    nd = NormalDist()
    qs = [nd.inv_cdf(i / 10) if 0 < i < 10 else (-math.inf if i == 0 else math.inf) for i in range(11)]
    out = []
    for i in range(10):
        a, b = qs[i], qs[i + 1]
        pa = 0 if a == -math.inf else nd.pdf(a)
        pb = 0 if b == math.inf else nd.pdf(b)
        out.append((pa - pb) / 0.1)
    return out


def binomial_table():
    rows = []
    for n in (20, 50, 100, 200, 500, 1000, 2000, 5000):
        se = math.sqrt(0.25 / n)
        rows.append((n, se, 1.96 * se))
    return rows


def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def n_required(p0=0.5, p1=0.52, alpha_z=1.96, power_z=0.8416):
    return ((alpha_z * math.sqrt(p0 * (1 - p0)) + power_z * math.sqrt(p1 * (1 - p1))) / (p1 - p0)) ** 2


# ----------------------------------------------------------------------------------------------
def fmt_rows(res, ffa=False):
    out = []
    if ffa:
        out.append('| decile | mean skill | P(1st) | P(top4) | avg place | P(1st) p10-p90 | mean rating |')
        out.append('|---|---|---|---|---|---|---|')
        for r in res['rows']:
            out.append(f"| {r['dec']} | {r['skill']:.0f} | {100*r['wr']:.1f}% | {100*r['top4']:.1f}% | "
                       f"{r['place']:.2f} | {100*r['p10']:.1f}-{100*r['p90']:.1f}% | {r['rating']:.0f} |")
    else:
        out.append('| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |')
        out.append('|---|---|---|---|---|---|---|')
        for r in res['rows']:
            out.append(f"| {r['dec']} | {r['skill']:.0f} | {100*r['wr']:.1f}% | "
                       f"{100*r['p10']:.1f}-{100*r['p90']:.1f}% | {r['rating']:.0f} | {100*r['E']:.1f}% | {100*r['dRKT']:+.2f} pp |")
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quick', action='store_true')
    args = ap.parse_args()
    if args.quick:
        NP, ROUNDS, BURN = 2000, 800, 300
    else:
        NP, ROUNDS, BURN = 10000, 3000, 1000
    lines = []
    P = lambda s='': (print(s), lines.append(s))
    P(f'# winrate_sim.py results  (N={NP} players, skill ~ N(1500, 200^2), {ROUNDS} rounds, '
      f'burn-in {BURN}, window = last {ROUNDS-BURN} games per player; SBMM queue jitter sd 100 unless stated)')
    P()
    # ---------------- analytic tables
    P('## A. Analytic: random matchmaking, 1v1 vs 5v5, normal approximation of Elo logistic')
    zs = decile_mid_z()
    P('| decile | E[z] | 1v1 | 1v1 + form noise 150 | 5v5 sum-model | 5v5 mean-model |')
    P('|---|---|---|---|---|---|')
    for i, z in enumerate(zs):
        P(f'| {i+1} | {z:+.3f} | {100*analytic_random_1v1(z):.1f}% | '
          f'{100*analytic_random_1v1(z, noise_sd=150):.1f}% | '
          f'{100*analytic_random_team(z, model="sum"):.1f}% | {100*analytic_random_team(z, model="mean"):.1f}% |')
    P()
    P('## B. Analytic: binomial uncertainty of an observed win rate (p = 0.5)')
    P('| games n | SE | 95% half-width (Wald) | Wilson 95% CI if observed 52% |')
    P('|---|---|---|---|')
    for n, se, hw in binomial_table():
        lo, hi = wilson(round(0.52 * n), n)
        P(f'| {n} | {100*se:.2f} pp | +/-{100*hw:.2f} pp | {100*lo:.1f}%-{100*hi:.1f}% |')
    P(f'n to detect 52% vs 50% (two-sided a=0.05, power 0.80): {n_required():.0f}; '
      f'(one-sided a=0.05, power 0.80): {n_required(alpha_z=1.645):.0f}; '
      f'(two-sided a=0.05, power 0.90): {n_required(power_z=1.2816):.0f}')
    P()
    P('## C. Analytic: Elo stationary error and time constant (linearised, perfectly matched 1v1)')
    P('| K | Kc | tau = 1/(Kc) games | half-life games | sd(R-s) approx sqrt(200K/ln10) | '
      'sd with (2-Kc) and opp-noise correction |')
    P('|---|---|---|---|---|---|')
    for K in (10, 16, 20, 32, 40):
        kc = K * C0
        sd0 = math.sqrt(200 * K / LN10)
        sd1 = math.sqrt(K / (8 * C0 * (1 - kc)))
        P(f'| {K} | {kc:.4f} | {1/kc:.1f} | {math.log(2)/kc:.1f} | {sd0:.1f} | {sd1:.1f} |')
    P()

    P('## D. Analytic: N-player free-for-all, Plackett-Luce (Gumbel performance), focal player vs an equal field')
    P('Focal edge d (Elo points) over each of the other N-1 players; w = 10^(d/400). '
      'P(1st) = w/(w+N-1); P(top k) = 1 - prod_{j=0}^{k-1} (N-1-j)/(w+N-1-j).')
    P('| d | w | 1v1 P(win) | 8-FFA P(1st) | 8-FFA P(top4) | 100-BR P(1st) | 100-BR P(top10) | 100-BR P(top50) |')
    P('|---|---|---|---|---|---|---|---|')
    def pl_topk(w, n, k):
        m = n - 1; prod = 1.0
        for j in range(k):
            prod *= (m - j) / (w + m - j)
        return 1 - prod
    for d in (-200, 0, 100, 200, 400):
        w = 10 ** (d / 400)
        P(f'| {d:+d} | {w:.2f} | {100*w/(w+1):.1f}% | {100*w/(w+7):.1f}% | {100*pl_topk(w,8,4):.1f}% | '
          f'{100*w/(w+99):.2f}% | {100*pl_topk(w,100,10):.1f}% | {100*pl_topk(w,100,50):.1f}% |')
    P()

    # ---------------- simulations
    scen = []
    for K in (16, 32):
        scen += [
            (f'1v1 random K={K}', dict(K=K, fmt='1v1', mm='random')),
            (f'1v1 SBMM K={K}', dict(K=K, fmt='1v1', mm='sbmm')),
            (f'1v1 strict-SBMM(jitter20) K={K}', dict(K=K, fmt='1v1', mm='sbmm', queue_sd=20)),
            (f'5v5 random sum-model K={K}', dict(K=K, fmt='5v5', mm='random')),
            (f'5v5 SBMM sum-model K={K}', dict(K=K, fmt='5v5', mm='sbmm')),
            (f'FFA8 random K={K}', dict(K=K, fmt='ffa8', mm='random')),
            (f'FFA8 SBMM K={K}', dict(K=K, fmt='ffa8', mm='sbmm')),
            (f'1v1 random +form-noise150 K={K}', dict(K=K, fmt='1v1', mm='random', noise_sd=150)),
            (f'1v1 SBMM +form-noise150 K={K}', dict(K=K, fmt='1v1', mm='sbmm', noise_sd=150)),
            (f'1v1 random +AR1 form sd100 phi0.99 K={K}', dict(K=K, fmt='1v1', mm='random', drift_sd=100)),
            (f'1v1 SBMM +AR1 form sd100 phi0.99 K={K}', dict(K=K, fmt='1v1', mm='sbmm', drift_sd=100)),
        ]
    scen += [('5v5 random mean-model K=16', dict(K=16, fmt='5v5', mm='random', team_model='mean')),
             ('5v5 SBMM mean-model K=16', dict(K=16, fmt='5v5', mm='sbmm', team_model='mean'))]
    summary = []
    for i, (label, kw) in enumerate(scen):
        kw = dict(kw); kw['n_players'] = NP; kw['seed'] = 100 + i
        res, sim = run_standard(label, ROUNDS, BURN, **kw)
        summary.append(res)
        P(f'## {label}')
        P(fmt_rows(res, ffa=(kw['fmt'] == 'ffa8')))
        extra = ''
        if 'var_ratio' in res:
            extra = (f"; 100-game-window win-rate variance / binomial = {res['var_ratio']:.2f}; "
                     f"share of 100-game windows >=60%: {100*res['frac60']:.1f}%, <=40%: {100*res['frac40']:.1f}%")
        st = ', '.join(f"t={k}: {v:.2f}" for k, v in res['slope_traj'].items())
        P(f"top 1% skill win rate {100*res['top1']:.1f}%, bottom 1% {100*res['bot1']:.1f}%; "
          f"sd of individual win rates {100*res['wr_sd']:.2f} pp; stationary sd(R-s) {res['stat_err_sd']:.1f}; "
          f"residual sd around fitted line {res['resid_sd']:.1f}; "
          f"RMSE<=2x stationary after {res['conv2']} games, <=1.1x after {res['conv11']} games; "
          f"slope(R on s) {res['slope']:.3f} [{st}], corr {res['corr']:.3f}"
          + extra + f"  [{res['secs']:.0f}s]")
        P()
        sys.stdout.flush()

    P('## Summary table (rating error, convergence, decile extremes)')
    P('| scenario | sd(R - s) | resid sd (fitted line) | slope R~s | corr(R,s) | games to RMSE<=2x stat. | to <=1.1x | top-decile win | bottom-decile win | 100-game var / binomial |')
    P('|---|---|---|---|---|---|---|---|---|---|')
    for r in summary:
        vr = f"{r['var_ratio']:.2f}" if 'var_ratio' in r else '-'
        P(f"| {r['label']} | {r['stat_err_sd']:.1f} | {r['resid_sd']:.1f} | {r['slope']:.3f} | {r['corr']:.3f} | {r['conv2']} | {r['conv11']} | "
          f"{100*r['rows'][9]['wr']:.1f}% | {100*r['rows'][0]['wr']:.1f}% | {vr} |")
    P()

    P('## Scale identifiability under SBMM: slope of R on s (and residual sd) vs queue jitter, 1v1')
    P('| K | queue jitter sd | t=250 | t=500 | t=1000 | t=2000 | t=3000 |')
    P('|---|---|---|---|---|---|---|')
    for K in (16, 32):
        for q in (0, 20, 50, 100, 200):
            o = run_stretch(K, q, ROUNDS, NP)
            P(f"| {K} | {q} | " + ' | '.join(f"{a:.2f} ({r:.0f})" for t_, (a, r) in o.items()) + ' |')
    P('theory for perfectly tight SBMM (own derivation): slope(t) ~ sqrt(1 + K^2 t / (4 sd_skill^2))')
    P()

    P('## Form drift (tilt/fatigue) details under SBMM: AR(1) u, sd 100, phi 0.99 (corr. time ~100 games)')
    P('| K | outcome autocorr lag1 | lag5 | lag20 | win rate when u>+1sd | when u<-1sd | sd(rating-implied - current skill) | share of u absorbed by rating |')
    P('|---|---|---|---|---|---|---|---|')
    for K in (16, 32):
        d = run_drift_extra(K, ROUNDS, BURN, n_players=NP)
        P(f"| {K} | {d['ac'][0]:.3f} | {d['ac'][1]:.3f} | {d['ac'][2]:.3f} | {100*d['wr_hot']:.1f}% | "
          f"{100*d['wr_cold']:.1f}% | {d['err_sd_cur']:.1f} | {d['absorbed']:.2f} |")
    P()
    P('## Improvement: random 10% of players gain +300 skill linearly over 600 games (0.5 pt/game), SBMM 1v1')
    P('| K | win rate first 100 games | win rate W games 100-600 | mean expected score E games 100-600 | W - E | theory lambda*v/K | lag (skill pts) games 100-600 | theory lambda*v/(Kc) | lambda (scale) | W 200 games after stop | E after stop |')
    P('|---|---|---|---|---|---|---|---|---|---|---|')
    for K in (16, 32):
        d = run_improve(K, n_players=NP, rounds=BURN + 600 + 200, burn=BURN)
        P(f"| {K} | {100*d['wr_trans']:.1f}% | {100*d['wr_steady']:.1f}% | {100*d['E_steady']:.1f}% | "
          f"{100*(d['wr_steady']-d['E_steady']):+.2f} pp | {100*d['theory_excess']:+.2f} pp | "
          f"{d['lag']:.1f} | {d['theory_lag']:.1f} | {d['lam']:.2f} | {100*d['wr_after']:.1f}% | {100*d['E_after']:.1f}% |")
    P()
    P('## Newcomer / reset: 500 top-decile players (mean skill ~1850) reset to 1500 after equilibrium, 1v1')
    P('| matchmaking | K | initial gap (skill pts) | games to close 50% | games to close 90% | linear-theory tau=1/(Kc) | win rate first 50 | first 100 | games 300-400 |')
    P('|---|---|---|---|---|---|---|---|---|')
    for mm in ('sbmm', 'random'):
        for K in (16, 32):
            d = run_reset(K, n_players=NP, rounds_burn=BURN, mm=mm)
            P(f"| {mm} | {K} | {d['gap0']:.0f} | {d['g50']} | {d['g90']} | {d['tau']:.0f} | {100*d['wr50']:.1f}% | "
              f"{100*d['wr100']:.1f}% | {100*d['wr_last']:.1f}% |")
    P()
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'results_quick.md' if args.quick else 'results.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
