# winrate_sim.py results  (N=10000 players, skill ~ N(1500, 200^2), 3000 rounds, burn-in 1000, window = last 2000 games per player; SBMM queue jitter sd 100 unless stated)

## A. Analytic: random matchmaking, 1v1 vs 5v5, normal approximation of Elo logistic
| decile | E[z] | 1v1 | 1v1 + form noise 150 | 5v5 sum-model | 5v5 mean-model |
|---|---|---|---|---|---|
| 1 | -1.755 | 16.3% | 19.9% | 34.7% | 41.3% |
| 2 | -1.045 | 27.9% | 30.7% | 40.7% | 44.8% |
| 3 | -0.677 | 35.2% | 37.2% | 44.0% | 46.6% |
| 4 | -0.386 | 41.4% | 42.6% | 46.6% | 48.1% |
| 5 | -0.126 | 47.2% | 47.6% | 48.9% | 49.4% |
| 6 | +0.126 | 52.8% | 52.4% | 51.1% | 50.6% |
| 7 | +0.386 | 58.6% | 57.4% | 53.4% | 51.9% |
| 8 | +0.677 | 64.8% | 62.8% | 56.0% | 53.4% |
| 9 | +1.045 | 72.1% | 69.3% | 59.3% | 55.2% |
| 10 | +1.755 | 83.7% | 80.1% | 65.3% | 58.7% |

## B. Analytic: binomial uncertainty of an observed win rate (p = 0.5)
| games n | SE | 95% half-width (Wald) | Wilson 95% CI if observed 52% |
|---|---|---|---|
| 20 | 11.18 pp | +/-21.91 pp | 29.9%-70.1% |
| 50 | 7.07 pp | +/-13.86 pp | 38.5%-65.2% |
| 100 | 5.00 pp | +/-9.80 pp | 42.3%-61.5% |
| 200 | 3.54 pp | +/-6.93 pp | 45.1%-58.8% |
| 500 | 2.24 pp | +/-4.38 pp | 47.6%-56.3% |
| 1000 | 1.58 pp | +/-3.10 pp | 48.9%-55.1% |
| 2000 | 1.12 pp | +/-2.19 pp | 49.8%-54.2% |
| 5000 | 0.71 pp | +/-1.39 pp | 50.6%-53.4% |
n to detect 52% vs 50% (two-sided a=0.05, power 0.80): 4903; (one-sided a=0.05, power 0.80): 3862; (two-sided a=0.05, power 0.90): 6563

## C. Analytic: Elo stationary error and time constant (linearised, perfectly matched 1v1)
| K | Kc | tau = 1/(Kc) games | half-life games | sd(R-s) approx sqrt(200K/ln10) | sd with (2-Kc) and opp-noise correction |
|---|---|---|---|---|---|
| 10 | 0.0144 | 69.5 | 48.2 | 29.5 | 29.7 |
| 16 | 0.0230 | 43.4 | 30.1 | 37.3 | 37.7 |
| 20 | 0.0288 | 34.7 | 24.1 | 41.7 | 42.3 |
| 32 | 0.0461 | 21.7 | 15.1 | 52.7 | 54.0 |
| 40 | 0.0576 | 17.4 | 12.0 | 58.9 | 60.7 |

## D. Analytic: N-player free-for-all, Plackett-Luce (Gumbel performance), focal player vs an equal field
Focal edge d (Elo points) over each of the other N-1 players; w = 10^(d/400). P(1st) = w/(w+N-1); P(top k) = 1 - prod_{j=0}^{k-1} (N-1-j)/(w+N-1-j).
| d | w | 1v1 P(win) | 8-FFA P(1st) | 8-FFA P(top4) | 100-BR P(1st) | 100-BR P(top10) | 100-BR P(top50) |
|---|---|---|---|---|---|---|---|
| -200 | 0.32 | 24.0% | 4.3% | 20.8% | 0.32% | 3.3% | 19.8% |
| +0 | 1.00 | 50.0% | 12.5% | 50.0% | 1.00% | 10.0% | 50.0% |
| +100 | 1.78 | 64.0% | 20.3% | 68.6% | 1.76% | 17.0% | 70.6% |
| +200 | 3.16 | 76.0% | 31.1% | 84.6% | 3.10% | 28.1% | 88.5% |
| +400 | 10.00 | 90.9% | 58.8% | 98.5% | 9.17% | 63.5% | 99.9% |

## 1v1 random K=16
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1152 | 16.8% | 9.8-22.7% | 1139 | 16.8% | -0.00 pp |
| 2 | 1296 | 27.7% | 24.3-31.1% | 1287 | 27.7% | -0.01 pp |
| 3 | 1370 | 35.1% | 32.0-38.0% | 1362 | 35.1% | -0.00 pp |
| 4 | 1429 | 41.5% | 38.7-44.2% | 1422 | 41.5% | +0.00 pp |
| 5 | 1480 | 47.2% | 44.5-49.9% | 1474 | 47.2% | -0.00 pp |
| 6 | 1531 | 52.9% | 50.4-55.5% | 1527 | 52.9% | +0.00 pp |
| 7 | 1581 | 58.6% | 55.8-61.5% | 1579 | 58.6% | +0.00 pp |
| 8 | 1641 | 65.0% | 61.9-68.1% | 1641 | 65.0% | +0.00 pp |
| 9 | 1716 | 72.4% | 69.2-75.6% | 1714 | 72.4% | -0.00 pp |
| 10 | 1854 | 82.9% | 77.3-90.1% | 1855 | 82.9% | +0.00 pp |
top 1% skill win rate 92.8%, bottom 1% 7.3%; sd of individual win rates 19.68 pp; stationary sd(R-s) 38.2; residual sd around fitted line 38.1; RMSE<=2x stationary after 90 games, <=1.1x after 236 games; slope(R on s) 1.021 [t=250: 0.92, t=500: 0.99, t=1000: 1.02, t=2000: 1.02, t=3000: 1.02], corr 0.983; 100-game-window win-rate variance / binomial = 1.00; share of 100-game windows >=60%: 33.9%, <=40%: 33.9%  [2s]

