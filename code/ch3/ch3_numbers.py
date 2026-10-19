"""打印第三章正文和表格引用的全部数字（精确计算 + 读取缓存的模拟结果）。

用法：python code/ch3/ch3_numbers.py > /tmp/ch3_numbers.txt
需要先运行 population.py 与 experiments.py 生成缓存（否则会现跑）。
"""
import numpy as np

import _common  # noqa: F401  （设置 sys.path）
from experiments import END_PROB, K_ELO, SIGMA_Q, STANDARD, exact_chain, run_standard
from model import (C_ELO, chain_iid, chain_tilt, elo_error_sd, elo_gain, elo_F, elo_lag1,
                   elo_streak_excess, expected_runs_ge, expected_wklk, first_win_recursion,
                   longest_run_distribution, miller_sanjurjo, miller_sanjurjo_k1,
                   pooled_streak_winrate, prob_longest_ge, prob_pattern_once, prob_window_slump,
                   schilling_mean, schilling_sd, win_prob_noisy, ar1_retained, detect_games)
from population import load


def sec(t):
    print("\n## " + t)


sec("A1 最长连败（精确）")
for pw in (0.45, 0.5, 0.55):
    for n in (50, 100, 500, 1000):
        q = 1 - pw
        E, sd, med, p95, ge = longest_run_distribution(n, q)
        print(f"p={pw} n={n}: E={E:.2f} GSW={schilling_mean(n, q):.2f} SD={sd:.2f} (GSW {schilling_sd(q):.2f}) "
              f"med={med} p95={p95} P>=5 {ge[5]:.3f} P>=7 {ge[7]:.3f} P>=10 {ge[10]:.4f} "
              f"E#runs>=5 {expected_runs_ge(n, q, 5):.2f} >=10 {expected_runs_ge(n, q, 10):.3f}")
mx = max(abs(longest_run_distribution(n, 1 - pw)[0] - schilling_mean(n, 1 - pw))
         for pw in (0.45, 0.5, 0.55) for n in (50, 100, 500, 1000))
print("max |exact-GSW| =", round(mx, 3), "| recursion check", 1 - first_win_recursion(1000, 0.5, 10))
print("rule log2(n/2): n=100", np.log2(50), "n=1000", np.log2(500))
print("session p=.5: 10 games P>=3/4/5", [round(prob_longest_ge(10, .5, r), 3) for r in (3, 4, 5)],
      "20 games P>=4/5", [round(prob_longest_ge(20, .5, r), 3) for r in (4, 5)])
print("10M players x 500 games: P>=10", prob_longest_ge(500, .5, 10), "P>=7", prob_longest_ge(500, .5, 7))

sec("A3 W^kL^k")
for pw in (0.5, 0.45):
    for k in (3, 4, 5, 6):
        print(f"p={pw} k={k}: E/100={expected_wklk(100, pw, k):.3f} E/1000={expected_wklk(1000, pw, k):.3f} "
              + " ".join(f"P(n={n})={prob_pattern_once(n, pw, k):.3f}" for n in (50, 100, 500, 1000)))
print("exactly-k (k=4, n=1000, p=.5) analytic:", (1000 - 2 * 4 - 1) * 0.5 ** 10 + 2 * 0.5 ** 9 * 0.5)
rng = np.random.default_rng(7)
X = rng.random((100000, 100)) < 0.5


def has_wl(X, k, first_win=True):
    A = X if first_win else ~X
    m = X.shape[1] - 2 * k + 1
    ok = np.ones((X.shape[0], m), bool)
    for j in range(k):
        ok &= A[:, j:m + j]
        ok &= ~A[:, k + j:m + k + j]
    return ok.any(1)


print("either order k=4 in 100 (MC 1e5):", (has_wl(X, 4) | has_wl(X, 4, False)).mean())

sec("A4 滑动窗口")
print("n=100 w=10 <=2:", prob_window_slump(100, 10, 2), " n=100 w=20 <=6:", prob_window_slump(100, 20, 6))
print("n=500 w=20 <=6:", prob_window_slump(500, 20, 6))
X5 = (rng.random((50000, 500)) < 0.5).astype(np.int16)
cs = np.concatenate([np.zeros((X5.shape[0], 1), np.int16), X5.cumsum(1, dtype=np.int16)], 1)
print("n=500 w=50 <=20 (MC 5e4):", ((cs[:, 50:] - cs[:, :-50]).min(1) <= 20).mean())

sec("A5 Miller-Sanjurjo")
for n in (20, 50, 100, 200, 1000):
    print(n, [round(miller_sanjurjo(n, k)[0], 4) for k in (1, 2, 3, 4, 5)] if n <= 200 else
          [round(miller_sanjurjo(n, k)[0], 4) for k in (3, 5)])
