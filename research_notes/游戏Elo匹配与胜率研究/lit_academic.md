# 学术文献图谱：通用 Elo 家族评分系统（rating）与匹配机制（matchmaking）研究（Part 1/4）

> 范围：通用的评分与匹配机制学术文献，不含公司博客和专利（另有研究员负责）。截至 2026-10。
> **来源类型标记**：[PR]=同行评审（期刊或会议）；[TR]=技术报告（未经同行评审）；[PP]=预印本（arXiv 等）；[TH]=学位论文或学生报告；[INF]=非正式来源（维基、博客、新闻、论坛）。
> **核验程度标记**：(全文核验)=本次会话读过 PDF 全文；(摘要核验)=只通过检索摘要、出版社摘要页或二手描述核实；(未核验)=引自研究者已有知识，给了 DOI/URL，但本次会话没能打开原文（arxiv.org、glicko.net、jmlr.org、papers.nips.cc 等域名在本环境的抓取工具中 DNS 解析失败或被代理拒绝）。报告撰写者引用"未核验"条目时请保守措辞。
> **术语对照**：等级分/埃洛等级分 = Elo rating；期望得分 = expected score；K 值/K 因子 = K-factor；成对比较 = paired comparison；评分偏差 = rating deviation (RD)；波动率 = volatility；隐藏分 = MMR (matchmaking rating)；匹配质量 = match quality；平局边际 = draw margin；因子图/消息传递 = factor graph / message passing；非传递性（克制环）= non-transitivity；流失 = churn；留存 = retention；连胜/连败 = win/loss streak；排队时间 = queue time；组排/开黑车队 = squad/party；单排 = solo queue；冷启动 = cold start；定级赛 = placement matches；分数膨胀/通缩 = rating inflation/deflation；天梯 = ladder；段位 = tier/rank；大逃杀 = battle royale；自由混战 = free-for-all (FFA)；参与度优化匹配 = engagement-optimized matchmaking (EOMM)。

---

## Q1 基础：Thurstone/Mosteller、Bradley–Terry 与 Elo（1978）的概率假设和更新规则

### Takeaway
Elo 本质上是"成对比较模型"的一个在线、线性化估计器。正态（Gaussian）版本对应 Thurstone Case V，Logistic 版本对应 Bradley–Terry。400 只是一个标度常数：在 Logistic 公式下，400 分差意味着 10:1 的期望得分比，约 91%。更新规则是 R' = R + K(S − E)，K 是固定学习率，模型本身不表示"对该玩家实力有多不确定"。