## 1v1 SBMM K=16
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1144 | 42.2% | 39.6-44.1% | 1079 | 42.2% | -0.04 pp |
| 2 | 1287 | 45.3% | 44.4-46.2% | 1247 | 45.3% | -0.03 pp |
| 3 | 1360 | 46.9% | 46.2-47.8% | 1335 | 47.0% | -0.03 pp |
| 4 | 1419 | 48.3% | 47.5-49.0% | 1407 | 48.3% | -0.01 pp |
| 5 | 1473 | 49.5% | 48.8-50.1% | 1469 | 49.5% | -0.00 pp |
| 6 | 1524 | 50.6% | 49.9-51.2% | 1532 | 50.6% | +0.00 pp |
| 7 | 1575 | 51.7% | 51.0-52.4% | 1595 | 51.7% | +0.02 pp |
| 8 | 1634 | 53.0% | 52.2-53.7% | 1661 | 53.0% | +0.00 pp |
| 9 | 1709 | 54.7% | 53.7-55.6% | 1755 | 54.6% | +0.03 pp |
| 10 | 1848 | 57.9% | 55.9-60.7% | 1920 | 57.9% | +0.05 pp |
top 1% skill win rate 62.2%, bottom 1% 38.4%; sd of individual win rates 4.50 pp; stationary sd(R-s) 55.2; residual sd around fitted line 41.3; RMSE<=2x stationary after 55 games, <=1.1x after 153 games; slope(R on s) 1.196 [t=250: 0.88, t=500: 1.04, t=1000: 1.15, t=2000: 1.19, t=3000: 1.20], corr 0.986; 100-game-window win-rate variance / binomial = 0.56; share of 100-game windows >=60%: 5.0%, <=40%: 4.9%  [2s]

## 1v1 strict-SBMM(jitter20) K=16
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1145 | 48.8% | 48.4-49.2% | 762 | 49.7% | -0.90 pp |
| 2 | 1291 | 49.3% | 49.0-49.6% | 1063 | 49.8% | -0.54 pp |
| 3 | 1364 | 49.6% | 49.2-49.9% | 1217 | 49.9% | -0.34 pp |
| 4 | 1421 | 49.7% | 49.4-50.0% | 1337 | 49.9% | -0.20 pp |
| 5 | 1473 | 49.9% | 49.6-50.2% | 1446 | 50.0% | -0.07 pp |
| 6 | 1525 | 50.1% | 49.8-50.4% | 1554 | 50.0% | +0.07 pp |
| 7 | 1577 | 50.3% | 50.0-50.5% | 1661 | 50.1% | +0.19 pp |
| 8 | 1634 | 50.5% | 50.1-50.7% | 1785 | 50.1% | +0.35 pp |
| 9 | 1704 | 50.7% | 50.4-51.0% | 1939 | 50.2% | +0.54 pp |
| 10 | 1844 | 51.2% | 50.7-51.7% | 2235 | 50.3% | +0.90 pp |
top 1% skill win rate 51.8%, bottom 1% 48.2%; sd of individual win rates 0.72 pp; stationary sd(R-s) 152.9; residual sd around fitted line 54.6; RMSE<=2x stationary after 1 games, <=1.1x after 14 games; slope(R on s) 2.108 [t=250: 0.69, t=500: 0.94, t=1000: 1.28, t=2000: 1.75, t=3000: 2.11], corr 0.992; 100-game-window win-rate variance / binomial = 0.59; share of 100-game windows >=60%: 0.6%, <=40%: 0.6%  [2s]

## 5v5 random sum-model K=16
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1148 | 34.8% | 30.0-38.5% | 1136 | 34.8% | -0.02 pp |
| 2 | 1289 | 40.8% | 38.8-42.8% | 1284 | 40.8% | -0.01 pp |
| 3 | 1361 | 43.9% | 42.1-45.7% | 1359 | 43.9% | -0.01 pp |
| 4 | 1419 | 46.5% | 44.8-48.2% | 1421 | 46.5% | -0.00 pp |
| 5 | 1472 | 48.9% | 47.1-50.5% | 1474 | 48.9% | -0.01 pp |
| 6 | 1523 | 51.2% | 49.5-53.0% | 1525 | 51.2% | -0.01 pp |
| 7 | 1575 | 53.5% | 51.9-55.2% | 1583 | 53.5% | +0.00 pp |
| 8 | 1633 | 56.2% | 54.4-57.8% | 1647 | 56.1% | +0.03 pp |
| 9 | 1703 | 59.3% | 57.3-61.4% | 1717 | 59.2% | +0.02 pp |
| 10 | 1837 | 65.0% | 61.5-69.5% | 1855 | 64.9% | +0.02 pp |
top 1% skill win rate 71.8%, bottom 1% 27.7%; sd of individual win rates 8.75 pp; stationary sd(R-s) 58.5; residual sd around fitted line 58.4; RMSE<=2x stationary after 101 games, <=1.1x after 324 games; slope(R on s) 1.045 [t=250: 0.75, t=500: 0.93, t=1000: 1.02, t=2000: 1.04, t=3000: 1.05], corr 0.962; 100-game-window win-rate variance / binomial = 1.00; share of 100-game windows >=60%: 17.6%, <=40%: 17.6%  [2s]

## 5v5 SBMM sum-model K=16
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1142 | 46.6% | 45.3-47.6% | 985 | 46.9% | -0.34 pp |
| 2 | 1286 | 48.0% | 47.3-48.6% | 1196 | 48.2% | -0.20 pp |
| 3 | 1359 | 48.7% | 48.0-49.3% | 1301 | 48.8% | -0.13 pp |
| 4 | 1419 | 49.2% | 48.6-49.9% | 1386 | 49.3% | -0.07 pp |
| 5 | 1474 | 49.8% | 49.1-50.3% | 1466 | 49.8% | -0.02 pp |
| 6 | 1525 | 50.2% | 49.5-50.8% | 1538 | 50.2% | +0.02 pp |
| 7 | 1574 | 50.7% | 50.1-51.4% | 1613 | 50.7% | +0.07 pp |
| 8 | 1631 | 51.3% | 50.7-52.0% | 1698 | 51.2% | +0.14 pp |
| 9 | 1704 | 52.1% | 51.3-52.8% | 1800 | 51.9% | +0.18 pp |
| 10 | 1849 | 53.4% | 52.4-54.6% | 2016 | 53.1% | +0.34 pp |
top 1% skill win rate 55.1%, bottom 1% 44.7%; sd of individual win rates 2.02 pp; stationary sd(R-s) 95.1; residual sd around fitted line 68.3; RMSE<=2x stationary after 9 games, <=1.1x after 144 games; slope(R on s) 1.456 [t=250: 0.70, t=500: 0.93, t=1000: 1.15, t=2000: 1.36, t=3000: 1.46], corr 0.974; 100-game-window win-rate variance / binomial = 0.79; share of 100-game windows >=60%: 2.4%, <=40%: 2.3%  [2s]

