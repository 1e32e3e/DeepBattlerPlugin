# Adversarial verification of `winrate_math.md` / `winrate_sim_results.md`

Verifier: independent re-derivation + independent Monte-Carlo code (`verify_winrate.py` in this folder, written from scratch; `winrate_sim.py` was **not** read until all verdicts below were fixed — the diagnosis in section D was written afterwards).
Setup of my simulations (unless stated): N = 4000 players (2000 for 10k-game runs), skill s ~ N(1500, 200²), all ratings start at 1500, every player plays one game per round, 3000 rounds, statistics over games 1001–3000; SBMM = sort by R + N(0, jitter²) with random tie-break, adjacent players paired; own seeds. One process at a time, < 1 GB RAM, each experiment 1–60 s.
Reproduce: `python3 verify_winrate.py analytic random sbmm stretch ode trueskill tau team ffa form j0 reset_frozen reset_seeds misc` (raw logs of my runs: scratchpad `verify_winrate/out_*.txt`).

## Summary table

| # | Claim (as stated in the notes) | Verdict | My numbers (parameters) | Sensitive to modelling? |
|---|---|---|---|---|
| 1 | F(100..800)=64.0/76.0/84.9/90.9/99.0%; c=ln10/1600; σ_d≈295.7; Φ(200/283)=76.0%, Φ(400/283)=92.1% | CONFIRMED | 64.01/75.97/84.90/90.91/99.01%; LS-best probit scale 294.9; max abs error of Φ(d/295.7) vs F = 0.95 pp | no |
| 2a | Random matching W(s)=Φ((s−μ)/√(σ_d²+τ²)), ρ=0.560 at τ=200 | CONFIRMED (approximation, <1 pp) | decile-avg exact logistic vs formula differ ≤0.6 pp | needs normal skills, logistic≈probit |
| 2b | Top 10% ≈83% (83.7% formula), top 1% ≈93% (93.2%), bottom 10% ≈17% (16.3%) | CONFIRMED for the rounded values; formula values slightly CORRECTED | exact decile averages 83.1 / 92.5 / 16.9%; my sim K16: 82.7 / 92.4 / 17.1%, K32: 83.0 / 93.3 / 16.9% | depends on τ/σ_d (table) |
| 2c | τ-table "前10%平均/前1%平均" columns (Φ(ρ·E[z])) | CORRECTED (minor) | Φ evaluated at the decile-mean z overstates the decile average (Jensen): τ=200 83.7→83.1, τ=300 89.4→88.2, τ=400 92.1→90.8 (top 1%: 97.1→96.4, 98.4→97.9) | – |
| 3 | Exact identity W_T = Ē_T + (R_T−R_0)/(K·T) for fixed K | CONFIRMED | holds to ≤3e-15 in every 1v1 and 5v5 run (each member updated K(S−E)) | only fixed-K Elo; Glicko/TrueSkill → weighted version |
| 4a | Stationary sd(R−s) ≈ 9.3√K; 37.7 (K16) / 54.0 (K32) with correction | CONFIRMED | random matching: 38.0 / 54.0 (resid sd), 38.1 / 54.8 raw | roughly matching-independent, as claimed |
| 4b | Time constant τ_R ≈ 695/K games (43 / 22), "SBMM 43 games" | CORRECTED | measured e-folding time of rating error: K16 66 (random), 57 (SBMM jitter 100 and 200); K32 33–34 (random and SBMM). ≈1.3–1.5× 695/K | yes: 695/K needs λ=1 *and* P(1−P)=¼ simultaneously, which never happens (tight SBMM ⇒ λ>1 weakens restoring force; loose matching ⇒ P(1−P)<¼) |
| 4c | Random matching τ_R: 55 games (average player), 94 (+350) at K16 | CONFIRMED | analytic 55.0 / 93.7; population-average measured 66 | – |
| 5 | Honest SBMM 1v1 deciles 42–58% (jitter 100), 49–51% (jitter 20); K32 43.5–56.4 / 48.9–51.1 | CONFIRMED | K16: 42.2–58.0%, 48.8–51.2%; K32: 43.6–56.4%, 48.9–51.1%; top1% 61.7% / 51.8% | strongly depends on jitter (window) width; strict-SBMM residual deviation is a transient dR/(KT) term that decays ∝1/λ²∝1/t |
| 6a | Reset of top-10% player: closes half the gap in 52 (K16) / 33 (K32) games | CORRECTED (mildly) | 45–47 / 30 games (3 seeds; also with 3000 warm-up rounds) | gap definition |
| 6b | … closes 90% in 282 / 195 games | CORRECTED (measurement artifact, see D1) | 138–153 / 89–100 games when the gap is measured against the *current* line of the other players (≈ exponential with the half-life). The note's numbers come from a target frozen at the reset moment, which ignores the ~20–26 rating-point deflation of the whole pool caused by the reset itself; with that definition my code gives 274 / 216 (random 285 / 142), close to the note | gap definition |
| 6c | Reset player wins 77.5% / 73.8% of first 50 games (72.8/68.1% first 100; 59.2/57.3% games 300–400) | CONFIRMED | 77.5–78.0% / 73.7–74.0%; 73.0 / 67.8–68.1%; 59.1 / 57.0% | jitter width |
| 7a | Strict SBMM: rating scale not pinned down, stretches (slope 2.1 at K16, 4.2 at K32 after 3000 games, jitter 20) | CONFIRMED — real model property, not an artifact | 2.11 / 4.16; with exactly-equal-rated pairs Var(R) grows by exactly K²/4 per game (191 823 vs 192 000 predicted at t=3000, K16); also with init at true skill, uniform "block window" pairing, deterministic vs random tie-break, zero-sum or not, and in a TrueSkill-type filter | yes – see 7c |
| 7b | λ(t) ≈ √(1+K²t/(4τ²)) | CONFIRMED as tight-matching limit / upper envelope, with λ0 made explicit; note's comparison column CORRECTED | general form λ² ≈ λ0² + K²t/(4τ²) (follows from the exact variance identity, ignores σ_e² and jitter restoring). Sims start at λ0≈0, so the right comparison is 1.26/2.19 (K16) and 2.53/4.38 (K32) at t=1000/3000, not the note's 1.61/2.41, 2.72/4.49. From λ0=1 (init = true skill, jitter 20): sim 1.56/2.27, my ODE 1.57/2.28, formula 1.61/2.41; t=10 000: sim 3.74, ODE 3.77, formula 4.12 | – |
| 7c | "Wider windows stop it" | CORRECTED (needs a threshold) | Equilibrium exists only if jitter sd σ_q > √(K/(8c(1−Kc))) ≈ stationary rating-error sd (37.7 at K16, 54.0 at K32; i.e. matched-pair rating-difference sd > ≈53 / ≈76). Then λ* ≈ 1/(1−(37.7/σ_q)²) at K16: σ_q=50 → λ*≈2.3 (sim 2.17 at t=10 000, still rising); σ_q=100 → 1.17 (sim 1.19, flat to t=10 000); σ_q=200 → 1.04 (sim 1.06). K32 σ_q=50 is *below* threshold → unbounded (sim 3.24 at t=3000). | yes |
| 7d | σ_q=0 rows of the stretching table (resid sd 42→200) | CORRECTED (artifact) | with deterministic adjacent pairing the residual is 176; adding 1 rating-point jitter gives 57 (slope unchanged). The large residual is a pairing artifact, not "strict SBMM destroys ranking" | implementation |
| 7e | Real-world plausibility | PLAUSIBLE ONLY IN BOUNDED FORM | TrueSkill-type filter (σ0=2β, τ_dyn=σ0/100): strict SBMM stretches early and keeps growing (2.06→2.61 over 10k games); correct prior σ0=200: 1.19→2.16; τ_dyn=0: frozen at whatever it reached (1.99 / 1.63–1.75); wide window (jitter 100) → stable ≈1.11. Player churn 0.1%/game caps λ≈1.25. | unbounded √t growth needs windows tighter than rating noise for thousands of games without resets/decay/churn — unlikely in deployed systems; bounded inflation (λ*≈1.05–1.5) is plausible |
| 8a | 5v5 random teams: top 10% 65% (sum) / 59% (mean); deciles 34.8–65.0 / 41.1–59.0 | CONFIRMED | sim 34.6–65.1% / 40.8–59.0%; analytic MC decile averages 65.3 / 59.0% | team-performance model choice |
| 8b | SBMM 5v5 deciles 46.6–53.4% (sum, K16), 47.6–52.4 (K32), 48.0–52.0 (mean) | CONFIRMED but FRAGILE | 46.5–53.5 / 47.7–52.4 / 48.0–52.0; but jitter 200 gives 41.7–58.4%, and at jitter 100 the scale is still stretching (λ 1.15→1.46 K16, 1.82→2.55 K32) | very sensitive to window width and t |
| 8c | Dilution: slope 40% (sum) / 22% (mean) of 1v1 at n=5; "~1/√n vs ~1/n" | CONFIRMED (heuristic) | 0.400 / 0.224 (1/√5=0.447, 1/5=0.200); per-100-pt slopes 11.2/4.5/2.5/6.0 pp reproduced; team resid sd 57.3 (sum K16, note 58.4), 85.5 (mean, note 85.0) | yes, where randomness lives |
| 9 | Plackett–Luce P(1st)=w/(w+N−1), table; 8-FFA top 10%: random 40%/93% top-4, SBMM 16.9%/61% | CONFIRMED | Gumbel MC d=+200: 31.3% (formula 31.1%), top-4 84.6%; FFA sim random 40.0–40.6% / 93.3–93.4%, SBMM 16.5–16.9% / 60.3–61.2% | SBMM figures depend on window |
| 10 | Per-game noise sd150: top decile 82.9→79.5%, rating slope 0.81 | CONFIRMED | exact analytic 79.5%, sim 79.5%, slope 0.810 | – |
| 11 | AR(1) form sd100, φ=.99: SBMM hot 58.8% / cold 41.0%; 100-game var ratio 1.64 (SBMM) / 3.70 (random); lag-1 autocorr ≈0.01; absorbed share 0.64 (theory 0.70) | CONFIRMED | 58.9 / 41.2%; 1.62 / 3.70 (K32: 1.06 / 3.65); acf 0.0155 / 0.0131 / 0.0077 (lags 1/5/20); absorbed 0.643 (K32 0.740) | definition of the variance ratio (within-player, 20 windows) |
| 12a | Improving player: W−E = (rating rise rate)/K exactly | CONFIRMED | equality to rounding in every run | – |
| 12b | W−E ≈ λv/K (≈v/K), lag ≈ λv/(Kc), "与理论吻合" | CORRECTED (approximate only, ±15%) | SBMM K16: W−E 3.05 pp vs λv/K 3.59, v/K 3.12; K32: 1.94 vs 2.26 / 1.56. Random K16: 2.67 vs 3.12. Lag: SBMM 28.5/18.2 vs theory 25.0/15.7; random 35/19 vs v/(Kc) 22/11. Rating rises slower than λv (zero-sum deflation of the other 90%, lag still growing) | yes |
| 13 | SBMM without drift: 100-game var ratio 0.56 (K16) / 0.42 (K32); sd(W_n)≈√2·sd(e)/(Kn) | CONFIRMED (formula is the n≫τ limit) | 0.56 / 0.43 | – |
| 14a | Binomial SE 11.18/5.00/2.24 pp at n=20/100/500; Wald half-widths; tail probs 2.84%, 5.77%, 2.07%, 1.42% | CONFIRMED | identical | – |
| 14b | n=4903 (52 vs 50, two-sided .05, 80%), 3862 one-sided, 6563 at 90% | CONFIRMED | 4903.2 / 3862.0 / 6563.0 (exact-binomial power at 4903 ≈ 0.797) | normal approximation |
| 14c | Observed 52% needs ≥2401 games for 95% CI to exclude 50% | CONFIRMED (for Wilson/score) | score/Wilson: n>2400.9; Wald with p̂: n≥2398 | interval type |
| 14d | Wilson 95% CI for observed 52% at n=20: 29.9–70.1% | CORRECTED | 31.6–71.7% (29.9–70.1% is the Wilson interval for 10/20 = 50%); other rows correct | – |
| 15 | Cold-start convergence, random 1v1: RMSE ≤2× stationary after 90 (K16)/25 (K32) games, ≤1.1× after 236/82 | CONFIRMED | 93 / 26 and 228 / 84 | – |