print("k=1 closed form n=100:", miller_sanjurjo_k1(100), " DP:", miller_sanjurjo(100, 1)[0])
print("p=.45 n=100 k=3:", miller_sanjurjo(100, 3, 0.45)[0])
# 每段连胜只取一次（第 3 胜后那一局）
Y = rng.random((200000, 100)) < 0.5
vals = []
cnt = np.zeros(Y.shape[0])
win = np.zeros(Y.shape[0])
ws = np.zeros(Y.shape[0], int)
for t in range(100):
    take = ws == 3
    cnt += take
    win += take & Y[:, t]
    ws = np.where(Y[:, t], ws + 1, 0)
d = cnt > 0
print("one obs per streak (after exactly 3rd win): per-history mean", (win[d] / cnt[d]).mean())

sec("A6 构成效应")
print("random matching pooled after k wins:", [round(pooled_streak_winrate(k), 4) for k in range(1, 7)])
print("after k losses:", [round(pooled_streak_winrate(-k), 4) for k in range(1, 7)])
for nm in ("elo10", "elo32"):
    d = load(nm)
    print(nm, "pooled W", np.round(d["pooledW"][:6], 3), "L", np.round(d["pooledL"][:6], 3))

sec("B 诚实 Elo 人群")
for nm in ("elo10", "elo32", "elo32_s25", "elo32_s50", "elo32_s200", "elo32_s400", "t5_elo32", "t5_random",
           "tilt30_elo32", "manip_sym", "manip_asym", "t5_loserq"):
    d = load(nm)
    print(f"{nm}: W1..6 {np.round(100 * d['W'][:6], 2)} L1..6 {np.round(100 * d['L'][:6], 2)}")
    print(f"   oppR W3/W5 {d['oppR_W'][2]:+.1f}/{d['oppR_W'][4]:+.1f} L3/L5 {d['oppR_L'][2]:+.1f}/{d['oppR_L'][4]:+.1f}"
          f" oppS W5 {d['oppS_W'][4]:+.1f} E_W3/W5 {100 * d['E_W'][2]:+.2f}/{100 * d['E_W'][4]:+.2f}"
          f" rho {d['rho1']:+.4f} corr {d['rho1_corr']:+.4f} n* {d['n_detect']:.0f}"
          f" slope {d['slope_R_s']:.2f} kappa {d['slope_s_R']:.3f} corr {d['corr_R_s']:.3f}")
    print(f"   longest {d['real_mean_longest']:.2f}/{d['shuf_mean_longest']:.2f} P10 {d['real_P10']:.3f}/{d['shuf_P10']:.3f}"
          f" P7 {d['real_P7']:.3f}/{d['shuf_P7']:.3f} wl4 {d['real_wl4']:.2f}/{d['shuf_wl4']:.2f} ({100 * (d['real_wl4'] / d['shuf_wl4'] - 1):+.0f}%)"
          f" wl5 {d['real_wl5']:.3f}/{d['shuf_wl5']:.3f} ({100 * (d['real_wl5'] / d['shuf_wl5'] - 1):+.0f}%)"
          f" sd_wr {d['sd_winrate']:.3f} pct45-55 {d['pct_45_55']:.3f}")
    if "mates_W" in d:
        print(f"   mates W1/W3/W5 {d['mates_W'][0]:+.1f}/{d['mates_W'][2]:+.1f}/{d['mates_W'][4]:+.1f}"
              f" weakest_mate loss/win/all {d['weakest_mate_loss']:.3f}/{d['weakest_mate_win']:.3f}/{d['weakest_mate_all']:.3f}"
              f" weakest_me {d['weakest_me_loss']:.3f}/{d['weakest_me_win']:.3f} team_weaker|loss {d['team_weaker_loss']:.3f}")
    K = 10 if nm == "elo10" else 32
    n = 5 if nm.startswith("t5") else 1
    th = elo_streak_excess(np.arange(1, 7), K, kappa=float(d["slope_s_R"]), team_size=n)[0]
    print(f"   theory(kappa=slope_s_R) W1..6 {np.round(100 * th, 2)} rho {elo_lag1(K, float(d['slope_s_R']), n):+.4f}")

sec("B' 单人校准池理论")
for K in (10, 20, 32):
    print(f"K={K}: b={elo_gain(K):.4f} sigma_e={elo_error_sd(K):.1f} W5={100 * elo_streak_excess(5, K)[0]:.2f} "
          f"overshoot5={elo_streak_excess(5, K)[1]:.1f} rho1={elo_lag1(K):.4f} n*={detect_games(elo_lag1(K)):.0f}")
print("5v5 K=32 kappa=1:", 100 * elo_streak_excess(5, 32, team_size=5)[0])