## FFA8 random K=16
| decile | mean skill | P(1st) | P(top4) | avg place | P(1st) p10-p90 | mean rating |
|---|---|---|---|---|---|---|
| 1 | 1149 | 1.4% | 10.6% | 6.81 | 0.7-2.1% | 1148 |
| 2 | 1293 | 2.9% | 20.6% | 6.04 | 2.2-3.6% | 1291 |
| 3 | 1366 | 4.3% | 28.7% | 5.53 | 3.5-5.1% | 1366 |
| 4 | 1423 | 5.8% | 36.5% | 5.10 | 4.9-6.8% | 1424 |
| 5 | 1474 | 7.6% | 44.3% | 4.70 | 6.6-8.6% | 1475 |
| 6 | 1524 | 9.9% | 52.6% | 4.30 | 8.7-11.1% | 1524 |
| 7 | 1575 | 12.8% | 61.3% | 3.90 | 11.2-14.3% | 1576 |
| 8 | 1633 | 16.8% | 70.9% | 3.46 | 14.6-19.1% | 1635 |
| 9 | 1706 | 23.2% | 81.1% | 2.96 | 19.9-27.0% | 1706 |
| 10 | 1851 | 40.2% | 93.3% | 2.18 | 29.2-56.1% | 1854 |
top 1% skill win rate 64.8%, bottom 1% 0.5%; sd of individual win rates 11.80 pp; stationary sd(R-s) 22.8; residual sd around fitted line 22.8; RMSE<=2x stationary after 151 games, <=1.1x after 334 games; slope(R on s) 1.005 [t=250: 0.91, t=500: 0.99, t=1000: 1.00, t=2000: 1.01, t=3000: 1.01], corr 0.994; 100-game-window win-rate variance / binomial = 1.00; share of 100-game windows >=60%: 0.8%, <=40%: 95.9%  [8s]

## FFA8 SBMM K=16
| decile | mean skill | P(1st) | P(top4) | avg place | P(1st) p10-p90 | mean rating |
|---|---|---|---|---|---|---|
| 1 | 1150 | 8.9% | 39.3% | 5.09 | 7.8-9.9% | 1121 |
| 2 | 1296 | 10.1% | 43.3% | 4.86 | 9.3-10.9% | 1276 |
| 3 | 1369 | 10.8% | 45.6% | 4.74 | 10.0-11.6% | 1357 |
| 4 | 1428 | 11.5% | 47.4% | 4.64 | 10.6-12.3% | 1420 |
| 5 | 1478 | 12.0% | 49.1% | 4.55 | 11.2-12.8% | 1473 |
| 6 | 1527 | 12.6% | 50.7% | 4.46 | 11.8-13.5% | 1526 |
| 7 | 1581 | 13.2% | 52.5% | 4.36 | 12.4-14.1% | 1585 |
| 8 | 1637 | 14.0% | 54.3% | 4.26 | 13.1-14.9% | 1642 |
| 9 | 1710 | 14.9% | 56.7% | 4.14 | 14.0-15.9% | 1722 |
| 10 | 1858 | 16.9% | 61.1% | 3.91 | 15.3-18.6% | 1878 |
top 1% skill win rate 19.5%, bottom 1% 7.4%; sd of individual win rates 2.39 pp; stationary sd(R-s) 28.4; residual sd around fitted line 24.7; RMSE<=2x stationary after 163 games, <=1.1x after 323 games; slope(R on s) 1.071 [t=250: 0.84, t=500: 0.97, t=1000: 1.05, t=2000: 1.07, t=3000: 1.07], corr 0.993; 100-game-window win-rate variance / binomial = 0.86; share of 100-game windows >=60%: 0.0%, <=40%: 100.0%  [10s]

## 1v1 random +form-noise150 K=16
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1150 | 20.7% | 13.6-26.2% | 1218 | 20.7% | +0.00 pp |
| 2 | 1290 | 30.8% | 27.8-33.8% | 1333 | 30.8% | +0.01 pp |
| 3 | 1361 | 37.2% | 34.4-39.9% | 1390 | 37.2% | -0.00 pp |
| 4 | 1419 | 42.5% | 40.1-44.7% | 1435 | 42.5% | -0.01 pp |
| 5 | 1471 | 47.4% | 45.0-49.9% | 1477 | 47.4% | -0.01 pp |
| 6 | 1522 | 52.3% | 49.8-54.8% | 1519 | 52.3% | -0.00 pp |
| 7 | 1576 | 57.4% | 55.0-59.8% | 1564 | 57.4% | +0.01 pp |
| 8 | 1634 | 62.9% | 60.2-65.6% | 1611 | 62.9% | -0.00 pp |
| 9 | 1708 | 69.3% | 66.2-72.5% | 1669 | 69.3% | +0.00 pp |
| 10 | 1849 | 79.5% | 73.9-87.1% | 1783 | 79.5% | -0.00 pp |
top 1% skill win rate 89.7%, bottom 1% 10.6%; sd of individual win rates 17.33 pp; stationary sd(R-s) 53.6; residual sd around fitted line 38.1; RMSE<=2x stationary after 65 games, <=1.1x after 267 games; slope(R on s) 0.810 [t=250: 0.76, t=500: 0.80, t=1000: 0.81, t=2000: 0.81, t=3000: 0.81], corr 0.973; 100-game-window win-rate variance / binomial = 1.00; share of 100-game windows >=60%: 31.6%, <=40%: 31.7%  [2s]

## 1v1 SBMM +form-noise150 K=16
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1150 | 40.9% | 38.1-43.1% | 1174 | 40.9% | -0.02 pp |
| 2 | 1293 | 44.5% | 43.4-45.6% | 1309 | 44.5% | -0.00 pp |
| 3 | 1364 | 46.4% | 45.6-47.3% | 1374 | 46.4% | -0.00 pp |
| 4 | 1421 | 48.0% | 47.2-48.8% | 1425 | 48.0% | -0.01 pp |
| 5 | 1472 | 49.3% | 48.6-50.1% | 1474 | 49.4% | -0.01 pp |
| 6 | 1523 | 50.7% | 50.0-51.5% | 1523 | 50.7% | +0.00 pp |
| 7 | 1575 | 52.1% | 51.3-52.9% | 1574 | 52.1% | +0.02 pp |
| 8 | 1632 | 53.6% | 52.8-54.4% | 1625 | 53.6% | +0.01 pp |
| 9 | 1705 | 55.4% | 54.5-56.4% | 1691 | 55.4% | +0.00 pp |
| 10 | 1855 | 59.0% | 56.8-61.8% | 1831 | 59.0% | +0.01 pp |
top 1% skill win rate 63.4%, bottom 1% 36.4%; sd of individual win rates 5.21 pp; stationary sd(R-s) 43.4; residual sd around fitted line 41.0; RMSE<=2x stationary after 122 games, <=1.1x after 519 games; slope(R on s) 0.931 [t=250: 0.76, t=500: 0.86, t=1000: 0.92, t=2000: 0.93, t=3000: 0.93], corr 0.977; 100-game-window win-rate variance / binomial = 0.57; share of 100-game windows >=60%: 6.7%, <=40%: 6.8%  [3s]