Overall: no headline claim is refuted. The numerical simulation results reproduce closely with independent code (deviations ≤0.5 pp on win rates). Corrections concern (i) the reset-experiment 90%-closure numbers, (ii) the "time constant 695/K" being an idealisation (~1.3–1.5× too short), (iii) the scale-stretching section, where the effect is real but the "wider windows stop it" statement needs the threshold criterion, the theory comparison column uses the wrong λ0, and the σ_q=0 residuals are an artifact, (iv) the improvement-approximation (±15%, not "吻合"), (v) small formula-vs-average and one Wilson-row slips.

## Caveats the final report should carry
1. All win-rate numbers are *model* outputs: normal skill distribution with τ/σ_d = 200/296, a correctly specified Elo model, fixed K, closed population, no parties/churn/resets. Real games will differ quantitatively; no real data validates them.
2. "Honest SBMM ⇒ ≈50%" depends on how tight matching is relative to population density; the decile spread (42–58% vs 49–51%) is set by an arbitrary jitter parameter, and the 5v5 version is even more sensitive (46.5–53.5% at jitter 100 vs 41.7–58.4% at jitter 200). Present ranges, not point values.
3. Scale stretching: present as "a property of the idealised model, derived and simulated by the authors, not observed in real data". The precise mechanism is simple: two players with equal ratings always split by ±K/2, so exact-equal pairing adds K²/4 of rating variance per game with nothing pulling it back; only games between *different* ratings anchor the scale. Unbounded growth needs matched-rating-difference sd below ≈13·√K Elo points; above that the scale settles at λ* > 1 (ratings exaggerate skill gaps by λ*, i.e. rating-based win predictions become over-confident). Bayesian filters (TrueSkill/Glicko) do not remove it if they keep a dynamics term; they freeze it if they do not.
4. Time constants ("43 games at K16") should be quoted as ≈55–65 games (K16) / ≈33 games (K32) for realistic matching; 695/K is a lower bound.
5. The identity W = Ē + ΔR/(KT) is exact only for fixed-K Elo with K(S−E) updates; team games where members get different K, Glicko RD, TrueSkill σ, rating floors or bonus systems (win-streak bonus, placement) break it.
6. The Q2 takeaway "前 10% 玩家约 84%" should read "约 83%".