sec("C 波动模型（精确链，K=0）")
for nm in ("hmm", "tilt", "tilt_break", "fatigue"):
    ch = exact_chain(nm)
    pb = ch.mean_winrate()
    print(f"{nm}: pbar={pb:.4f} acf1={ch.autocorr(1):+.4f} acf5={ch.autocorr(5):+.4f} "
          f"L1..6 {[round(100 * (ch.cond_after_losses(k) - pb), 2) for k in range(1, 7)]} "
          f"W1..6 {[round(100 * (ch.cond_after_wins(k) - pb), 2) for k in range(1, 7)]}")
    print(f"   P(L1000>=10) {1 - ch.longest_loss_lt(1000, 10):.3f} vs iid same p {prob_longest_ge(1000, 1 - pb, 10):.3f};"
          f" wl4 {ch.expected_wklk(1000, 4):.2f} vs iid {expected_wklk(1000, pb, 4):.2f}; wl5 {ch.expected_wklk(1000, 5):.3f}"
          f" vs {expected_wklk(1000, pb, 5):.3f}; mean run {ch.loss_run_survival(400).sum():.3f}"
          f" vs iid {1 / pb:.3f}; P(run>=5|start) {ch.loss_run_survival(5)[-1]:.4f} vs {(1 - pb) ** 4:.4f}")
t = chain_tilt(30, 3, SIGMA_Q)
print("tilt30 p(L)=", np.round(t.pwin, 4), "stationary", np.round(t.stationary(), 4))
print("probit dilution sigma_u=100: E F(200+u) =", float(win_prob_noisy(np.array([200.0]), 100)[0]),
      " approx F(200/sqrt(1+pi c^2 s^2/8)) =", float(elo_F(200 / np.sqrt(1 + np.pi * C_ELO ** 2 * 100 ** 2 / 8))),
      " F(200)=", float(elo_F(200)))
a, b_ = STANDARD["hmm"].trans
print("hmm: pi_bad", a / (a + b_), "sojourn bad", 1 / b_, "normal", 1 / a, "rho_state", 1 - a - b_,
      "mean u", -120 * a / (a + b_), "sd u", 120 * np.sqrt(a / (a + b_) * b_ / (a + b_)),
      "p_bad", float(win_prob_noisy(np.array([-120.0]), SIGMA_Q)[0]))
for K in (10, 20, 32):
    bb = elo_gain(K)
    print(f"AR retained K={K} b={bb:.4f}:", {r: round(ar1_retained(r, bb), 3) for r in (0.5, 0.8, 0.9, 0.95, 0.98, 0.99)},
          "approx (1-r)/(1-r+b) at .9:", round(0.1 / (0.1 + bb), 3))
print("AR(0.9,60) K=0 lag1 linear:", (C_ELO / 4) ** 2 * 3600 * 0.9 / 0.25)

sec("C' 单人模拟汇总")
for nm in ("none", "iid", "ar1", "hmm", "tilt", "tilt_break", "fatigue"):
    for K in (0, K_ELO):
        d = run_standard(nm, K)
        h = d["longest_hist"].astype(float)
        hs = d["longest_hist_shuf"].astype(float)
        P10 = h[10:].sum() / h.sum()
        P10s = hs[10:].sum() / hs.sum()
        print(f"{nm} K={K}: pbar {d['pbar']:.3f} acf1 {d['acf'][0]:+.4f} (shuf {d['acf_shuf']:+.4f}) "
              f"W1 {100 * d['W'][0]:+.2f} W3 {100 * d['W'][2]:+.2f} W5 {100 * d['W'][4]:+.2f} "
              f"L1 {100 * d['L'][0]:+.2f} L3 {100 * d['L'][2]:+.2f} L5 {100 * d['L'][4]:+.2f} | "
              f"P10 {P10:.3f}/{P10s:.3f} mean longest {(h * np.arange(h.size)).sum() / h.sum():.2f}/"
              f"{(hs * np.arange(hs.size)).sum() / hs.sum():.2f} wl4 {d['wl4']:.2f}/{d['wl4_shuf']:.2f} "
              f"({100 * (d['wl4'] / d['wl4_shuf'] - 1):+.0f}%) wl5 {d['wl5']:.3f}/{d['wl5_shuf']:.3f} "
              f"({100 * (d['wl5'] / d['wl5_shuf'] - 1):+.0f}%)")
    if nm == "fatigue":
        print("   winrate by j (K=20):", np.round(100 * run_standard(nm, K_ELO)["winrate_by_j"][:12], 1))

sec("D 8 人名次游戏")
for d_ in (10, 20, 30, 40):
    print(f"drought >= {d_} in 100: {prob_longest_ge(100, 7 / 8, d_):.4f}; in 500: {prob_longest_ge(500, 7 / 8, d_):.4f}")
E, sd, med, p95, ge = longest_run_distribution(100, 7 / 8, rmax=200)
print("longest drought in 100: E", E, "median", med, "p95", p95, "GSW", schilling_mean(100, 7 / 8))
print("P(no 1st in a given 10)", (7 / 8) ** 10, " bottom-4 run >=5 in 100:", prob_longest_ge(100, 0.5, 5))