## 1v1 random +AR1 form sd100 phi0.99 K=16
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1152 | 18.7% | 11.3-25.6% | 1155 | 18.7% | -0.02 pp |
| 2 | 1292 | 29.3% | 24.8-33.9% | 1303 | 29.2% | +0.02 pp |
| 3 | 1366 | 36.3% | 31.5-41.0% | 1373 | 36.3% | +0.01 pp |
| 4 | 1424 | 42.0% | 37.1-46.9% | 1425 | 42.0% | -0.00 pp |
| 5 | 1477 | 47.5% | 42.7-52.3% | 1480 | 47.5% | +0.01 pp |
| 6 | 1528 | 52.9% | 48.1-57.6% | 1528 | 52.9% | +0.00 pp |
| 7 | 1578 | 58.0% | 53.1-62.8% | 1572 | 58.0% | -0.01 pp |
| 8 | 1635 | 63.6% | 59.1-68.4% | 1629 | 63.7% | -0.01 pp |
| 9 | 1708 | 70.5% | 65.5-75.1% | 1697 | 70.5% | -0.01 pp |
| 10 | 1852 | 81.3% | 74.6-88.7% | 1837 | 81.3% | +0.00 pp |
top 1% skill win rate 91.0%, bottom 1% 9.1%; sd of individual win rates 18.69 pp; stationary sd(R-s) 74.5; residual sd around fitted line 82.8; RMSE<=2x stationary after 14 games, <=1.1x after 118 games; slope(R on s) 0.966 [t=250: 0.88, t=500: 0.96, t=1000: 0.97, t=2000: 0.97, t=3000: 0.97], corr 0.919; 100-game-window win-rate variance / binomial = 3.70; share of 100-game windows >=60%: 34.4%, <=40%: 34.3%  [2s]

## 1v1 SBMM +AR1 form sd100 phi0.99 K=16
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1145 | 42.8% | 40.4-44.9% | 1107 | 42.8% | -0.03 pp |
| 2 | 1289 | 45.7% | 44.4-46.9% | 1264 | 45.7% | -0.04 pp |
| 3 | 1361 | 47.2% | 46.1-48.4% | 1349 | 47.3% | -0.02 pp |
| 4 | 1417 | 48.4% | 47.1-49.6% | 1408 | 48.4% | -0.01 pp |
| 5 | 1468 | 49.4% | 48.2-50.5% | 1462 | 49.4% | -0.00 pp |
| 6 | 1521 | 50.6% | 49.4-51.7% | 1529 | 50.6% | -0.00 pp |
| 7 | 1573 | 51.6% | 50.4-52.8% | 1588 | 51.6% | +0.01 pp |
| 8 | 1631 | 52.8% | 51.6-54.0% | 1652 | 52.8% | +0.01 pp |
| 9 | 1704 | 54.3% | 53.0-55.6% | 1743 | 54.3% | +0.05 pp |
| 10 | 1849 | 57.2% | 55.1-59.7% | 1899 | 57.1% | +0.04 pp |
top 1% skill win rate 60.9%, bottom 1% 39.1%; sd of individual win rates 4.20 pp; stationary sd(R-s) 77.9; residual sd around fitted line 100.1; RMSE<=2x stationary after 1 games, <=1.1x after 72 games; slope(R on s) 1.131 [t=250: 0.84, t=500: 0.99, t=1000: 1.09, t=2000: 1.12, t=3000: 1.13], corr 0.915; 100-game-window win-rate variance / binomial = 1.64; share of 100-game windows >=60%: 10.4%, <=40%: 10.3%  [3s]

## 1v1 random K=32
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1155 | 17.4% | 10.2-23.0% | 1145 | 17.4% | +0.00 pp |
| 2 | 1291 | 28.0% | 24.6-31.2% | 1287 | 28.0% | +0.00 pp |
| 3 | 1362 | 35.1% | 32.2-38.0% | 1360 | 35.1% | -0.00 pp |
| 4 | 1419 | 41.3% | 38.6-43.9% | 1417 | 41.3% | -0.00 pp |
| 5 | 1470 | 47.0% | 44.4-49.5% | 1473 | 47.0% | +0.00 pp |
| 6 | 1519 | 52.6% | 49.9-55.2% | 1521 | 52.6% | -0.00 pp |
| 7 | 1572 | 58.5% | 55.6-61.2% | 1578 | 58.5% | -0.01 pp |
| 8 | 1631 | 64.8% | 62.0-67.8% | 1638 | 64.8% | +0.00 pp |
| 9 | 1706 | 72.3% | 68.6-75.9% | 1718 | 72.3% | +0.01 pp |
| 10 | 1847 | 83.1% | 77.8-89.8% | 1863 | 83.1% | -0.00 pp |
top 1% skill win rate 92.5%, bottom 1% 7.9%; sd of individual win rates 19.58 pp; stationary sd(R-s) 55.1; residual sd around fitted line 54.4; RMSE<=2x stationary after 25 games, <=1.1x after 82 games; slope(R on s) 1.037 [t=250: 1.01, t=500: 1.03, t=1000: 1.04, t=2000: 1.04, t=3000: 1.04], corr 0.967; 100-game-window win-rate variance / binomial = 1.00; share of 100-game windows >=60%: 33.7%, <=40%: 34.0%  [2s]

## 1v1 SBMM K=32
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1147 | 43.5% | 41.4-45.1% | 977 | 43.5% | -0.02 pp |
| 2 | 1290 | 46.1% | 45.3-46.9% | 1192 | 46.1% | -0.01 pp |
| 3 | 1361 | 47.5% | 46.8-48.1% | 1298 | 47.5% | -0.01 pp |
| 4 | 1418 | 48.6% | 47.9-49.2% | 1380 | 48.6% | -0.02 pp |
| 5 | 1470 | 49.5% | 48.9-50.1% | 1458 | 49.5% | +0.00 pp |
| 6 | 1520 | 50.5% | 49.9-51.1% | 1536 | 50.5% | -0.00 pp |
| 7 | 1573 | 51.5% | 50.8-52.1% | 1615 | 51.5% | +0.00 pp |
| 8 | 1631 | 52.6% | 51.8-53.2% | 1701 | 52.5% | +0.01 pp |
| 9 | 1703 | 53.9% | 53.0-54.6% | 1812 | 53.8% | +0.01 pp |
| 10 | 1851 | 56.4% | 54.9-58.7% | 2031 | 56.4% | +0.02 pp |
top 1% skill win rate 59.8%, bottom 1% 40.0%; sd of individual win rates 3.71 pp; stationary sd(R-s) 117.3; residual sd around fitted line 66.2; RMSE<=2x stationary after 1 games, <=1.1x after 19 games; slope(R on s) 1.496 [t=250: 1.16, t=500: 1.34, t=1000: 1.46, t=2000: 1.49, t=3000: 1.50], corr 0.976; 100-game-window win-rate variance / binomial = 0.42; share of 100-game windows >=60%: 2.6%, <=40%: 2.5%  [2s]