---

## A. Analytic checks (`verify_winrate.py analytic`)
- Constants: c = 0.0014391; 1.702·400/ln10 = 295.67; least-squares best probit scale for F over |d|≤800 = 294.9; max |F(d) − Φ(d/295.7)| = 0.0095.
- Random matching via Gauss–Hermite (exact logistic, normal skills), decile averages 16.9, 27.8, 35.1, 41.3, 47.1, 52.9, 58.7, 64.9, 72.2, 83.1%; top/bottom 1% 92.5/7.5%. The note's formula column (Φ(ρ·E[z|decile])) is 16.3 … 83.7%; difference only at the extreme deciles.
- Linearised Elo: e_{t+1} = (1−Kc)e_t + Kc·e_opp + Kη; Var(e) = K/(8c(1−Kc)) — re-derived; values 29.7/37.7/42.3/54.0/60.7 for K = 10/16/20/32/40. √(200K/ln10) = 9.32√K.
- Time constants under random matching: E[P(1−P)] = 0.1972 (d=0) → 55.0 games, 0.1159 (d=+350) → 93.7 games.
- Teams (MC, 400k draws, logistic): top-decile sum model n = 1,2,3,5,6,8: 83.0, 73.8, 69.6, 65.3, 64.0, 62.1%; mean model 83.0, 69.7, 64.1, 59.0, 57.7, 55.9%. Slope ratios n=5: 0.400 (sum), 0.224 (mean).
- Plackett–Luce table reproduced exactly; random 8-FFA top decile P(1st) 40.0%, P(top4) 93.3%, avg place 2.18; bottom decile P(1st) 1.4%.
- Per-game noise 150: effective σ_d 363.9 (ratio 0.813; exact local slope ratio at d=0 is 0.772); exact top-decile 79.5%.
- AR(1) absorbed share α/(1−(1−α)φ): 0.702 (K16), 0.828 (K32). With λ>1 under SBMM the effective α is Kc/λ, giving 0.675 at λ=1.13, closer to the simulated 0.64.
- Binomial: all SE / Wald / Wilson rows reproduced except n=20 (Wilson for 52%: 31.6–71.7%). Sample sizes 4903.19 / 3862.01 / 6562.98. Tail probabilities P(X≥60|100)=0.0284, P(X≥14|20)=0.0577, P(X≥15|20)=0.0207, P(X≥275|500)=0.0142.