### Cited Findings
- **Thurstone (1927), "A law of comparative judgment"**，*Psychological Review* 34(4):273–286 [PR](未核验)。提出成对比较的"判别过程"服从正态分布。Case V 假设各对象方差相等且互不相关，于是 P(i 胜 j) = Φ((μi − μj)/σ√2)。— [DOI 10.1037/h0070288](https://doi.org/10.1037/h0070288)
- **Mosteller (1951), "Remarks on the method of paired comparisons"**，*Psychometrika* 16:3–9 [PR](未核验)。给出 Case V 尺度值的估计方法，这就是后来所说的 "Thurstone–Mosteller 模型"。— [DOI 10.1007/BF02313422](https://doi.org/10.1007/BF02313422)
- **Zermelo (1929)**，*Mathematische Zeitschrift* 29:436–460 [PR](未核验)。为国际象棋循环赛提出了与 Bradley–Terry 等价的模型，比 BT 早 23 年。— [DOI 10.1007/BF01180541](https://doi.org/10.1007/BF01180541)
- **Bradley & Terry (1952), "Rank analysis of incomplete block designs: I. The method of paired comparisons"**，*Biometrika* 39(3/4):324–345 [PR](未核验)。P(i 胜 j) = πi/(πi+πj)。令 πi = exp(θi)，就变成 θi − θj 的 logistic 函数。— [DOI 10.2307/2334029](https://doi.org/10.2307/2334029)
- **Elo 与 Thurstone/BT 的统计对应关系（原文明确写出）**："From the point of view of statistics the Elo system addresses the problem of estimating from paired comparison data with the Gaussian variant corresponding to the Thurstone Case V model and the logistic variant to the Bradley-Terry model." 同文还说 "Most currently used Elo variants use a logistic distribution instead of a Gaussian because it is argued to provide a better fit for Chess data." — [Herbrich, Minka & Graepel, TrueSkill, NIPS 2006](https://www.microsoft.com/en-us/research/wp-content/uploads/2007/01/NIPS2006_0688.pdf) [PR](全文核验)
- **Elo 的历史与基本设定**：Elo 1959 年为国际象棋设计了这套系统，FIDE 于 1970 年采用。在 Gaussian 设定下，每位玩家的表现 pi ~ N(si, β²)，P(p1>p2) = Φ((s1−s2)/(√2β))。线性化更新为 s1 ← s1 + yΔ、s2 ← s2 − yΔ（y=+1/−1/0 分别对应胜/负/平），其中 Δ = αβ√π·((y+1)/2 − Φ((s1−s2)/(√2β)))，"αβ√π" 这一项就是 K 因子。文中还说 Elo 中 "a player's rating is regarded as provisional as long as it is based on less than a fixed number of, say, 20 games"（定级/临时分问题）。— [TrueSkill NIPS 2006](https://www.microsoft.com/en-us/research/wp-content/uploads/2007/01/NIPS2006_0688.pdf) [PR](全文核验)
- **K 的典型取值**：TrueSkill 论文的对照实验用 Gaussian Elo，α = 0.07，"this corresponds to a K factor of 24 on the Elo scale which is considered a good and stable dynamics"。— [TrueSkill NIPS 2006](https://www.microsoft.com/en-us/research/wp-content/uploads/2007/01/NIPS2006_0688.pdf) [PR](全文核验)
- **Elo 原书**：Arpad E. Elo, *The Rating of Chessplayers, Past and Present*, Arco, 1978（第二版 1986；Ishi Press 2008 重印），ISBN 0-668-04721-6 [书籍](未核验原书)。— [Wikipedia 条目引用信息](https://en.wikipedia.org/wiki/Elo_rating_system) [INF]
- **原始正态假设与 200/400 标度**：Elo 假设棋手的表现服从正态分布，均值等于真实实力，并把标准差校准为"200 分差 ≈ 3:1 期望得分比"。400 分是"校准差"，在该分差下强者的期望得分比为 10:1（约 91%）。— [ChessBase India, "The origin and accuracy of Elo rating"](https://chessbase.in/news/the-origin-and-accuracy-of-elo-rating) [INF]
- **差值方差**：个人表现的 σ 定为 200，两人表现之差的 σ' = 200√2 ≈ 282.84。— [Wikipedia: Elo rating system](https://en.wikipedia.org/wiki/Elo_rating_system) [INF]
- **Logistic 公式与更新式**：E_A = 1/(1 + 10^((R_B − R_A)/400))，R'_A = R_A + K(S_A − E_A)，S 取 1/0.5/0。USCF 和多数网站改用 logistic，理由是实际数据中弱者赢的概率比正态模型预测的高（尾部更厚）。FIDE 仍沿用 Elo 按均值 0、σ=200 计算的正态差值表。— [Wikipedia: Elo rating system](https://en.wikipedia.org/wiki/Elo_rating_system) [INF]；[Chess.com 博客 "Elo Ratings – Part 1"](https://www.chess.com/blog/RISHIVIJAYANCHES/elo-ratings-part-1) [INF，作者自己标注部分说法需引证]
- **FIDE 现行 K 值**：新棋手前 30 局，以及 18 岁以下且等级分 < 2300 的棋手，K=40；等级分 < 2400 时 K=20；一旦达到 2400，K=10。FIDE 另有"400 分规则"，计算时分差超过 400 一律按 400 计。— [FIDE Handbook, Rating Regulations (B.02)](https://handbook.fide.com/chapter/B022017) [规章](未核验；本次会话未能打开，数值来自已有知识，引用前需核对最新版本)
- **Glickman 的综述**："A Comprehensive Guide to Chess Ratings"（*American Chess Journal* 3, 1995）系统讨论了 Elo 的正态/Logistic 假设、K 值、临时分（provisional rating），以及通胀和通缩。— [glicko.net/research/acjpaper.pdf](http://www.glicko.net/research/acjpaper.pdf) [PR/综述](未核验，域名不可达)
- **Aldous (2017)**，"Elo ratings and the sports model: a neglected topic in applied probability?"，*Statistical Science* 32(4):616–629 [PR](未核验)。从应用概率角度分析 Elo 作为随机过程的性质，例如在实力固定时评分的平稳分布与抖动。— [DOI 10.1214/17-STS628](https://doi.org/10.1214/17-STS628)

### Inferences
- **Elo 的隐含假设清单**（据以上各源整理）：(1) 每位玩家只有一个标量实力；(2) 单局表现 = 实力 + 独立同分布噪声，且所有玩家的噪声方差相同；(3) 实力关系是传递的（A>B、B>C 推出 A>C）；(4) 平局记 0.5，模型本身不单独刻画平局率；(5) 不表示估计的不确定性，K 固定；(6) 双方 K 相同时为零和更新，封闭池中总分守恒，这是通胀/通缩讨论的根源。
- **Elo 更新 = 对 BT 对数似然做一步随机梯度上升**：对 logistic BT 求导，∂log L/∂R_A = (ln10/400)·(S − E)，所以 K 相当于学习率乘一个常数。这说明 K 值的取舍本质上是"偏差–方差"或"跟踪速度–稳态抖动"的权衡（这是数学推导，不是文献原话）。
- **对第 2 部分（胜率推导）的意义**：在 Elo/BT 框架下，如果匹配器总是找"期望得分 ≈ 0.5"的对手，那么不论玩家水平高低，长期胜率都会被推向约 50%。胜率反映的是"匹配后的相对强弱"，不是绝对实力。

### Gaps
- 本次没能读到 Elo 1978 原书，书中关于 K 值的具体建议（如按棋手级别分 K=10/16/32 等）以及"class = 200 分"的原始表述未经原文核实。
- Glickman 1995 综述（glicko.net）和 FIDE 手册没能直接打开，FIDE 2024 年前后针对低分段通缩的一次性调整等最新规章未核验。

---

## Q2 后继与扩展模型：各自修正了什么问题、团队实力如何聚合

### Takeaway
Elo 之后的主线是：①引入不确定性（Glicko 的 RD → Glicko-2 的波动率）；②支持团队、多队和平局（TrueSkill 用因子图加期望传播，Weng–Lin/OpenSkill 用解析近似）；③全历史平滑（TrueSkill Through Time、WHR、Edo）；④大规模多人排名（Plackett–Luce、Elo-MMR）；⑤非传递性（mElo）；⑥利用胜负以外的信息（TrueSkill 2 用击杀/死亡、退出、组排、经验）。团队实力几乎都默认取**成员表现之和**（TrueSkill 按上场时长加权求和），但实证显示"求和"假设对车队（squad）系统性低估，而且 MAX 聚合常常预测更准。

### Cited Findings

#### 模型速查表
（下表各行的出处见本节后续条目。）

| 模型（年份/出处） | 表现分布 | 不确定性 | 多人/多队 | 平局 | 团队聚合 | 主要修正点 |
|---|---|---|---|---|---|---|
| Elo (1959/1978) | 正态（原始）/ Logistic（USCF 等） | 无（固定 K） | 原生仅 1v1；团队赛常用"对决启发式"（duelling heuristic）或队均分 | 记 0.5 | 无原生定义 | — |
| Glicko (Glickman 1999, JRSS-C) | Logistic/BT 动态模型 | RD（评分偏差），不活跃时 RD 增大 | 1v1 | 0.5 | 无 | 不确定性、评分周期 |
| Glicko-2 (Glickman 2001, J. Appl. Stat.) | 同上 | RD + 波动率 σ | 1v1 | 0.5 | 无 | 实力突变/波动 |
| TrueSkill (Herbrich+ NIPS 2006) | 正态 N(s, β²) | N(μ, σ²) | 任意队数、任意人数 | 显式平局边际 ε | **成员表现之和**（加权） | 团队、多队、平局、收敛速度 |
| TrueSkill Through Time (NIPS 2007) | 正态 | 全历史平滑 | 是 | 是 | 和 | 历史可比性 |
| WHR (Coulom 2008) | 动态 BT | 全历史 MAP + Hessian 方差 | 1v1（可含让子） | — | — | 用全部历史回溯修正 |
| Weng–Lin (JMLR 2011) / OpenSkill | BT / Thurstone–Mosteller / Plackett–Luce | N(μ, σ²) | 是 | 部分模型支持 | 成员 μ 与 σ² 求和 | 解析更新、更快 |
| Elo-MMR (WWW 2021) | Logistic 类（对极端表现稳健） | 有 | 大规模个人排名 | 支持并列 | 无（个人赛） | 大规模多人、激励相容 |
| mElo (Balduzzi+ NeurIPS 2018) | BT + 循环分量 | 无 | 1v1 | — | — | 非传递性 |
| TrueSkill 2 (MSR-TR 2018) | 正态 + 个人统计似然 | 有 | 是 | 是 | 加权和 + **车队偏移**（squad offset） | 个人数据、退出、经验、跨模式、车队 |

#### Glicko / Glicko-2
- **Glickman (1999), "Parameter estimation in large dynamic paired comparison experiments"**，*JRSS Series C (Applied Statistics)* 48(3):377–394 [PR](摘要核验)。把实力随时间变化的成对比较数据建模为非线性状态空间模型，给出计算简单、非迭代的近似拟合算法。"improves over the commonly used algorithm of Elo by incorporating the variability in parameter estimates"，并应用于国际象棋和网球。— [IDEAS/RePEc 摘要页](https://ideas.repec.org/a/bla/jorssc/v48y1999i3p377-394.html)；[DOI 10.1111/1467-9876.00159](https://doi.org/10.1111/1467-9876.00159)
- **Glicko 的机制细节**（未核验）：每位玩家有 (r, RD)，按"评分周期"批量更新；不活跃时 RD 按常数 c 增大；单局变动幅度随自身 RD² 增大、随对手 RD 增大而减小。— [glicko.net/glicko/glicko.pdf](http://www.glicko.net/glicko/glicko.pdf) [TR](未核验)
- **Glicko-2 (Glickman 2001)**，"Dynamic paired comparison models with stochastic variances"，*Journal of Applied Statistics* 28(6):673–689 [PR](DOI 摘要核验)。新增波动率 σ，玩家表现偏离预期的周期里 RD 会相应增减。σ 用 Illinois 算法迭代估计。— [DOI 10.1080/02664760120059219](https://doi.org/10.1080/02664760120059219)；机制描述见 [EDM 2021 论文对 Glicko-2 的转述](https://educationaldatamining.org/EDM2021/virtual/static/pdf/EDM21_paper_8.pdf) [PR]；算法说明 [glicko.net/glicko/glicko2.pdf](http://www.glicko.net/glicko/glicko2.pdf)（未核验：系统常数 τ、内部标度 173.7178 等细节）
- **Glicko-boost**：Glickman 参加 Deloitte/FIDE 比赛时提交的版本。当某月表现异常时"boost"（调高）该玩家月初的 RD 再重新计算，并用对手更新后的评分做第二次更新。— [glicko.net/glicko/glicko-boost.pdf](https://www.glicko.net/glicko/glicko-boost.pdf) [TR](摘要核验)

#### TrueSkill 家族（Microsoft Research）
- **TrueSkill (Herbrich, Minka, Graepel, NIPS 2006)** [PR](全文核验)：
  - 每位玩家有因子化的高斯先验 N(μi, σi²)。表现 pi ~ N(si, β²)。"The performance tj of team j is modeled as the sum of the performances of its players"（团队表现 = 成员表现之和）。比赛排名由团队表现的大小顺序生成：胜要求 t_r(j) > t_r(j+1) + ε，平局要求 |差| ≤ ε，ε 由实际观察到的平局概率反推。推断方法是在因子图上做近似消息传递（期望传播，EP）。
  - 文中承认"平局"这个关系在该模型下不满足传递性。
  - Xbox Live 参数：μ0 = 25，σ0 = 25/3，β = σ0/2，动态方差 τ = σ0/100。排行榜显示保守估计 μ − 3σ（1% 下分位数）。匹配准则（match quality）是"draw probability relative to the highest possible draw probability in the limit ε → 0"。
  - 处理 Elo 的团队赛时用 "duelling heuristic"：每个玩家与所有其他玩家两两比较，取各次更新量的平均。
  - 线上规模："processes hundreds of thousands of games per day"（Xbox 360 Live）。
  - 出处：[TrueSkill NIPS 2006 PDF（MSR 镜像）](https://www.microsoft.com/en-us/research/wp-content/uploads/2007/01/NIPS2006_0688.pdf)；[NeurIPS 论文集页面](https://papers.nips.cc/paper_files/paper/2006/file/f44ee263952e65b3610b8ba51229d1f9-Paper.pdf)。注意卷号存在出入：MSR 页面写 *Advances in NIPS 20*，Herbrich 个人主页等列为 NIPS 19, pp. 569–576（见 [MSR 出版物页](https://www.microsoft.com/en-us/research/publication/trueskilltm-a-bayesian-skill-rating-system/)、[HPI Herbrich 出版物 2006](https://hpi.de/herbrich/publications/2006.html)）。
- **TrueSkill Through Time (Dangauthier, Herbrich, Minka, Graepel, NIPS 2007, pp. 931–938)** [PR](摘要核验)：把各时期的实力串联起来做全历史平滑（smoothing），可以跨世纪比较国际象棋棋手。— [Herbrich: Computer Gaming 页](https://herbrich.me/computer-gaming/)
- **TrueSkill 2 (Minka, Cleven, Zaykov, 2018)**，Microsoft Research 技术报告 [TR，**非同行评审**](全文核验)：
  - 经典 TrueSkill 的 5 条假设：表现是实力的噪声样本；团队表现 = 按上场时长加权的表现之和；只用胜负/平局，不用比分；实力做无偏随机游走；各模式的实力相互独立。
  - TrueSkill 2 的 5 处修改：①用击杀/死亡等个人统计推断实力；②中途退出按投降处理，无论实际结果如何都按输更新；③各模式实力相关，进入新模式时借用其他模式的评分；④随机游走偏向上升，新手前几局偏得更多；⑤组队（squad）时表现高于平时。
  - 设计约束：评分须为单一数字，以兼容既有匹配器；"aligned incentives"，即不能让玩家为刷分而损害队友（比如只奖励击杀会诱发不合作行为）；计算成本低；参数可从批量数据自动估计。
  - 出处：[trueskill2.pdf（MSR）](https://www.microsoft.com/en-us/research/uploads/prod/2018/03/trueskill2.pdf)
- **团队聚合的实证问题（TrueSkill 2 车队表，Halo 5 测试集）**：玩家按所在车队人数分组，"实际胜率 vs. 经典 TrueSkill 按求和假设得出的预期胜率"为：1 人 47 vs 47；2 人 50 vs 50；3 人 50 vs 50；4 人 57 vs 52；5 人 53 vs 49；6 人 56 vs 48；7 人 62 vs 49；8 人 68 vs 49；9 人 70 vs 54；≥10 人 89 vs 67。作者结论："the assumption about squads is false. The skill rating of a squad should be larger than the sum of its players, and the effect grows with the size of the squad"；Halo 5 和 Gears of War 4 的部分模式因此禁止大车队，但这会缩小匹配池。— [TrueSkill 2](https://www.microsoft.com/en-us/research/uploads/prod/2018/03/trueskill2.pdf) [TR](全文核验)

#### Weng–Lin 贝叶斯近似与 OpenSkill
- **Weng & Lin (2011), "A Bayesian Approximation Method for Online Ranking"**，*JMLR* 12:267–300 [PR](摘要核验)。面向多队、多人的在线排名，覆盖 Bradley–Terry、Thurstone–Mosteller、Plackett–Luce 三类模型。更新式是解析形式，不需要数值积分。"accuracy … competitive with state of the art systems such as TrueSkill, but the running time as well as the code is much shorter"。— [JMLR 页面](https://www.jmlr.org/beta/papers/v12/weng11a.html)；[PDF 镜像](https://jmlr2020.csail.mit.edu/papers/volume12/weng11a/weng11a.pdf)
- **OpenSkill (Joshy, 2024, arXiv 2401.05451)** [PP](摘要核验)：Weng–Lin 方法的开源实现，支持非对称多队。在作者自选的一个数据集上，Plackett–Luce 变体准确率 87.56%（556 对、79 错），TrueSkill 为 92.44%（587 对、48 错）；耗时 0.97 s 对 3.41 s。作者自己说速度差异可能部分来自所用 TrueSkill 实现的效率。注意：在这个数据集上 TrueSkill **更准**。— [arXiv 2401.05451](https://arxiv.org/pdf/2401.05451)；Plackett–Luce 实现注明是 "Algorithm 4 by Weng and Lin [2011]"，见 [openskill.py 文档](https://openskillpy.readthedocs.io/en/latest/api/openskill/models/weng_lin/plackett_luce/index.html) [INF/文档]

#### 全历史评分：WHR、Edo
- **Coulom (2008), "Whole-History Rating: A Bayesian Rating System for Players of Time-Varying Strength"**，Computers and Games 2008（LNCS 5131）[PR](摘要核验)。基于动态 Bradley–Terry 模型，"directly computes the exact maximum a posteriori over the whole rating history of all players"，不做增量近似。"in comparison to Elo, Glicko, TrueSkill, and decayed-history algorithms, WHR produces better predictions"。计算成本更高，但作者称仍足以用于实时服务器。— [WHR.pdf](https://www.remi-coulom.fr/WHR/WHR.pdf)；[WHR 主页](https://remi-coulom.fr/WHR/)
- **Edo（Rod Edwards，历史国际象棋评分）**[INF/个人项目](未核验)：基于 Bradley–Terry，把同一棋手的不同年份视为不同实体，用虚拟对局把相邻年份连起来，事后回溯估计历史实力。— [edochess.ca](http://www.edochess.ca/)

#### 多人自由混战与 Plackett–Luce、Elo-MMR
- **Plackett–Luce 模型**：Luce (1959) 的选择公理加 Plackett (1975) 的排名模型。名次序列 π 的概率 = ∏_i exp(θ_π(i)) / Σ_{j≥i} exp(θ_π(j))，可以理解为"逐个选出第一名"。— [Plackett 1975, JRSS-C 24(2):193–202, DOI 10.2307/2346567](https://doi.org/10.2307/2346567) [PR](未核验)；贝叶斯推断见 Guiver & Snelson, ICML 2009 [PR](未核验)，[DOI 10.1145/1553374.1553423](https://doi.org/10.1145/1553374.1553423)
- **TrueSkill 对 8 人 FFA 的处理**：把名次视为 k 个"队"的表现排序，因子图只连接相邻名次（k−1 个比较因子）。论文在 Halo 2 的 8 人 FFA 上做了实验（见 Q4）。— [TrueSkill NIPS 2006](https://www.microsoft.com/en-us/research/wp-content/uploads/2007/01/NIPS2006_0688.pdf) [PR](全文核验)
- **Elo-MMR (Ebtekar & Liu, WWW 2021, pp. 1772–1784)** [PR](摘要核验)：面向大规模多人、名次离散的比赛（编程竞赛、障碍赛、部分电子游戏）。证明了激励相容（想提高评分的玩家没有理由故意表现差）、对极端表现稳健、渐近快速、可高度并行，并称是首个在多于两名个体排名的场景下严格证明这些性质的系统。预测精度与现有系统相当或更好，速度最多快一个数量级。DMOJ 于 2021 年 8 月迁移到该系统。— [DOI 10.1145/3442381.3450091](https://doi.org/10.1145/3442381.3450091)；[arXiv 2101.00400](https://arxiv.org/pdf/2101.00400)；[WWW'21 文集条目](https://ir.webis.de/anthology/2021.wwwconf_conference-2021.156)；[DMOJ 迁移公告](https://dmoj.ca/post/206-ratings-migrated-to-elo-mmr) [INF]
- **含运气成分的多人游戏**：针对 Skat 等游戏的 Elo 改造。— [arXiv 2104.05422](https://arxiv.org/pdf/2104.05422) [PP](摘要核验)

#### 非传递性：mElo 及其后续
- **Balduzzi, Tuyls, Pérolat, Graepel (NeurIPS 2018), "Re-evaluating Evaluation"** [PR](摘要核验)：指出 Elo 的两个缺陷。①假设相对实力可传递，所以在石头剪刀布式的循环博弈中没有信息量；②可以通过加入大量"它能打赢的对手副本"来抬高某个体的评分。提出多维 Elo（mElo），把胜负矩阵分解为传递分量和循环分量（Hodge 分解思想），并配合 Nash averaging 评估。在 8 个 AlphaGo 变体及 Zen 上，mElo₂ 的胜率预测优于 Elo，并能识别 Elo 判错的三元非传递组合。— [arXiv 1806.02643](https://arxiv.org/pdf/1806.02643)；[ar5iv HTML](https://ar5iv.labs.arxiv.org/html/1806.02643)
- **Czarnecki et al. (NeurIPS 2020), "Real World Games Look Like Spinning Tops"** [PR](未核验)：真实博弈的策略空间呈"陀螺"形，中段循环（非传递）最强，顶端趋于传递。— [arXiv 2004.09468](https://arxiv.org/abs/2004.09468)
- **Bertrand, Czarnecki, Gidel (AISTATS 2023), "On the Limitations of the Elo: Real-World Games are Transitive, not Additive"** [PR](**未核验**，本次检索没找到，标题和作者凭记忆，引用前必须核对)。
- **2025 年预印本 arXiv 2502.10985**（作者未能从检索结果确认）[PP](摘要核验)：即使 BT 模型设定有误，Elo 在稀疏的真实数据上依然表现良好；在稠密数据中会被 mElo 等更复杂模型超越；并警告在任意匹配机制下，即使数据本身是传递的，Elo 也可能给不出一致的排序。— [arXiv 2502.10985](https://www.arxiv.org/pdf/2502.10985)

#### 团队聚合与"团队化学反应"
- **Dehpanah, Ghori, Gemmell, Mobasher, "Evaluating Team Skill Aggregation in Online Competitive Games"**（IEEE CoG 2021）[PR](摘要核验)：在 Elo、Glicko、TrueSkill 上比较常规聚合（SUM/AVG）与两种新方法（MAX、MIN），数据来自 3 个真实数据集，共 10 万+ 场大逃杀和对战。**MAX 在大多数情形下表现最好**，说明团队表现更接近其最强成员。— [arXiv 2106.11397](https://arxiv.org/pdf/2106.11397)
- **DeLong et al., "TeamSkill: Modeling Team Chemistry in Online Multi-player Games"**（PAKDD 2011，Halo 3 数据）[PR](摘要核验)：用子团队的历史实力刻画"默契"。Glicko 和 TrueSkill 加上这些方法后精度明显提升，尤其在势均力敌的对局中；Elo 不加反而更好（后续工作 "TeamSkill Evolved" 用了混合分类方案）。— [SMU 机构库](https://ink.library.smu.edu.sg/sis_research/1492)；[UMN 条目](https://experts.umn.edu/en/publications/teamskill-modeling-team-chemistry-in-online-multi-player-games/)

### Inferences
- **"求和"聚合的含义**：在 TrueSkill/Weng–Lin 的求和假设下，(高+低) 的队伍等价于 (中+中) 的队伍。MAX 聚合预测更准、车队实际胜率显著高于求和预期，这两个结果都说明求和假设会系统性低估"有一个大腿"或"有默契的车队"。如果游戏只按求和匹配，单排玩家对上车队时会处于系统性劣势。TrueSkill 2 用车队偏移修正了这一点。
- **团队赛中个人评分收敛更慢**：团队赛只观察到一个团队层面的胜负比特，平摊到个人的信息量随队伍人数增加而下降。所以团队游戏需要更多局才能区分个人（TrueSkill 2 加入击杀/死亡等个人统计，部分原因就在这里）。这是推论，没有直接的定量文献支持。
- **从"修什么问题"看谱系**：不确定性（Glicko）→ 团队、多人、平局（TrueSkill、Weng–Lin、PL、Elo-MMR）→ 时变实力与回溯（TTT、WHR、Edo）→ 非传递性（mElo）→ 多源行为数据（TrueSkill 2）。

### Gaps
- 没能读到 Weng–Lin 原文，5 个具体算法（BT full/partial pair、TM full/partial pair、PL）的细节和团队方差求和公式凭已有知识，未核验。
- 本次没有核对 WHR 原文的具体数据集（据记忆为 KGS 围棋服务器数据）和误差数字。
- Bertrand et al. 2023 没有检索到，"Additive vs Transitive" 的结论未核验。
- 没有检索 Menke & Martinez (2008) 的 BT-神经网络团队个体评分模型和 Alman & McKay (AAMAS 2017) 的团队匹配理论。

---

## Q3 关于"匹配机制本身"（而非评分）的学术研究：能否以及是否应该优化公平以外的目标

### Takeaway
学术界和游戏公司研究院至少有 4 条独立研究线在优化"参与度/留存"而非"公平"：Delalleau 2012（Ubisoft，预测乐趣）、EOMM 2017（EA，最小化流失）、EnMatch 2024（网易伏羲，k-vs-k）、Chen–Elmachtoub–Lei（Management Science，Lichess 数据）。它们都声称比纯技术匹配（SBMM）更好，但证据主要来自作者自有数据上的仿真或自家 A/B 测试，报告的效应量不大（例如 4–6% 参与度），也缺乏独立复现。连胜/连败对流失的实证效应在不同研究之间**并不一致**。另有一条理论线（带延迟的在线匹配，MPMD）专门形式化"等待时间 vs 匹配质量"的权衡。

### Cited Findings
- **TrueSkill 的匹配质量与公平性实验**：匹配质量准则 = 相对平局概率（见 Q2）。Halo 2 实验中，只保留匹配质量超过阈值的对局后，"with TrueSkill even players with very few games got mostly fair matches (with a winning probability within 35% to 65%)"。— [TrueSkill NIPS 2006](https://www.microsoft.com/en-us/research/wp-content/uploads/2007/01/NIPS2006_0688.pdf) [PR](全文核验)
- **Graepel & Herbrich, "Ranking and Matchmaking"**，*Game Developer Magazine*（2006）[INF/行业杂志]，介绍 TrueSkill 的排名与匹配实践。— [herbrich.me PDF](https://www.herbrich.me/papers/Game-Developer-Feature-Article-Graepel-Herbrich.pdf)
- **Delalleau, Contal, Thibodeau-Laufer, Chandias Ferrari, Bengio, Zhang (2012), "Beyond Skill Rating: Advanced Matchmaking in Ghost Recon Online"**，*IEEE TCIAIG* 4(3):167–177 [PR](仅二手描述核验)：训练神经网络，根据玩家历史统计预测其"乐趣"（enjoyment），用于改进匹配。据 EOMM 论文描述，乐趣的真值来自赛后直接询问玩家。EOMM 作者称它是少数直接以体验为目标的匹配研究之一。— DOI [10.1109/TCIAIG.2012.2188833](https://doi.org/10.1109/TCIAIG.2012.2188833)（DOI 未核验）；二手描述见 [EOMM arXiv 1702.06820](https://arxiv.org/pdf/1702.06820) 和 [QuickSkill arXiv 2208.07704](https://arxiv.org/pdf/2208.07704)
- **EOMM：Chen, Xue, Kolen, Aghdaie, Zaman, Sun, Seif El-Nasr (WWW 2017, pp. 1143–1150)** [PR](摘要核验)：
  - 观点："fairness-based matchmaking" 不一定最能留住玩家，应直接最大化总体参与度。并证明在一个简化假设下，同水平匹配是该框架的特例。
  - 框架包含三部分：技能模型、流失（churn）预测模型、最小权完美匹配。把等待池建成完全图，边权 = 两人对局后的流失风险之和。
  - 实验：基于 EA 一款热门 1v1 PvP 游戏的真实数据做仿真。对比随机匹配、技术匹配（SkillMM）和故意最差的匹配（WorstMM，作 sanity check）。等待池 100–500 人，各重复 10,000 轮，指标是"之后 8 小时内仍活跃的玩家数"，用 Welch t 检验。结论是 EOMM 留存显著更高。
  - 出处：[arXiv 1702.06820](https://arxiv.org/pdf/1702.06820)；[ADS 摘要](https://ui.adsabs.harvard.edu/abs/2017arXiv170206820C/abstract)；[WWW'17 文集条目](https://ir.webis.de/anthology/2017.wwwconf_conference-2017.118/)；DOI 10.1145/3038912.3052559（未核验）
  - 局限：只适用于 1v1（EnMatch 论文明确指出）。结论来自仿真，不是线上 A/B 测试。
- **EnMatch：Wang Kai 等 10 位作者（网易伏羲 AI Lab），AAAI 2024, 38(8):9098–9106** [PR](摘要核验)：把参与度导向匹配扩展到 k-vs-k 团队模式。两大难点：一是量化阵容组成与对抗关系对参与度的影响，二是带非线性目标的 NP-hard 组合优化。做法是用数据分析建立"赛前即可估计"的参与度模型，再把优化建模为强化学习/神经组合优化问题。称在两款游戏的真实数据和线上部署中都优于现有方法，并"尽量保持公平"。— [AAAI 页面](https://ojs.aaai.org/index.php/AAAI/article/view/28760)；[DOI 10.1609/aaai.v38i8.28760](https://doi.org/10.1609/aaai.v38i8.28760)；[mlanthology 条目](https://mlanthology.org/aaai/2024/wang2024aaai-enmatch)
- **Chen Mingliu（UT Dallas）、Adam N. Elmachtoub（Columbia）、Xiao Lei（HKU），"Matchmaking Strategies for Maximizing Player Engagement in Video Games"**，*Management Science*（DOI 10.1287/mnsc.2023.02957；2026 年前后正式刊出，2026 年 6 月有新闻稿）；会议版 ACM EC 2022；SSRN 2021 [PR](摘要与新闻核验)：
  - EC'22 版对最优策略的描述："matches as many low-skilled players who are not at risk of churning to high-skilled players who are one loss away from churning"，即让濒临流失的高手去赢不会流失的新手。
  - 发现：玩家多数为低水平时，"pay-to-win" 可以提升参与度；优化匹配策略可以大幅减少所需的机器人（bot）数量。
  - 新闻稿称，在 Lichess 的 540 万场对局上，优化策略比常规技术匹配提升参与度 4–6%（数字来自新闻报道，需以期刊原文为准）。
  - 出处：[INFORMS 期刊页](https://pubsonline.informs.org/doi/10.1287/mnsc.2023.02957)；[SSRN 3928966](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3928966)；[EC'22 PDF](https://dl.acm.org/doi/pdf/10.1145/3490486.3538314)；[TechXplore 新闻（2026-06）](https://techxplore.com/news/2026-06-smarter-matchmaking-equal-skill-millions.html) [INF]
- **Yuksel (2024), "Skill-Based Matchmaking for Competitive Two-Player Games"**，*Proc. ACM Comput. Graph. Interact. Tech.*（I3D 2024），DOI 10.1145/3651303 [PR](摘要核验)：提出一种以"目标胜率"为每位玩家匹配的简单算法，使长连胜和长连败更难出现；另提出只依赖胜负结果的评分估计器。作者称它针对 Elo/Glicko/TrueSkill 的估计噪声或发散、收敛慢、对实力变化反应不足等问题。— [项目页](https://cemyuksel.com/research/matchmaking/)；[论文 PDF](https://www.cemyuksel.com/research/matchmaking/i3d2024-matchmaking.pdf)；[DOI 条目](https://www.citedrive.com/en/discovery/skill-based-matchmaking-for-competitive-two-player-games)
- **QuickSkill（Chaoyun Zhang 等，arXiv 2208.07704）**[PP](摘要核验)：解决新手冷启动问题，用新手前几局的序列表现特征预测其未来评分。称比 TrueSkill 及其变体估计更准，用于匹配时一边倒对局减少 20% 以上。在一款知名手机 MOBA 的两种模式上做了离线和在线评估。— [arXiv 2208.07704](https://arxiv.org/pdf/2208.07704)
- **CUPID（2024，arXiv 2406.19720；后发表于 ACM HCI 期刊，crossref DOI 10.1145/3686978）**[PR/PP](摘要核验)：MOBA "重匹配"（re-matchmaking）框架，先预筛选保证基本匹配质量，再用赛前胜率预测模型给候选的队伍和位置分配打分。胜率预测准确率比基线平均相对提升 7.18%，已部署在一款热门 MOBA，A/B 测试显示公平性和位置满意度都有提升。— [arXiv 2406.19720](https://arxiv.org/pdf/2406.19720)；[crossref](https://api.crossref.org/works/10.1145%2F3686978)
- **OptMatch, "Optimized Matchmaking via Modeling the High-Order Interactions on the Arena"** [PR?](摘要核验；会议为 KDD 2020、作者来自网易伏羲是凭记忆，**未核验**)：两阶段数据驱动框架。离线阶段从高阶交互中学习个体表示并训练对局结果预测模型；在线阶段用这些表示改进匹配以提升满意度。在 4 个真实数据集上测试，并在一款篮球游戏上做了线上实验。— [Papers with Code 条目](https://astro.paperswithcode.com/paper/optmatch-optimized-matchmaking-via-modeling)
- **流失与匹配、连胜连败的实证（Heliyon 2024，"Match experiences affect interest: Impacts of matchmaking and performance on churn in a competitive game"）**[PR](摘要核验，**各摘要来源之间有冲突**)：游戏为 *Everybody's Marble*（모두의마블），使用 42 天服务器日志、双向固定效应面板回归。
  - 一份机器生成的摘要称数据约 600 万场、26.2 万名玩家；另一份检索摘要称 2,700 万场。**数据规模有冲突**，需看原文。
  - 发现：对上明显更强的对手时流失上升；对上较弱对手比均衡对局更能降低流失；连败的效应因玩家所处阶段或等级而异。关于胜率和连胜，一份摘要说"胜率与连胜率显著影响流失、连败率不显著"，另一份说"频繁获胜与大分差会正向影响流失"。**方向表述不一致**，引用前必须核对原文。
  - 第一作者"Kang"未核验。
  - 出处：[PubMed 38318006](https://pubmed.ncbi.nlm.nih.gov/38318006)；[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2405844024009228)；[PMC 全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC10839887/)；[JoVE 机器摘要](https://visualize.jove.com/38318006) [INF]
- **定性研究：英雄联盟论坛内容分析（CHI 2018，DOI 10.1145/3173574.3174152，标题未核验）**[PR](摘要核验)：连败损害玩家体验并降低参与度；玩家把连败归因于匹配系统的设计，把单局表现归因于个人。— [ACM DL](https://dl.acm.org/doi/pdf/10.1145/3173574.3174152)
- **"Ever tried. Ever failed. No matter? On the demotivational effect of losing in repeated competitions"（2019，经济学）**[PR?](摘要核验，期刊未确认)：输给相对较弱的对手比输给较强对手更打击积极性。— [上财学术简讯条目](https://academicnewsletter.sufe.edu.cn/info/325893)
- **在线国际象棋中的"经历效应"（胜者–败者效应），层次贝叶斯分析（2025，arXiv 2503.21713）**[PP](摘要核验)：指出人类竞赛中的赢家/输家效应研究远少于动物研究。— [arXiv 2503.21713](https://arxiv.org/pdf/2503.21713)
- **英雄联盟玩家调查（WPI 本科 IQP 报告）**[TH/INF]：排队时间随段位上升而增加，但总体较短；玩家认为实力是胜负主因；玩家喜欢均势的对局，或己方更强的对局。— [WPI 报告](https://web.cs.wpi.edu/~claypool/iqp/lol-match/report.pdf)
- **等待时间 vs 匹配质量的理论（MPMD）**：Emek, Kutten, Wattenhofer, "Online Matching: Haste makes Waste!"（STOC 2016）以游戏平台匹配为动机，提出"带延迟的最小代价完美匹配"。目标是总代价 = 已配对请求间的度量距离（实力差）之和 + 每个请求的等待时间之和，算法必须在线、不可撤销地决策。[PR](摘要核验) — [arXiv 1603.03024](https://arxiv.org/abs/1603.03024)；[机构条目](https://cris.iucc.ac.il/en/publications/online-matching-haste-makes-waste/)。后续 Liu, Pan, Wang, Wattenhofer 研究**凸**延迟代价，即不满随等待时间加速增长，认为更符合游戏匹配。— [arXiv 2203.03335](https://arxiv.org/pdf/2203.03335) [PP/PR]；确定性原始–对偶算法见 [arXiv 1804.08097](https://arxiv.org/pdf/1804.08097)
- **对 EOMM 的批评性评论**：有 Substack 文章把 EOMM 描述为操纵玩家的"大谎言"，并分析了 EnMatch。这是观点性文章，框架强烈，缺乏证据，不宜作为技术或实证依据，只能作为"公众争议存在"的佐证。— [Substack #127](https://raminshokrizade.substack.com/p/127-eomm-the-big-lie-that-was-used)；[Substack #129](https://raminshokrizade.substack.com/p/129-analysing-neteases-enmatch-research) [INF]

### Inferences
- **可行性**：技术上完全可行。只要有流失预测模型（输入近期胜负序列、对手强弱等），就能把匹配写成带权匹配（1v1）或组合优化/强化学习（k-vs-k）问题。纯公平匹配是"流失只取决于胜率且对称"这一特例下的解（EOMM 的论证）。
- **有效性**：现有证据都显示有正向但温和的提升（例如 Lichess 上 4–6%），而且多为作者自有数据、自报结果，缺乏独立复现。最优策略的结构往往是"把会流失玩家的胜利，从不太会流失的玩家那里转移过来"（Chen–Elmachtoub–Lei 的表述）。这意味着部分玩家的对局被有意地变得不公平，即公平与参与度之间存在真实的取舍。
- **与"Elo 感/连败"的联系（对第 3 部分有用）**：EOMM 类系统的输入正是近期胜负序列，所以玩家感受到的"系统在安排连胜连败"在机制上是**可能的**。但学术文献只能证明这类系统存在、在研究中有效，**不能**证明某款具体游戏用了它。另一方面，Yuksel 2024 的"目标胜率匹配"恰恰是**为了减少**长连胜连败而设计的。
- 关于连败是否导致流失，大样本面板研究和定性研究的结论不一致，不能简单断言"连败一定导致流失"。

### Gaps
- 本次没有拿到 EOMM 的具体留存提升百分比，也没有拿到 Delalleau 2012 的定量结果（ACM、IEEE、arxiv 全文均不可达）。
- 没有找到专门的"游戏匹配研究综述"（survey）。检索只返回零散论文，这本身是一个信号：该领域缺少系统综述。
- 没有找到独立第三方对 EOMM/EnMatch 类系统的复现或伦理审查研究。
- Alman & McKay "Theoretical Foundations of Team Matchmaking"（AAMAS 2017）未检索核验。

---

## Q4 实证评估：如何比较评分系统，以及在真实数据上的比较结果

### Takeaway
常用评估指标有：胜负预测准确率或错误率、对数损失（log-loss/binomial deviance）、Brier 分数、MAE、Kendall τ 和 NDCG（多人排名），以及"子群体预期胜率 vs 实际胜率"的校准检查。一个关键方法学陷阱是：**数据本身经过匹配器筛选，对局接近五五开，所以即使系统完美，原始准确率也可能接近 50%**。TrueSkill 论文为此设计了"挑战集"协议。主要结果：TrueSkill 在多数 Halo 2 模式上优于 Elo，在挑战集上优势明显；TrueSkill 2 在 Halo 5 上把准确率从 52% 提到 68%；WHR 自称优于 Elo、Glicko、TrueSkill；Kaggle 2010 冠军是加正则化的 Elo++。

### Cited Findings
- **TrueSkill vs Elo（Halo 2 Beta，Bungie 数据；4 种模式：8 人 FFA、4v4 Small Teams、1v1 Head to Head、8v8 Large Teams）**，指标为预测错误率（预测名次顺序错误的比例；越低越好）。下表按 PDF 坐标重建，粗体值的 y 坐标偏移约 11.9 pt 已校正：

  | 模式 | Elo 全集 | TrueSkill 全集 | Elo 挑战集 | TrueSkill 挑战集 |
  |---|---|---|---|---|
  | Free for All (8 人) | 32.14% | 30.82% | 38.30% | 35.64% |
  | Small Teams (4v4) | 34.92% | 35.23% | 42.55% | 37.17% |
  | Head to Head (1v1) | 33.24% | 32.44% | 40.57% | 30.83% |
  | Large Teams (8v8) | 39.49% | 38.15% | 44.12% | 29.94% |

  原文说明："This measure is difficult to interpret because of the interplay of ranking and matchmaking: Depending on the (unknown) true skills of all players, the smallest achievable prediction error could be as big as 50%." 因此设计了挑战协议：每个系统挑出自认为最势均力敌的 20% 对局，交给对方系统预测。在全集上 Small Teams 一项 Elo 略好；在挑战集上 TrueSkill 全面占优。论文还报告 TrueSkill 自动选出合适的"学习率"，收敛更快，而 Elo 收敛缓慢。— [TrueSkill NIPS 2006](https://www.microsoft.com/en-us/research/wp-content/uploads/2007/01/NIPS2006_0688.pdf) [PR](全文核验)
- **TrueSkill 2 vs TrueSkill（Halo 5，343 Industries 提供 2015 年发售以来的全部对局，"millions of match results"）**：按时间切分训练集和测试集；指标为"预测获胜队伍（或平局）"的准确率，以及各子群体的预期胜率 vs 实际胜率。经典 TrueSkill 52%，TrueSkill 2 68%。批处理对比用了 70 万场 Halo 5 Slayer 对局。Gears of War 4 自 2016 年发售起使用 TrueSkill 2：线上实时更新，每个赛季前用 TrueSkill Through Time 批量重算；AI 机器人按难度各视为一个实力恒定的"玩家"，作为固定基准。— [TrueSkill 2](https://www.microsoft.com/en-us/research/uploads/prod/2018/03/trueskill2.pdf) [TR](全文核验)
- **WHR**：称预测优于 Elo、Glicko、TrueSkill 和 decayed-history 方法，代价是计算量更大。— [WHR.pdf](https://www.remi-coulom.fr/WHR/WHR.pdf) [PR](摘要核验；具体数字未取得)
- **Weng–Lin**：在游戏数据上精度与 TrueSkill 相当，运行时间和代码量都短得多。— [JMLR](https://www.jmlr.org/beta/papers/v12/weng11a.html) [PR](摘要核验)
- **OpenSkill vs TrueSkill**：87.56% 对 92.44%，0.97 s 对 3.41 s（单一数据集，作者自报）。— [arXiv 2401.05451](https://arxiv.org/pdf/2401.05451) [PP](摘要核验)
- **Kaggle "Chess Ratings – Elo vs the Rest of the World"（2010，Jeff Sonas 组织）**：训练集为 8,631 名顶尖棋手的 6.5 万+ 局，预测约 7,800 局。冠军方法 "Elo++"（Yannis Sismanis）基于 Elo，核心是一种防止过拟合的正则化技术。Sonas 提交的 Elo 基准曾短暂排第 1，约一周后跌到 80 份提交中的第 14 名。— [heliosphan.org 竞赛总结](https://heliosphan.org/kagglechessratingscomp.html) [INF]；[Sismanis, arXiv 1012.4571](https://emergentmind.com/papers/1012.4571) [PP]；[KDnuggets 2010](https://www.kdnuggets.com/2010/09/f-kaggle-competition-update.html) [INF]
- **Deloitte/FIDE Chess Rating Challenge（2011，Kaggle）**：约 184 万局、5.4 万+ 名棋手的训练数据，预测其后 3 个月的 10 万局；奖金 1 万美元，获胜队赴雅典向 FIDE 汇报。Glickman 以 Glicko-boost 参赛。— [chessdailynews](https://chessdailynews.com/rocking-the-rating-system/) [INF]；[glicko-boost.pdf](https://www.glicko.net/glicko/glicko-boost.pdf) [TR]。最终排名未核验。
- **评估指标本身的比较（Dehpanah et al.）**：
  - 2020 年（FFA，10 万+ 场死斗/大逃杀）分析了 6 种评估指标，发现它们的有用性差别很大。— [arXiv 2008.06787](https://arxiv.org/abs/2008.06787) [PP](摘要核验)
  - 2021 年（团队大逃杀，2.5 万+ 场）比较 Elo、Glicko、TrueSkill，指标包括准确率、MAE、Kendall τ 和 NDCG。不同指标给出的评价模式差别很大，部分指标受新玩家影响很强，NDCG 最稳定。— [arXiv 2105.14069](https://arxiv.org/pdf/2105.14069v1) [PP](摘要核验)
  - 同组另有研究把行为信号纳入玩家建模以提升评分。— [arXiv 2112.04379](https://arxiv.org/pdf/2112.04379) [PP]
  - 另有 MMBench 基准，跨 1v1、n vs n、大逃杀、团队大逃杀比较 Elo、Glicko、TrueSkill（来源于检索摘要，具体条目未定位）。
- **"Skill Issues: An Analysis of CS:GO Skill Rating Systems"（Bober-Irizar, Dua, McGuinness, Cambridge, arXiv 2410.02831, 2024）**[PP](摘要核验)：在 CS:GO 大数据集上实证比较 Elo、Glicko-2、TrueSkill。采用"代理建模"：评分会反过来驱动后续匹配（可配置的采集函数），并做整体表现、数据效率和参数敏感性分析。背景是 Valve 使用一个未公开的 Glicko-2 变体，其准确性在社区争议很大。具体哪个系统最优未取得。— [arXiv 2410.02831](https://arxiv.org/pdf/2410.02831)
- **Heroes of Newerth：玩家局内表现 vs 评分**（arXiv 1305.5189）[PP](仅标题核验)。— [arXiv 1305.5189](https://arxiv.org/pdf/1305.5189)
- **mElo 在 AlphaGo 变体上优于 Elo**（见 Q2）。— [arXiv 1806.02643](https://arxiv.org/pdf/1806.02643) [PR]

### Inferences
- **"准确率低"不一定说明系统差**：匹配越成功，对局越接近 50/50，可预测性越低。所以有匹配器的游戏数据上，Elo/TrueSkill 的原始准确率常在 55–70% 区间（Halo 2 错误率 30–40%，Halo 5 准确率 52–68%）。评估应改用校准（预期 vs 实际胜率）、log-loss/Brier，或 TrueSkill 的挑战集协议。这一点对第 2、4 部分论证"观察到的胜率≈50% 不代表实力相同"很关键。
- 没有一个系统在所有数据和指标上都赢。增益最大的往往来自"更多信息"（个人统计、车队、全历史平滑），而不是更换评分的核心公式。

### Gaps
- Kaggle 两场比赛的官方评估指标（据记忆，2010 年为按月汇总得分的 RMSE，2011 年为 binomial deviance）及最终排行榜未核验。
- WHR、Skill Issues、Dehpanah 各文的具体数值没能取得原文（arxiv.org 不可达）。
- 没有找到在电竞赛事数据（职业 Dota2/LoL/CS 赛事）上系统比较 Elo/Glicko/TrueSkill 的同行评审论文。

---

## Q5 已知性质与批评：通胀/通缩、收敛速度、K 值敏感性、团队赛中的单排玩家、"Elo hell"

### Takeaway
- 通胀/通缩：顶级国际象棋用基于走子质量的"内在评分"检验，结论是基本没有通胀，但这只排除了部分通胀来源。
- 收敛：Elo 固定 K，收敛慢，需要定级局；贝叶斯系统（Glicko/TrueSkill）通过不确定性自动调节步长。在一定假设下，有关于 Elo 类动力学收敛到真实实力的数学证明。
- K 值是"跟踪速度 vs 稳态噪声"的权衡。
- 团队游戏中，求和聚合对车队系统性低估，单排玩家因此吃亏，TrueSkill 2 给出了定量证据和修正。
- "Elo hell" 在同行评审文献中几乎没有正式研究，只有一篇 2012 年台湾学位论文讨论"未收敛评分导致不平衡匹配"，其余都是论坛观点。

### Cited Findings
- **通胀**：Regan & Haworth (AAAI 2011), "Intrinsic Chess Ratings"，用高深度引擎评估棋步质量来拟合棋手参数（敏感度、一致性），再映射到 Elo。结论："ratings are shown to have stayed quite constant over time. That is, there has been little or no 'rating inflation'"。— [AAAI 页面](https://ojs.aaai.org/index.php/AAAI/article/view/7951)；[作者 PDF](https://cse.buffalo.edu/~regan/papers/pdf/RMH11.pdf) [PR](摘要核验)。后续 Regan, Macieja, Haworth (2011) 的措辞更谨慎：数据没有提供通胀证据，排除了两种通胀来源，但"do not disprove the inflation theory"；并指出这一问题也关系到最优 K 值。— [Regan 演讲 PDF](https://cse.buffalo.edu/faculty/regan/Talks/ReganMaciejaHaworth2011.pdf) [PR/演讲](摘要核验)
- **通胀/通缩的机制**（推论加已知讨论）：双方 K 相同时零和，新玩家带着初始分进入、带走或留下分数，以及新手进步快而系统追不上（通缩），都会让分池整体漂移。Glickman 的综述有系统讨论。— [Glickman 1995 指南](http://www.glicko.net/research/acjpaper.pdf) (未核验)
- **收敛速度**：TrueSkill 论文显示 TrueSkill "automatically chooses the correct learning rate whereas Elo only slowly converges"；Elo 的临时分阶段约 20 局。— [TrueSkill NIPS 2006](https://www.microsoft.com/en-us/research/wp-content/uploads/2007/01/NIPS2006_0688.pdf) [PR](全文核验)
- **收敛的数学理论**：Jabin & Junca 的动力学（kinetic）Elo 模型在一定假设下证明评分收敛到真实实力。Bertram, Fischer, Wolfram (2021) 推广到个人或团队表现可变的情形（二人零和设定）。— [arXiv 2109.15046](https://arxiv.org/pdf/2109.15046) [PP](摘要核验)
- **K 值敏感性**：α = 0.07 ≈ K = 24 被视为"良好且稳定"。— [TrueSkill NIPS 2006](https://www.microsoft.com/en-us/research/wp-content/uploads/2007/01/NIPS2006_0688.pdf)。Skill Issues (2024) 对 Elo、Glicko-2、TrueSkill 做了参数敏感性分析（具体数值未取得）。— [arXiv 2410.02831](https://arxiv.org/pdf/2410.02831) [PP]。在 LLM 评测领域，"Elo Uncovered"（Boubdir et al., 2023）报告 Elo 排名对 K 和对局顺序敏感 [PP](未核验)，可作为跨领域佐证。
- **团队赛中单排 vs 车队**：TrueSkill 2 在 Halo 5 中发现车队实际胜率显著高于求和预期，≥10 人车队实际 89%、预期 67%。部分模式因此禁止大车队，代价是匹配池缩小。TrueSkill 2 的修正是按车队规模给表现加偏移。— [TrueSkill 2](https://www.microsoft.com/en-us/research/uploads/prod/2018/03/trueskill2.pdf) [TR](全文核验)
- **聚合方式影响预测**：MAX 优于 SUM/AVG。— [arXiv 2106.11397](https://arxiv.org/pdf/2106.11397) [PR](摘要核验)
- **评分未收敛导致不平衡匹配**：台湾交通大学 2012 年学位论文（Chen & Sun）指出："the ELO ranking system has a limitation that player must play enough games to converge effective ELO score"，而匹配器无法判断某个分数是否已收敛，"match making system often generates unbalanced match"。论文提出评估个人与团队影响加以修正。— [NYCU 机构库](https://ir.lib.nycu.edu.tw/handle/11536/71640) [TH](摘要核验)
- **"Elo hell" 的讨论**：有论坛帖把它定义为"团队评分 + 个人对结果影响小 + 无法控制队友"的组合，并称这是数学事实；也有战队文章否认它真实存在。两者都没有正式证据。— [Blizzard 论坛](https://us.forums.blizzard.com/en/heroes/t/elo-hell-is-real/27222) [INF]；[Dignitas](https://dignitas.gg/articles/blogs/Unknown/10719/myths-and-facts-about-elo-hell-and-the-proper-climbing-mentality) [INF]
- **连胜/连败可以在设计上抑制**：Yuksel 2024 的目标胜率匹配。— [项目页](https://cemyuksel.com/research/matchmaking/) [PR](摘要核验)
- **激励问题**：
  - TrueSkill 2 要求评分体系"aligned incentives"，避免奖励玩家刷个人数据而牺牲团队。— [TrueSkill 2](https://www.microsoft.com/en-us/research/uploads/prod/2018/03/trueskill2.pdf)
  - Elo-MMR 证明了不存在"故意打差"的激励。— [DOI 10.1145/3442381.3450091](https://doi.org/10.1145/3442381.3450091)
  - Elo 可以被"刷副本"抬分。— [Balduzzi et al. 2018](https://arxiv.org/pdf/1806.02643)
- **非传递性**：Elo 在循环博弈中失效，mElo 部分弥补（见 Q2）。— [arXiv 1806.02643](https://arxiv.org/pdf/1806.02643)

### Inferences
- **"Elo hell" 的可能学术解释**（推论，没有直接文献证明）：在团队游戏中，个人对胜负的边际影响约为 1/N，评分收敛慢，短期内运气（队友、对手）方差大；如果再叠加求和聚合低估车队，单排玩家会对上被低估的车队。这些因素足以让玩家"感觉"被卡在某个分段。但从长期期望看，玩家真实贡献仍会体现：系统性偏差主要来自车队效应和未收敛，不是一个"无法爬出的地狱"。这需要第 2、3 部分用数学和模拟验证。
- K 值越大、单局权重越高，评分随机游走的稳态方差越大，"连胜连败"带来的分数大起大落也越明显。这也是第 3 部分的一个可检验假设。

### Gaps
- 没有找到在电子游戏场景下定量研究"Elo hell 是否存在"的同行评审论文。
- 没有核验 FIDE 近年为对抗低分段通缩做的规则调整（据记忆约在 2024 年），以及 Glickman 或 Sonas 关于通缩的具体数据。
- "Elo Uncovered" 等 K 敏感性论文未核验。

---

## Q6 中文学术文献（知网/学位论文）中关于游戏匹配机制、ELO 算法、天梯的值得注意的工作

### Takeaway
本次检索**没有发现**值得引用的中文同行评审期刊论文（知网无法直接访问，中文检索结果以 CSDN、GameRes、萌娘百科、澎湃等非正式文章为主）。中国机构最有分量的贡献是发表在国际顶会的英文论文，如网易伏羲的 EnMatch（AAAI 2024）和（据记忆）OptMatch。中文学位论文方面，只检索到台湾交通大学 2012 年一篇讨论 Elo 未收敛导致匹配不平衡的论文。

### Cited Findings
- **网易伏羲 EnMatch（AAAI 2024）**：参与度导向的 k-vs-k 匹配，见 Q3。— [AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/28760) [PR](摘要核验)
- **OptMatch**：竞技场类游戏的两阶段匹配，在篮球游戏上做了线上实验。会议和机构（KDD 2020 / 网易伏羲）未核验。— [Papers with Code](https://astro.paperswithcode.com/paper/optmatch-optimized-matchmaking-via-modeling) [PR?](摘要核验)
- **QuickSkill**（移动 MOBA 新手冷启动）和 **CUPID**（MOBA 重匹配并已上线部署）：两者的作者机构是否为中国游戏公司未核验，见 Q3。— [arXiv 2208.07704](https://arxiv.org/pdf/2208.07704)；[arXiv 2406.19720](https://arxiv.org/pdf/2406.19720) [PP/PR]
- **Chen–Elmachtoub–Lei（Management Science）**：合作者 Xiao Lei 来自香港大学，相关研究海报和报告见港城大和港中文页面。— [港中文商学院条目](https://www.bschool.cuhk.edu.hk/?p=36593)；[港城大海报](https://www.cb.cityu.edu.hk/ms/sites/g/files/asqsls5586/files/2022-09/Poster%20-%20Dr%20Xiao%20Lei.pdf) [INF]
- **台湾交通大学 2012 学位论文（Chen & Sun）**：Elo 未收敛导致团队匹配不平衡，提出评估个人与团队影响。— [NYCU](https://ir.lib.nycu.edu.tw/handle/11536/71640) [TH](摘要核验)
- **中文非正式资料**（只能作背景，不能作学术依据）：
  - 萌娘百科"ELO算法"：中文互联网常把基于 Elo 或其变体的隐藏分机制称为"Elo 机制"；匹配等待时间长时会放宽分差容忍度；炉石传说使用可变学习率（K）。— [萌娘百科](https://zh.moegirl.org.cn/ELO%E7%AE%97%E6%B3%95) [INF]
  - GameRes《游戏设计左道：匹配机制 Elo 系统介绍与 Trueskill 系统原理研究》。— [GameRes](https://www.gameres.com/908465.html) [INF]
  - 澎湃湃客《为什么同样一套段位算法，能让柯洁风光无限，也能逼疯无数上分玩家？》。— [澎湃](https://www.thepaper.cn/newsDetail_forward_7209036) [INF]
  - CSDN 上有开发者文章称匹配目标是让队伍胜率尽量接近 50%，希望多数队伍胜率不超过 55%（无数据支撑）。— [CSDN](https://blog.csdn.net/apengjiang/article/details/7232532) [INF]
  - CSDN《游戏匹配算法实现（基于 ELO 分数、等待时长）》。— [CSDN](https://blog.csdn.net/best789248/article/details/78429538) [INF]
- **相关英文硕士论文（非中文，供参考）**：Laurentian 大学的 CentroMatch 以英雄联盟为实验场景，结合 Elo、TrueSkill 2 与图算法，加上问卷与访谈，称对局更均衡、毒性行为可能性更低。— [Laurentian](https://laurentian.scholaris.ca/items/e188a443-7085-4467-b0d8-0e4fb0d9f50e) [TH](摘要核验)；Radboud 本科论文《Improving matchmaking with game data》。— [cs.ru.nl](https://www.cs.ru.nl/bachelors-theses/2016/Wietse_Kuipers___4317904___Improving_matchmaking_with_game_data.pdf) [TH]

### Inferences
- 中国游戏公司（网易、腾讯等）的匹配研究主要以英文发表在 AAAI/KDD/WWW/CHI 等会议，中文期刊和学位论文中的"ELO 匹配"工作多为工程实现或课程级改进，学术影响有限（这个判断基于本次检索的覆盖面，并非对知网的穷尽检索）。
- 中文舆论中的"Elo 机制"一词常被用来指"系统操纵胜负"，这与学术上"Elo = 成对比较评分"的含义不同。最终报告应明确区分"评分系统（Elo/TrueSkill）"和"匹配策略（SBMM/EOMM）"两个层面。

### Gaps
- 无法访问知网、万方、维普，没能检索中文期刊和硕博论文。建议用关键词"游戏 匹配 TrueSkill""MOBA 匹配 冷启动""ELO 改进 天梯""参与度 匹配 流失"在知网补检。
- 没有核验腾讯、网易等其他英文匹配论文（如 GloMatch 等名称在本次检索中未命中）。