## 1v1 strict-SBMM(jitter20) K=32
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1154 | 48.9% | 48.5-49.4% | 41 | 49.9% | -0.95 pp |
| 2 | 1293 | 49.3% | 49.0-49.7% | 630 | 49.9% | -0.56 pp |
| 3 | 1365 | 49.6% | 49.2-49.9% | 934 | 49.9% | -0.37 pp |
| 4 | 1423 | 49.8% | 49.5-50.0% | 1176 | 50.0% | -0.21 pp |
| 5 | 1476 | 49.9% | 49.6-50.2% | 1396 | 50.0% | -0.06 pp |
| 6 | 1528 | 50.1% | 49.8-50.3% | 1605 | 50.0% | +0.06 pp |
| 7 | 1580 | 50.2% | 49.9-50.5% | 1821 | 50.0% | +0.20 pp |
| 8 | 1637 | 50.4% | 50.1-50.7% | 2066 | 50.1% | +0.37 pp |
| 9 | 1710 | 50.7% | 50.3-50.9% | 2370 | 50.1% | +0.57 pp |
| 10 | 1852 | 51.1% | 50.7-51.5% | 2961 | 50.1% | +0.95 pp |
top 1% skill win rate 51.7%, bottom 1% 48.3%; sd of individual win rates 0.68 pp; stationary sd(R-s) 481.6; residual sd around fitted line 109.2; RMSE<=2x stationary after 1 games, <=1.1x after 1 games; slope(R on s) 4.176 [t=250: 1.24, t=500: 1.74, t=1000: 2.44, t=2000: 3.42, t=3000: 4.18], corr 0.991; 100-game-window win-rate variance / binomial = 0.58; share of 100-game windows >=60%: 0.6%, <=40%: 0.6%  [2s]

## 5v5 random sum-model K=32
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1147 | 34.7% | 29.6-38.5% | 1117 | 34.7% | +0.00 pp |
| 2 | 1290 | 40.6% | 38.6-42.6% | 1271 | 40.6% | +0.00 pp |
| 3 | 1364 | 43.9% | 42.2-45.7% | 1350 | 43.9% | -0.00 pp |
| 4 | 1423 | 46.5% | 44.8-48.2% | 1416 | 46.5% | -0.00 pp |
| 5 | 1478 | 48.9% | 47.2-50.6% | 1474 | 48.9% | +0.01 pp |
| 6 | 1529 | 51.2% | 49.5-52.8% | 1523 | 51.2% | -0.01 pp |
| 7 | 1581 | 53.5% | 51.8-55.1% | 1588 | 53.5% | +0.00 pp |
| 8 | 1638 | 56.1% | 54.2-57.8% | 1644 | 56.1% | -0.01 pp |
| 9 | 1712 | 59.3% | 57.4-61.4% | 1729 | 59.3% | -0.01 pp |
| 10 | 1855 | 65.3% | 61.6-69.9% | 1887 | 65.3% | +0.00 pp |
top 1% skill win rate 72.4%, bottom 1% 27.3%; sd of individual win rates 8.85 pp; stationary sd(R-s) 87.4; residual sd around fitted line 84.3; RMSE<=2x stationary after 14 games, <=1.1x after 114 games; slope(R on s) 1.085 [t=250: 0.95, t=500: 1.06, t=1000: 1.09, t=2000: 1.09, t=3000: 1.09], corr 0.933; 100-game-window win-rate variance / binomial = 1.00; share of 100-game windows >=60%: 17.6%, <=40%: 17.7%  [3s]

## 5v5 SBMM sum-model K=32
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1147 | 47.6% | 46.6-48.5% | 599 | 48.0% | -0.41 pp |
| 2 | 1287 | 48.6% | 48.0-49.2% | 958 | 48.8% | -0.25 pp |
| 3 | 1364 | 49.1% | 48.5-49.6% | 1157 | 49.2% | -0.15 pp |
| 4 | 1422 | 49.5% | 48.9-50.0% | 1303 | 49.5% | -0.08 pp |
| 5 | 1473 | 49.8% | 49.2-50.4% | 1437 | 49.9% | -0.03 pp |
| 6 | 1521 | 50.2% | 49.6-50.8% | 1562 | 50.2% | +0.03 pp |
| 7 | 1574 | 50.5% | 49.9-51.1% | 1690 | 50.4% | +0.08 pp |
| 8 | 1634 | 50.9% | 50.3-51.5% | 1849 | 50.7% | +0.15 pp |
| 9 | 1707 | 51.4% | 50.8-52.0% | 2043 | 51.2% | +0.26 pp |
| 10 | 1849 | 52.4% | 51.5-53.3% | 2401 | 52.0% | +0.40 pp |
top 1% skill win rate 53.5%, bottom 1% 46.3%; sd of individual win rates 1.43 pp; stationary sd(R-s) 278.4; residual sd around fitted line 133.4; RMSE<=2x stationary after 1 games, <=1.1x after 1 games; slope(R on s) 2.568 [t=250: 1.08, t=500: 1.42, t=1000: 1.83, t=2000: 2.28, t=3000: 2.57], corr 0.968; 100-game-window win-rate variance / binomial = 0.74; share of 100-game windows >=60%: 1.6%, <=40%: 1.6%  [2s]

## FFA8 random K=32
| decile | mean skill | P(1st) | P(top4) | avg place | P(1st) p10-p90 | mean rating |
|---|---|---|---|---|---|---|
| 1 | 1145 | 1.4% | 10.7% | 6.81 | 0.6-2.1% | 1145 |
| 2 | 1286 | 2.9% | 20.4% | 6.05 | 2.2-3.5% | 1289 |
| 3 | 1358 | 4.2% | 28.3% | 5.56 | 3.4-5.1% | 1361 |
| 4 | 1415 | 5.7% | 36.0% | 5.12 | 4.9-6.7% | 1421 |
| 5 | 1468 | 7.6% | 44.2% | 4.71 | 6.5-8.7% | 1474 |
| 6 | 1520 | 9.9% | 52.8% | 4.30 | 8.6-11.3% | 1527 |
| 7 | 1574 | 13.0% | 61.8% | 3.88 | 11.4-14.6% | 1581 |
| 8 | 1631 | 16.9% | 71.1% | 3.45 | 14.8-19.1% | 1637 |
| 9 | 1705 | 23.6% | 81.6% | 2.93 | 20.1-27.3% | 1713 |
| 10 | 1844 | 39.8% | 93.2% | 2.19 | 29.8-54.6% | 1853 |
top 1% skill win rate 63.1%, bottom 1% 0.5%; sd of individual win rates 11.73 pp; stationary sd(R-s) 32.5; residual sd around fitted line 32.3; RMSE<=2x stationary after 54 games, <=1.1x after 133 games; slope(R on s) 1.012 [t=250: 1.00, t=500: 1.01, t=1000: 1.01, t=2000: 1.01, t=3000: 1.01], corr 0.987; 100-game-window win-rate variance / binomial = 1.00; share of 100-game windows >=60%: 0.7%, <=40%: 96.1%  [8s]