## B. Simulation details

### B1. Random 1v1 (N=4000, K16/K32; also N=2000 with init at true skill)
| decile | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| K16 W | 17.1 | 28.0 | 35.3 | 41.5 | 47.1 | 52.8 | 58.7 | 64.6 | 72.1 | 82.7 |
| K32 W | 16.9 | 27.9 | 34.8 | 41.5 | 47.1 | 52.9 | 58.7 | 65.1 | 72.1 | 83.0 |
sd of individual win rates 19.5 / 19.7 pp; slope R~s 1.012 / 1.045; corr 0.982 / 0.968; 100-game var/binomial 1.00 / 0.99; share of 100-game windows ≥60%: 33.9 / 34.1%. Init at true skill (N=2000): 16.8–82.5%.

### B2. SBMM 1v1
| case | decile 1 … 10 W | top1% | E col. vs dR col. | slope t=3000 | resid sd |
|---|---|---|---|---|---|
| jitter100 K16 | 42.2 45.3 47.0 48.3 49.4 50.5 51.6 53.0 54.7 58.0 | 61.7 | deviation all in E, dR ≈ ±0.05 pp | 1.20 | 41 |
| jitter20 K16 | 48.8 49.3 49.6 49.7 49.9 50.1 50.3 50.5 50.7 51.2 | 51.8 | E 49.7–50.3, dR −0.90…+0.90 pp | 2.11 | 54 |
| jitter100 K32 | 43.6 … 56.4 | 59.3 | E | 1.49 | 66 |
| jitter20 K32 | 48.9 … 51.1 | 51.7 | dR ±0.95 pp | 4.16 | 114 |
100-game var/binomial: 0.56 (j100 K16), 0.59 (j20 K16), 0.43 (j100 K32), 0.58 (j20 K32).

