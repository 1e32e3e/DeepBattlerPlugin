# 第二章待核对来源

第二章（`paper/chapters/ch2.tex`，研究二）中未能读到全文的来源。正文对应位置有 `\needcheck` 脚注。整合时并入 `docs/TO_VERIFY.md`。

| 章节 | 来源键名 | 需要核对的说法 | 原因 |
|---|---|---|---|
| 2.1.1 | `thurstone1927law` | 正态表现噪声的成对比较模型（Thurstone Case V），$G(x)=\Phi(x/(\sqrt2\beta))$ | 只核对了 Crossref 书目信息；APA PsycNet 付费墙。模型形式依据 `herbrich2006trueskill` 原文（“Gaussian variant corresponding to the Thurstone Case V model”）和 `weng2011bayesian` 的转述 |
| 2.1.1 | `bradley1952rank` | 逻辑斯蒂成对比较模型（Bradley–Terry），即 Elo 的逻辑斯蒂变体 | 只核对了 Crossref 书目信息；JSTOR 付费墙。模型形式依据 `herbrich2006trueskill`、`weng2011bayesian`、`oleskertaylor2024analysis` 的转述 |
| 2.7 | `brown2001interval` | 小样本二项比例的区间应使用 Wilson（或 Jeffreys）区间而不是 Wald 区间 | 只核对了 Crossref 书目信息；Project Euclid 页面拒绝访问（403），未读到摘要和正文 |
| 2.7 | `wilson1927probable` | Wilson 区间的出处 | 只核对了 Crossref 书目信息；Taylor & Francis 付费墙。区间公式本身由本项目在 `code/ch2/fig_ci.py` 中按标准形式计算 |

## 已读全文或原页面（本章引用，供整合时参考）

| 来源键名 | 读到的版本 |
|---|---|
| `elo1978rating` | 1986 年第 2 版扫描本（gwern.net），引用了 1.24–1.27 节与 8.94 节 |
| `herbrich2006trueskill` | MSR 托管的 NIPS 2006 论文 PDF |
| `minka2018trueskill` | MSR-TR-2018-8 PDF |
| `aldous2017elo` | 作者主页的预印本（2017-03-22），与 Statistical Science 正式版标题、结论一致；页码取自 Crossref |
| `oleskertaylor2024analysis` | arXiv:2406.05869v1；NeurIPS 2024 页码与 DOI 取自 proceedings.neurips.cc 元数据 |
| `cortez2024convergence` | arXiv:2410.09180v2（2026-01-26），定理 2 的 $\sqrt K$ 收敛率 |
| `jabin2015continuous` | 作者预印本（2014-05-16）；期刊信息取自 Crossref |
| `during2019boltzmann` | arXiv:1806.06648v2 摘要与引言；期刊信息取自 Crossref |
| `balduzzi2018reevaluating` | arXiv:1806.02643v2（NIPS 2018 final version） |
| `weng2011bayesian` | JMLR PDF |
| `bowling2009logistic` | JIEM 开放获取 PDF（1.702 的最大偏差 0.0095） |
| `blizzard2019developer`、`blizzard2020developer` | 炉石传说官网原文（2019-11-27、2020-09-28） |
| `blizzard2022overwatch`、`blizzard2023overwatch` | 守望先锋官网原文（2022-12-20、2023-01-30） |

## 未引用但曾尝试的来源

- Riot 2018 “/dev: Matchmaking Real Talk”（"50 +/- 1%"）：原链接已重定向到首页，Wayback Machine 连接被重置，未能核对，故本章不引用（属第一章厂商披露范围）。
- Glickman (1999) JRSS-C 与 glicko.net 上的指南：glicko.net 域名无法解析，本章未引用。