## FFA8 SBMM K=32
| decile | mean skill | P(1st) | P(top4) | avg place | P(1st) p10-p90 | mean rating |
|---|---|---|---|---|---|---|
| 1 | 1151 | 9.1% | 39.9% | 5.06 | 8.0-10.1% | 1097 |
| 2 | 1291 | 10.3% | 43.9% | 4.83 | 9.4-11.1% | 1259 |
| 3 | 1364 | 11.0% | 45.9% | 4.72 | 10.2-11.8% | 1342 |
| 4 | 1421 | 11.5% | 47.6% | 4.63 | 10.8-12.3% | 1408 |
| 5 | 1473 | 12.1% | 49.1% | 4.54 | 11.2-12.9% | 1472 |
| 6 | 1524 | 12.6% | 50.6% | 4.46 | 11.8-13.5% | 1530 |
| 7 | 1576 | 13.2% | 52.2% | 4.37 | 12.4-14.1% | 1590 |
| 8 | 1633 | 13.8% | 54.0% | 4.28 | 13.0-14.6% | 1658 |
| 9 | 1706 | 14.8% | 56.2% | 4.16 | 13.9-15.8% | 1740 |
| 10 | 1850 | 16.6% | 60.5% | 3.94 | 15.2-18.3% | 1904 |
top 1% skill win rate 19.1%, bottom 1% 7.6%; sd of individual win rates 2.25 pp; stationary sd(R-s) 48.2; residual sd around fitted line 36.6; RMSE<=2x stationary after 35 games, <=1.1x after 89 games; slope(R on s) 1.157 [t=250: 1.03, t=500: 1.12, t=1000: 1.15, t=2000: 1.16, t=3000: 1.16], corr 0.988; 100-game-window win-rate variance / binomial = 0.81; share of 100-game windows >=60%: 0.0%, <=40%: 100.0%  [10s]

## 1v1 random +form-noise150 K=32
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1150 | 20.5% | 13.5-26.0% | 1208 | 20.5% | -0.00 pp |
| 2 | 1292 | 30.8% | 27.5-33.9% | 1325 | 30.8% | -0.01 pp |
| 3 | 1365 | 37.2% | 34.6-39.9% | 1390 | 37.2% | +0.00 pp |
| 4 | 1425 | 42.8% | 40.2-45.2% | 1439 | 42.7% | +0.01 pp |
| 5 | 1477 | 47.7% | 45.3-50.1% | 1483 | 47.7% | +0.00 pp |
| 6 | 1525 | 52.3% | 50.1-54.8% | 1519 | 52.3% | +0.00 pp |
| 7 | 1578 | 57.4% | 54.9-59.9% | 1563 | 57.4% | -0.01 pp |
| 8 | 1637 | 62.9% | 60.2-65.5% | 1612 | 62.9% | +0.00 pp |
| 9 | 1707 | 69.0% | 66.0-72.4% | 1672 | 69.0% | +0.00 pp |
| 10 | 1847 | 79.3% | 73.9-85.8% | 1789 | 79.3% | +0.01 pp |
top 1% skill win rate 88.9%, bottom 1% 10.5%; sd of individual win rates 17.29 pp; stationary sd(R-s) 64.7; residual sd around fitted line 54.4; RMSE<=2x stationary after 22 games, <=1.1x after 117 games; slope(R on s) 0.832 [t=250: 0.82, t=500: 0.82, t=1000: 0.83, t=2000: 0.83, t=3000: 0.83], corr 0.950; 100-game-window win-rate variance / binomial = 1.00; share of 100-game windows >=60%: 31.6%, <=40%: 31.3%  [2s]

## 1v1 SBMM +form-noise150 K=32
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1148 | 42.4% | 40.0-44.2% | 1087 | 42.4% | -0.01 pp |
| 2 | 1292 | 45.5% | 44.5-46.4% | 1257 | 45.5% | +0.00 pp |
| 3 | 1364 | 47.0% | 46.3-47.8% | 1339 | 47.0% | +0.00 pp |
| 4 | 1423 | 48.3% | 47.6-49.1% | 1410 | 48.3% | +0.00 pp |
| 5 | 1475 | 49.4% | 48.8-50.1% | 1470 | 49.4% | -0.00 pp |
| 6 | 1524 | 50.5% | 49.8-51.2% | 1530 | 50.5% | +0.00 pp |
| 7 | 1578 | 51.7% | 51.0-52.4% | 1591 | 51.7% | -0.01 pp |
| 8 | 1636 | 52.9% | 52.2-53.7% | 1659 | 52.9% | -0.00 pp |
| 9 | 1709 | 54.6% | 53.6-55.5% | 1743 | 54.6% | -0.00 pp |
| 10 | 1850 | 57.6% | 55.7-60.0% | 1914 | 57.6% | +0.01 pp |
top 1% skill win rate 61.2%, bottom 1% 38.6%; sd of individual win rates 4.35 pp; stationary sd(R-s) 74.1; residual sd around fitted line 65.7; RMSE<=2x stationary after 15 games, <=1.1x after 73 games; slope(R on s) 1.174 [t=250: 0.99, t=500: 1.10, t=1000: 1.16, t=2000: 1.17, t=3000: 1.17], corr 0.963; 100-game-window win-rate variance / binomial = 0.43; share of 100-game windows >=60%: 3.9%, <=40%: 3.9%  [3s]

## 1v1 random +AR1 form sd100 phi0.99 K=32
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1148 | 18.7% | 11.3-25.2% | 1145 | 18.7% | -0.00 pp |
| 2 | 1289 | 29.3% | 24.7-34.0% | 1294 | 29.3% | +0.01 pp |
| 3 | 1362 | 36.1% | 31.4-40.9% | 1358 | 36.1% | -0.01 pp |
| 4 | 1419 | 41.9% | 37.0-46.7% | 1423 | 41.9% | +0.00 pp |
| 5 | 1471 | 47.0% | 42.3-51.7% | 1471 | 47.0% | +0.00 pp |
| 6 | 1521 | 52.5% | 47.8-57.0% | 1526 | 52.5% | +0.00 pp |
| 7 | 1574 | 57.9% | 52.9-62.9% | 1578 | 57.9% | +0.00 pp |
| 8 | 1636 | 64.0% | 59.4-68.5% | 1636 | 64.0% | -0.00 pp |
| 9 | 1712 | 71.0% | 66.2-75.8% | 1711 | 71.0% | -0.01 pp |
| 10 | 1857 | 81.7% | 75.1-89.0% | 1857 | 81.7% | +0.00 pp |
top 1% skill win rate 91.4%, bottom 1% 8.9%; sd of individual win rates 18.84 pp; stationary sd(R-s) 74.9; residual sd around fitted line 100.5; RMSE<=2x stationary after 1 games, <=1.1x after 38 games; slope(R on s) 0.999 [t=250: 0.98, t=500: 1.00, t=1000: 1.00, t=2000: 1.00, t=3000: 1.00], corr 0.895; 100-game-window win-rate variance / binomial = 3.66; share of 100-game windows >=60%: 34.4%, <=40%: 34.6%  [2s]