### B3. Scale stretching — robustness battery (slope λ with resid sd in brackets)
| K | jitter | t=250 | 500 | 1000 | 2000 | 3000 | Var(R) at 3000 vs K²t/4 |
|---|---|---|---|---|---|---|---|
| 16 | 0 | 0.58 (47) | 0.81 (73) | 1.13 (110) | 1.60 (154) | 1.99 (178) | 191 823 vs 192 000 |
| 16 | 20 | 0.69 (31) | 0.94 (37) | 1.28 (43) | 1.75 (49) | 2.11 (54) | 178 683 |
| 16 | 50 | 0.79 | 1.00 | 1.25 | 1.52 | 1.68 (49) | 118 487 |
| 16 | 100 | 0.87 | 1.03 | 1.14 | 1.19 | 1.19 (41) | 59 819 |
| 16 | 200 | 0.91 | 1.02 | 1.05 | 1.06 | 1.06 (40) | 47 500 |
| 32 | 0 | 1.16 (99) | 1.62 | 2.27 | 3.26 | 4.07 (325) | 766 435 vs 768 000 |
| 32 | 20 | 1.24 (61) | 1.74 | 2.44 | 3.42 | 4.17 (109) | 703 149 |
| 32 | 50 | 1.24 | 1.63 | 2.13 | 2.78 | 3.24 (98) | 419 763 |
| 32 | 100 | 1.17 | 1.34 | 1.45 | 1.50 | 1.51 (66) | 93 051 |
| 32 | 200 | 1.07 | 1.12 | 1.13 | 1.13 | 1.12 (56) | 53 783 |
Other variants (K16): deterministic index tie-break, jitter 0 → 2.04 (174) at t=3000 (same as random tie-break); jitter 1 → slope 2.16, resid 57; jitter 5 → 2.16 (56). Init at true skill, jitter 20: 1.16, 1.31, 1.56, 1.95, 2.27 (Var growth 169 043 vs K²t/4 = 191 936). Init 1500 + N(0,200²) noise: 2.26 at 3000. "Block window" pairing (sort, shuffle within moving blocks of 2/4/16/64 players): 2.10/2.14/2.21/2.15 at t=3000. Long runs (N=2000, init = skill): jitter 20 → 1.55, 2.26, 3.00, 3.74 at t=1k/3k/6k/10k; jitter 50 → 1.42, 1.76, 2.00, 2.17; jitter 100 → 1.17, 1.20, 1.20, 1.19. Churn 0.1% of players replaced per round by new players at 1500 (jitter 20): λ (players aged >300) 1.06, 1.26, 1.24 at 1k/3k/6k.

Derivation (mine). Write R−μ = λ(s−μ)+e. With jitter σ_q, the partner's rating regresses: E[R'|R] = μ+g(R−μ), g = σ_R²/(σ_R²+σ_q²); E[s'|R'] = μ+b(R'−μ), b = λτ²/σ_R². Expected drift of a player of skill s ≈ Kc[(s−μ) − (bg+1−g)(R−μ)], hence
 dλ/dt = Kc·[σ_e² + σ_q²(1−λ)] / (λ²τ² + σ_e² + σ_q²), σ_e² ≈ Kλ/(8c(1−Kc/λ)).
For σ_q→0 this reduces to the note's dλ/dt = K²/(8λτ²). Fixed point λ* = 1 + σ_e²(λ*)/σ_q², which exists only for σ_q² > K/(8c(1−Kc)). Independently of linearisation: if the two players of a pair have exactly equal ratings, E = ½ and their ratings move to R ± K/2 whoever wins, so the population rating variance rises by exactly K²/4 per game; for any pairing in which the partner's skill is exchangeable with one's own given the rating, Cov(R, S−E) = 0 exactly, so nothing removes that variance. This is why the effect is not an artifact of zero-sum updating, of the 1500 initialisation or of the burn-in. Zero-sum is not needed (each player's own ±K_i/2 suffices).

### B4. Time constants and reset experiment
Rating-error autocorrelation (e = R − fitted line), K16: random k20 0.738, k50 0.470, k100 0.228 → τ≈66–68; SBMM jitter100 → 56–57; jitter200 → 57–58. K32: random and SBMM jitter100 both 33–34. Mean-field restoring coefficient Kc·(λτ²+σ_q²)/(σ_R²+σ_q²)·4E[P(1−P)] gives ≈58 (K16, j100) and ≈32 (K32, j100), matching.
Reset (200 of the 400 top-decile players reset to 1500 after 1000 rounds; gap in skill points = s − (R−a)/λ with (a,λ) fitted on the other players):
| matching | K | gap0 | 50% closed | 90% closed | W first 50 | first 100 | games 300–400 |
|---|---|---|---|---|---|---|---|
| SBMM j100 | 16 | 350 | 45 (46, 46, 47 other seeds / 3000 warm-up) | 147 (150, 138, 153) | 78.0% | 73.0% | 59.1% |
| SBMM j100 | 32 | 347 | 30 (30, 30) | 92 (100, 89) | 73.7% | 67.8% | 57.0% |
| random | 16 | 357 | 52 (52) | 211 (186) | 83.6% | 83.8% | 83.2% |
| random | 32 | 345 | 26 (26) | 84 (103) | 82.9% | 83.2% | 83.0% |
| SBMM j50 | 16 | – | 51 | 158 | 76.8% | – | – |