## 1v1 SBMM +AR1 form sd100 phi0.99 K=32
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1151 | 44.2% | 42.3-45.9% | 999 | 44.3% | -0.03 pp |
| 2 | 1291 | 46.5% | 45.5-47.6% | 1192 | 46.6% | -0.02 pp |
| 3 | 1366 | 47.8% | 46.9-48.8% | 1294 | 47.8% | -0.02 pp |
| 4 | 1423 | 48.8% | 47.9-49.7% | 1390 | 48.8% | -0.01 pp |
| 5 | 1474 | 49.6% | 48.6-50.5% | 1468 | 49.6% | +0.01 pp |
| 6 | 1524 | 50.5% | 49.5-51.4% | 1539 | 50.4% | +0.02 pp |
| 7 | 1577 | 51.3% | 50.2-52.2% | 1607 | 51.3% | +0.01 pp |
| 8 | 1636 | 52.2% | 51.2-53.2% | 1700 | 52.2% | +0.01 pp |
| 9 | 1711 | 53.4% | 52.3-54.5% | 1805 | 53.4% | +0.02 pp |
| 10 | 1854 | 55.7% | 54.0-57.6% | 2006 | 55.7% | +0.02 pp |
top 1% skill win rate 58.7%, bottom 1% 41.2%; sd of individual win rates 3.35 pp; stationary sd(R-s) 125.8; residual sd around fitted line 141.1; RMSE<=2x stationary after 1 games, <=1.1x after 4 games; slope(R on s) 1.445 [t=250: 1.11, t=500: 1.27, t=1000: 1.39, t=2000: 1.45, t=3000: 1.45], corr 0.899; 100-game-window win-rate variance / binomial = 1.07; share of 100-game windows >=60%: 5.7%, <=40%: 5.8%  [3s]

## 5v5 random mean-model K=16
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1158 | 41.1% | 37.9-43.9% | 1148 | 41.2% | -0.05 pp |
| 2 | 1297 | 44.7% | 43.0-46.3% | 1292 | 44.7% | -0.01 pp |
| 3 | 1364 | 46.4% | 44.9-47.9% | 1359 | 46.4% | -0.02 pp |
| 4 | 1422 | 47.9% | 46.4-49.4% | 1417 | 47.9% | -0.01 pp |
| 5 | 1477 | 49.3% | 47.9-50.9% | 1472 | 49.4% | -0.01 pp |
| 6 | 1527 | 50.7% | 49.1-52.2% | 1525 | 50.7% | -0.00 pp |
| 7 | 1578 | 52.0% | 50.5-53.5% | 1577 | 52.0% | +0.00 pp |
| 8 | 1636 | 53.5% | 51.9-55.0% | 1638 | 53.5% | +0.02 pp |
| 9 | 1710 | 55.3% | 53.8-57.0% | 1713 | 55.3% | +0.02 pp |
| 10 | 1853 | 59.0% | 56.4-62.3% | 1858 | 59.0% | +0.05 pp |
top 1% skill win rate 63.4%, bottom 1% 36.6%; sd of individual win rates 5.24 pp; stationary sd(R-s) 85.1; residual sd around fitted line 85.0; RMSE<=2x stationary after 48 games, <=1.1x after 359 games; slope(R on s) 1.022 [t=250: 0.62, t=500: 0.85, t=1000: 0.98, t=2000: 1.02, t=3000: 1.02], corr 0.922; 100-game-window win-rate variance / binomial = 1.00; share of 100-game windows >=60%: 9.3%, <=40%: 9.1%  [3s]

## 5v5 SBMM mean-model K=16
| decile | mean skill | mean win rate | p10-p90 of individual win rates | mean rating | mean expected score E | dR/(K*T) |
|---|---|---|---|---|---|---|
| 1 | 1150 | 48.0% | 47.1-48.9% | 912 | 48.6% | -0.60 pp |
| 2 | 1292 | 48.8% | 48.1-49.5% | 1140 | 49.2% | -0.38 pp |
| 3 | 1366 | 49.2% | 48.6-49.9% | 1270 | 49.5% | -0.24 pp |
| 4 | 1425 | 49.6% | 48.9-50.2% | 1375 | 49.7% | -0.12 pp |
| 5 | 1478 | 49.9% | 49.2-50.5% | 1461 | 49.9% | -0.04 pp |
| 6 | 1529 | 50.2% | 49.5-50.8% | 1541 | 50.1% | +0.05 pp |
| 7 | 1579 | 50.4% | 49.8-51.0% | 1634 | 50.3% | +0.15 pp |
| 8 | 1637 | 50.8% | 50.1-51.4% | 1727 | 50.5% | +0.22 pp |
| 9 | 1711 | 51.2% | 50.5-51.8% | 1852 | 50.8% | +0.36 pp |
| 10 | 1849 | 52.0% | 51.1-52.8% | 2089 | 51.4% | +0.60 pp |
top 1% skill win rate 53.0%, bottom 1% 47.0%; sd of individual win rates 1.23 pp; stationary sd(R-s) 138.0; residual sd around fitted line 109.8; RMSE<=2x stationary after 1 games, <=1.1x after 89 games; slope(R on s) 1.690 [t=250: 0.59, t=500: 0.85, t=1000: 1.14, t=2000: 1.47, t=3000: 1.69], corr 0.951; 100-game-window win-rate variance / binomial = 0.91; share of 100-game windows >=60%: 2.4%, <=40%: 2.4%  [2s]