### B5. Teams 5v5 (snake draft inside groups of 10 for SBMM; member update K(S−E_team), E_team from the same functional form as the outcome model)
random sum K16 34.6–65.1% (top1% 72.1), K32 34.7–65.4%; random mean K16 40.8–59.0%; SBMM j100 sum K16 46.5–53.5% (λ 1.15/1.36/1.46 at 1k/2k/3k), K32 47.7–52.4% (λ 1.82/2.27/2.55); SBMM mean K16 48.0–52.0%; SBMM sum K16 jitter 200: 41.7–58.4% (λ 1.14, stable). Var ratios 0.79/0.74/0.90 (note 0.79/0.74/0.91).

### B6. 8-player FFA (Gumbel performances = Plackett–Luce; pairwise Elo K/7)
random K16: top10% P1st 40.0%, top4 93.3%, avg place 2.18; bottom10% 1.5% / 11.2% / 6.77; top1% 62.2%; resid sd 23.0. random K32: 40.6 / 93.4 / 2.17. SBMM j100 K16: 16.9 / 61.2 / 3.91, bottom 8.9 / 39.2 / 5.10; resid 24.8. K32: 16.5 / 60.3.

### B7. Skill fluctuation and improvement
Per-game noise 150 (K16): random 20.9–79.5%, slope 0.810, resid 37.5; SBMM 40.9–59.0%, slope 0.930.
AR(1) σ_u=100, φ=0.99: random K16 18.4–81.5%, var ratio 3.70, share ≥60% 34.3%; K32 3.65. SBMM K16 42.8–57.3%, var ratio 1.62, share ≥60% 10.3%, hot 58.9%, cold 41.2%, absorbed 0.643, outcome acf 0.0155/0.0131/0.0077; SBMM K32 44.3–55.7%, 1.06, hot 57.0%, cold 43.1%, absorbed 0.740, acf 0.0045/0.0031/0.0014.
Improvement (10% of players +0.5/game for 600 games; window = games 101–600 of the ramp):
| matching | K | W | E | W−E | drift/K | λv/K | v/K | lag (skill pts) | λv/(Kc) | after stop W/E |
|---|---|---|---|---|---|---|---|---|---|---|
| SBMM j100 | 16 | 55.8 | 52.8 | +3.05 | +3.05 | +3.59 | 3.12 | 28.5 | 25.0 | 55.9 / 55.0 |
| SBMM j100 | 32 | 54.4 | 52.5 | +1.94 | +1.94 | +2.26 | 1.56 | 18.2 | 15.7 | 54.6 / 54.1 |
| random | 16 | 65.8 | 63.1 | +2.67 | +2.67 | +3.17 | 3.12 | 35.2 | 22.0 | 74.7 / 73.8 |
| random | 32 | 64.3 | 62.9 | +1.40 | +1.40 | +1.62 | 1.56 | 19.0 | 11.2 | 73.5 / 73.2 |

### B8. TrueSkill-type Gaussian filter (1v1, Thurstone truth P = Φ(Δs/(√2β)), β = 209 so slope equals Elo's; slope λ (resid) [mean posterior sd, sd(μ)])
| matching | prior / dynamics | t=1000 | 3000 | 10 000 |
|---|---|---|---|---|
| SBMM j20 | σ0=2β=418, τ_dyn=4.18 | 2.06 (43) [40, 431] | 2.20 | 2.61 (47) [40, 545] |
| SBMM j20 | σ0=418, τ_dyn=0 | 1.99 [12] | 1.99 | 1.99 (18) [4] |
| SBMM j20 | σ0=200, τ_dyn=4.18 | 1.19 | 1.49 | 2.16 |
| SBMM j100 | σ0=418, τ_dyn=4.18 | 1.50 | 1.15 | 1.11 |
| SBMM j100 | σ0=200, τ_dyn=4.18 | 1.09 | 1.12 | 1.11 |
| SBMM j100 | σ0=418, τ_dyn=0 | 1.75 | 1.69 | 1.63 |
| random | either | 1.02 | 1.03 | 1.00–1.03 |
Interpretation: under strict SBMM the likelihood barely constrains the scale, so a Bayesian filter's scale is set by its prior width plus accumulated dynamics noise; it keeps drifting if τ_dyn>0 and freezes (possibly far from 1) if τ_dyn=0. Wide windows let it self-correct.