## Summary table (rating error, convergence, decile extremes)
| scenario | sd(R - s) | resid sd (fitted line) | slope R~s | corr(R,s) | games to RMSE<=2x stat. | to <=1.1x | top-decile win | bottom-decile win | 100-game var / binomial |
|---|---|---|---|---|---|---|---|---|---|
| 1v1 random K=16 | 38.2 | 38.1 | 1.021 | 0.983 | 90 | 236 | 82.9% | 16.8% | 1.00 |
| 1v1 SBMM K=16 | 55.2 | 41.3 | 1.196 | 0.986 | 55 | 153 | 57.9% | 42.2% | 0.56 |
| 1v1 strict-SBMM(jitter20) K=16 | 152.9 | 54.6 | 2.108 | 0.992 | 1 | 14 | 51.2% | 48.8% | 0.59 |
| 5v5 random sum-model K=16 | 58.5 | 58.4 | 1.045 | 0.962 | 101 | 324 | 65.0% | 34.8% | 1.00 |
| 5v5 SBMM sum-model K=16 | 95.1 | 68.3 | 1.456 | 0.974 | 9 | 144 | 53.4% | 46.6% | 0.79 |
| FFA8 random K=16 | 22.8 | 22.8 | 1.005 | 0.994 | 151 | 334 | 40.2% | 1.4% | 1.00 |
| FFA8 SBMM K=16 | 28.4 | 24.7 | 1.071 | 0.993 | 163 | 323 | 16.9% | 8.9% | 0.86 |
| 1v1 random +form-noise150 K=16 | 53.6 | 38.1 | 0.810 | 0.973 | 65 | 267 | 79.5% | 20.7% | 1.00 |
| 1v1 SBMM +form-noise150 K=16 | 43.4 | 41.0 | 0.931 | 0.977 | 122 | 519 | 59.0% | 40.9% | 0.57 |
| 1v1 random +AR1 form sd100 phi0.99 K=16 | 74.5 | 82.8 | 0.966 | 0.919 | 14 | 118 | 81.3% | 18.7% | 3.70 |
| 1v1 SBMM +AR1 form sd100 phi0.99 K=16 | 77.9 | 100.1 | 1.131 | 0.915 | 1 | 72 | 57.2% | 42.8% | 1.64 |
| 1v1 random K=32 | 55.1 | 54.4 | 1.037 | 0.967 | 25 | 82 | 83.1% | 17.4% | 1.00 |
| 1v1 SBMM K=32 | 117.3 | 66.2 | 1.496 | 0.976 | 1 | 19 | 56.4% | 43.5% | 0.42 |
| 1v1 strict-SBMM(jitter20) K=32 | 481.6 | 109.2 | 4.176 | 0.991 | 1 | 1 | 51.1% | 48.9% | 0.58 |
| 5v5 random sum-model K=32 | 87.4 | 84.3 | 1.085 | 0.933 | 14 | 114 | 65.3% | 34.7% | 1.00 |
| 5v5 SBMM sum-model K=32 | 278.4 | 133.4 | 2.568 | 0.968 | 1 | 1 | 52.4% | 47.6% | 0.74 |
| FFA8 random K=32 | 32.5 | 32.3 | 1.012 | 0.987 | 54 | 133 | 39.8% | 1.4% | 1.00 |
| FFA8 SBMM K=32 | 48.2 | 36.6 | 1.157 | 0.988 | 35 | 89 | 16.6% | 9.1% | 0.81 |
| 1v1 random +form-noise150 K=32 | 64.7 | 54.4 | 0.832 | 0.950 | 22 | 117 | 79.3% | 20.5% | 1.00 |
| 1v1 SBMM +form-noise150 K=32 | 74.1 | 65.7 | 1.174 | 0.963 | 15 | 73 | 57.6% | 42.4% | 0.43 |
| 1v1 random +AR1 form sd100 phi0.99 K=32 | 74.9 | 100.5 | 0.999 | 0.895 | 1 | 38 | 81.7% | 18.7% | 3.66 |
| 1v1 SBMM +AR1 form sd100 phi0.99 K=32 | 125.8 | 141.1 | 1.445 | 0.899 | 1 | 4 | 55.7% | 44.2% | 1.07 |
| 5v5 random mean-model K=16 | 85.1 | 85.0 | 1.022 | 0.922 | 48 | 359 | 59.0% | 41.1% | 1.00 |
| 5v5 SBMM mean-model K=16 | 138.0 | 109.8 | 1.690 | 0.951 | 1 | 89 | 52.0% | 48.0% | 0.91 |

## Scale identifiability under SBMM: slope of R on s (and residual sd) vs queue jitter, 1v1
| K | queue jitter sd | t=250 | t=500 | t=1000 | t=2000 | t=3000 |
|---|---|---|---|---|---|---|
| 16 | 0 | 0.59 (42) | 0.83 (65) | 1.15 (102) | 1.59 (159) | 1.94 (200) |
| 16 | 20 | 0.68 (32) | 0.93 (37) | 1.27 (43) | 1.74 (49) | 2.09 (54) |
| 16 | 50 | 0.80 (34) | 1.01 (38) | 1.26 (43) | 1.53 (47) | 1.69 (49) |
| 16 | 100 | 0.88 (35) | 1.04 (39) | 1.14 (40) | 1.19 (41) | 1.19 (41) |
| 16 | 200 | 0.91 (36) | 1.02 (38) | 1.06 (39) | 1.06 (39) | 1.06 (39) |
| 32 | 0 | 1.18 (86) | 1.65 (135) | 2.28 (214) | 3.17 (325) | 3.87 (401) |
| 32 | 20 | 1.23 (60) | 1.72 (71) | 2.42 (84) | 3.39 (97) | 4.14 (109) |
| 32 | 50 | 1.22 (60) | 1.61 (68) | 2.10 (78) | 2.74 (88) | 3.20 (96) |
| 32 | 100 | 1.16 (59) | 1.33 (62) | 1.45 (65) | 1.50 (66) | 1.50 (66) |
| 32 | 200 | 1.07 (56) | 1.12 (57) | 1.13 (57) | 1.13 (57) | 1.13 (57) |
theory for perfectly tight SBMM (own derivation): slope(t) ~ sqrt(1 + K^2 t / (4 sd_skill^2))

## Form drift (tilt/fatigue) details under SBMM: AR(1) u, sd 100, phi 0.99 (corr. time ~100 games)
| K | outcome autocorr lag1 | lag5 | lag20 | win rate when u>+1sd | when u<-1sd | sd(rating-implied - current skill) | share of u absorbed by rating |
|---|---|---|---|---|---|---|---|
| 16 | 0.015 | 0.013 | 0.008 | 58.8% | 41.0% | 69.6 | 0.64 |
| 32 | 0.004 | 0.005 | 0.001 | 56.9% | 42.9% | 67.4 | 0.75 |

## Improvement: random 10% of players gain +300 skill linearly over 600 games (0.5 pt/game), SBMM 1v1
| K | win rate first 100 games | win rate W games 100-600 | mean expected score E games 100-600 | W - E | theory lambda*v/K | lag (skill pts) games 100-600 | theory lambda*v/(Kc) | lambda (scale) | W 200 games after stop | E after stop |
|---|---|---|---|---|---|---|---|---|---|---|
| 16 | 51.9% | 55.8% | 52.7% | +3.06 pp | +3.60 pp | 26.8 | 25.0 | 1.15 | 55.9% | 55.0% |
| 32 | 51.6% | 54.3% | 52.4% | +1.95 pp | +2.27 pp | 18.4 | 15.7 | 1.45 | 54.5% | 54.1% |

## Newcomer / reset: 500 top-decile players (mean skill ~1850) reset to 1500 after equilibrium, 1v1
| matchmaking | K | initial gap (skill pts) | games to close 50% | games to close 90% | linear-theory tau=1/(Kc) | win rate first 50 | first 100 | games 300-400 |
|---|---|---|---|---|---|---|---|---|
| sbmm | 16 | 349 | 52 | 282 | 43 | 77.5% | 72.8% | 59.2% |
| sbmm | 32 | 349 | 33 | 195 | 22 | 73.8% | 68.1% | 57.3% |
| random | 16 | 349 | 57 | 269 | 43 | 82.8% | 82.8% | 83.2% |
| random | 32 | 349 | 29 | 143 | 22 | 82.8% | 82.8% | 83.2% |