## C. Real-system plausibility of the stretching effect (judgement)
- Deployed systems have several anchors the model lacks: player churn (new accounts at the default rating; 0.1%/game already caps λ≈1.25 here), seasonal soft resets (compress the spread periodically: with compression factor f every P games the stationary variance is f²K²P/(4(1−f²))), inactivity decay, rating floors, party/role/ping constraints and queue-time widening, all of which raise the effective σ_q.
- What remains plausible: a moderate, persistent scale inflation (λ*≈1.05–1.5) whenever matched rating differences are only somewhat larger than the rating noise; the practical symptom would be that rating-gap-based win predictions are too extreme. This is a model prediction; no empirical confirmation was found or attempted.
- The note's own wording ("作者推导，需谨慎表述") is appropriate; it should add the threshold condition and drop the implication that windows "stop" it in general.

## D. Diagnosis after reading `winrate_sim.py` (read only after sections A–C were written)
The original code turns out to be a clean implementation of the same model: jitter-sorted adjacent pairing, snake draft for 5v5, model-consistent team updates, Gumbel FFA with pairwise K/7 updates, and the same within-player variance-ratio definition (20 windows, ddof 1, divided by p̂(1−p̂)/100). That explains why nearly all numbers reproduce. No coding bug changes a headline win-rate number. Discrepancies:

D1. Reset experiment, 90% closure (`run_reset`). `target = a*s + b` is fitted once, just before the reset, and kept fixed. Setting 500 ratings from ≈1920 to 1500 removes ≈210 000 rating points that zero-sum Elo never gives back, so the whole pool, and with it the equilibrium target, shifts down ≈20 points; the scale λ also keeps drifting. Against the frozen target the reset cohort keeps a residual gap of ≈25–30 skill points (my replication at t=400: 30.0 for SBMM K16, 25.8 for K32). That residual sits close to the 10% threshold (35 points), so "90% closed" arrives late. My replication with the frozen definition gives 51/274 (SBMM K16), 34/216 (K32), 59/285 and 30/142 (random), essentially the note's 52/282, 33/195, 57/269, 29/143. With a moving target (the current line of the non-reset players) the numbers are 45/146, 30/96, 52/186, 26/103. The half-closure numbers change only slightly (by about 10%). Recommendation: quote "≈45 games to halve the gap, ≈150 to close 90% (K16); ≈30 / ≈95 (K32)" and note the pool deflation as a side effect of resets in a closed zero-sum pool.

D2. Stretching table, σ_q=0 rows (`run_stretch` with `queue_sd=0`). `np.argsort(R + 0·noise)` gives fully deterministic adjacent pairing. The slope is right (the variance identity forces it), but the residual (→200) is inflated by that deterministic pairing pattern: 1 point of jitter brings it down to 57. Don't use those residuals.

D3. "Perfect-SBMM theory" column. It prints √(1+K²t/(4τ²)), i.e. λ0=1, while every simulation starts at λ0≈0 (all ratings 1500). The notes mention this ("理论值从 λ0≈0 起步，所以偏高"), but the column should show the λ0=0 values (1.26/2.19, 2.53/4.38), or the sims should start at λ0=1 (sim 1.56/2.27 vs formula 1.61/2.41, K16 jitter 20).

D4. Improvement (`run_improve`). The comparison is computed correctly. The text says the 15% gap between 3.06 and 3.60 pp "吻合" (agrees), which overstates it. Two effects explain the gap: the zero-sum deflation of the non-improvers, and a lag that keeps growing over the 500-game window.

D5. Time constant. The code never measures it under SBMM. The "43 games" figure is only the linear-theory column (`tau = 1/(K*C0)`). The measured value is ≈57 games (section B4).

D6. Strict SBMM, 5v5 SBMM and the AR(1)+SBMM K32 runs are all still stretching inside the 2000-game statistics window. Their rows in the summary table therefore describe a transient (the dR/(KT) column). The notes already mark these rows with "*" for convergence, but the win-rate ranges should get the same caveat.
