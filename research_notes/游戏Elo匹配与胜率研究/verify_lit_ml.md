# 事实核查：lit_academic.md 与 ml_training.md（学术文献与 ML 训练部分）

> 核查对象：`lit_academic.md`（下称 LIT）和 `ml_training.md`（下称 ML）。原文件未修改。核查日期 2026-10-18。
> **方法**：
> - microsoft.com 可以直连。因此 TrueSkill（NIPS 2006）PDF、TrueSkill 2 PDF、MSR TrueSkill 项目页/FAQ、MSR 出版物页、Graepel & Herbrich 的 Game Developer 文章、QuickSkill 的 MSR 页面都**下载并逐字核对**过。TrueSkill 第 6、7 页还渲染成图片，用来核对表格和希腊字母。
> - GitHub raw 可以直连，DI-engine 的 PFSP 源码直接读过。
> - 其余主机都返回 CONNECT 403 或 DNS 失败，包括 arxiv、jmlr、neurips、acm、aaai、lmsys、arena.ai、semanticscholar、crossref、openreview、informs、pmc、sciencedirect、gwern、mlr.press、glicko.net、themoonlight 等，WebFetch 也同样失败。这些条目只能用 WebSearch 摘要交叉核对。
> - Elo/SGD 推导、Fisher 信息、稳态方差和样本量数字都写成 Python 脚本独立复算过（`/tmp/claude-0/-home-user-DeepBattlerPlugin/f35f0f34-7043-5f04-a498-40b548a0550d/scratchpad/scripts/elo_math.py`），其中稳态方差还做了蒙特卡洛模拟。
>
> **判定规则**：
> - CONFIRMED：一手原文已读，或者至少两个独立摘要一致。
> - CONFIRMED-as-reported：只有二手来源，而且彼此一致。
> - CORRECTED：原说法有误或不精确，正文给出更正。
> - REFUTED：与证据相反。
> - UNVERIFIABLE：查不到可靠支持。
>
> **结果概览**：共核查 64 条（汇总表 T/B/C/D/E/M/F 各组）。
> - CONFIRMED（含 as-reported）：55 条。其中 M4、M10 有部分子项无法核实。
> - CORRECTED：7 条（T4、B4、B12、C5、C10、E3、M3）。
> - UNVERIFIABLE：2 条，即 E2 和 E6 的数值。另有以下子项无法核实：C10 的"20%"、M4 中 AlphaGo Zero 的 BayesElo、M10 的 DeepMind 引语、B12 中的一句转述。
> - REFUTED：0 条。
>
> 另外，LIT/ML 中有 5 处原本标为"未核验/凭记忆"的条目，这次确认为真：Bertrand et al. AISTATS 2023、Balduzzi et al. ICML 2019、α-Rank、OpenAI Five 的 80/20、Christiano 2017 的 BT 损失。还有 1 处补全了作者：arXiv 2502.10985。
> **没有发现方向性错误**。主要问题有三类：(1) ML 把 TrueSkill 对照实验的参数 α 写成了 β；(2) 部分电竞预测数字张冠李戴；(3) Heliyon 研究的"冲突"其实可以澄清，结论是**连败不显著**。

---

## 一、汇总表

### A. TrueSkill / TrueSkill 2（一手 PDF 逐字核对）
| # | 主张 | 出处 | 结论 | 置信度 |
|---|---|---|---|---|
| T1 | TrueSkill NIPS 2006 预测错误率表（16 个数，FFA 32.14/30.82/38.30/35.64 等） | LIT Q4，ML Q3 | CONFIRMED（逐格核对渲染图） | 高 |
| T2 | 原文："the smallest achievable prediction error could be as big as 50%" | LIT Q4，ML Q3/Q4 | CONFIRMED（逐字） | 高 |
| T3 | 原文："50% (the optimal winning ratio)"；局数很少的玩家胜率也在 35%–65% 之内 | LIT Q3，ML Q3/Q7 | CONFIRMED（逐字）。限定条件：仅指 Head to Head 模式，且已剔除低匹配质量的对局 | 高 |
| T4 | Elo 对照参数 0.07 ≈ K=24 | LIT Q1 写 α；ML Q1 写 β | LIT CONFIRMED；**ML CORRECTED：应为 α=0.07，不是 β** | 高 |
| T5 | TrueSkill FAQ："every match-made game where the game outcome is not predictable ahead of time ensures that the game is informative!"；log₂(n!) 比特；t·p·log₂(n)/log₂(t!) 局；"primary purpose…minimize the number of games" | ML Q3/Q8 | CONFIRMED（MSR 项目页逐字） | 高 |
| T6 | TrueSkill 2：MSR-TR-2018-8（2018-03）；准确率 52% vs 68%；车队表（≥10 人实际 89% vs 预期 67%）；训练 2300 万局、测试 300 万局；70 万场 Slayer；Gears of War 4 自 2016 起使用 | LIT Q2/Q4/Q5，ML Q2/Q3/Q4 | CONFIRMED（PDF 逐字）。注意：准确率指"预测获胜队或平局"，选项数 = 队数 + 1，所以 52% 不能直接等同于"二选一抛硬币" | 高 |
| T7 | Elo 1959 年提出、FIDE 1970 年采用；Halo 2 Beta 数据来自 Bungie；"Gaussian density filtering"；匹配质量 = 相对平局概率（ε→0）；Xbox Live 参数 μ0=25、σ0=25/3、β=σ0/2、动态项 σ0/100；排行榜用 μ−3σ；"hundreds of thousands of games per day" | LIT Q1/Q2，ML Q1 | CONFIRMED（逐字）。记号说明：论文把动态方差记作 γ²，LIT 写的 τ 是开源库的记号，含义相同 | 高 |
| T8 | TrueSkill 团队表现 = 成员表现之和 | LIT Q2 | CONFIRMED。补充：论文自己承认在 Small Teams 模式下匹配质量不如 Elo，原因"possibly due to the violation of the additive team performance model"（多为夺旗模式） | 高 |

### B. 基础与后继模型的书目
| # | 主张 | 出处 | 结论 | 置信度 |
|---|---|---|---|---|
| B1 | Elo 原书：Arco 1978，ISBN 0-668-04721-6，第二版 1986 | LIT Q1 | CONFIRMED（ISBN-13 9780668047210） | 高 |
| B2 | Bradley & Terry (1952)，*Biometrika* 39(3/4):324–345 | LIT Q1 | CONFIRMED（作者 Ralph A. Bradley、Milton E. Terry） | 高 |
| B3 | Glickman 1999 *JRSS-C* 48(3):377–394；Glicko-2 = Glickman 2001 *J. Appl. Stat.* 28(6):673–689；Glicko-2 内部标度 173.7178、波动率用 Illinois 法求解、τ 为系统常数 | LIT Q2 | CONFIRMED（RePEc；多份实现文档一致；glicko.net 原文不可达） | 高 / 中高 |
| B4 | TrueSkill 的卷号：MSR 页写 NIPS 20，Herbrich 主页写 NIPS 19, pp.569–576 | LIT Q2 | **CORRECTED**：应引作 *Advances in NIPS 19 (NIPS 2006)*, pp. 569–576, MIT Press, 2007。MSR 出版物页写的 "Advances in Neural Information Processing Systems 20 \| January 2007" 是 MSR 页面自身的错误 | 高 |
| B5 | Weng & Lin (2011)，*JMLR* 12:267–300 | LIT Q2，ML Q1 | CONFIRMED（Ruby C. Weng、Chih-Jen Lin） | 高 |
| B6 | WHR：Coulom 2008，Computers and Games（LNCS 5131） | LIT Q2 | CONFIRMED；补页码 pp.113–124 | 高 |
| B7 | Elo-MMR：Ebtekar & Liu，WWW 2021 pp.1772–1784；激励相容 | LIT Q2，ML Q7/Q8 | CONFIRMED（arXiv 版标题为 "An Elo-like System for Massive Multiplayer Competitions"） | 高 |
| B8 | Balduzzi, Tuyls, Pérolat, Graepel，"Re-evaluating Evaluation"，NeurIPS 2018（mElo、Nash averaging） | LIT Q2，ML Q5 | CONFIRMED；补 NeurIPS 31 pp.3268–3279。原文称 Elo 的预测失败来自循环分量。Atari 方面：Nash averaging 下"超人"优势被解释为基准偏差，20 个智能体 × 54 个环境。"人类与最佳智能体打平"的具体措辞没能逐字核对 | 中高 |
| B9 | Balduzzi et al.，ICML 2019，"Open-ended Learning in Symmetric Zero-sum Games"（PSRO_rN） | ML Q5（标"未核实"） | CONFIRMED：PMLR 97:434–443；arXiv 1901.08106 | 高 |
| B10 | Czarnecki et al.，NeurIPS 2020，"Real World Games Look Like Spinning Tops"；9 个两人零和对称博弈；Nash 聚类 | LIT Q2（标未核验），ML Q5 | CONFIRMED（NeurIPS 2020 论文集；meta-review 评为 borderline accept） | 高 |
| B11 | Bertrand, Czarnecki, Gidel，AISTATS 2023，"On the Limitations of the Elo…" | LIT Q2（标"凭记忆，必须核对"） | CONFIRMED：PMLR 206:2905–2921；arXiv 2206.12301 | 高 |
| B12 | arXiv 2502.10985（作者不明） | LIT Q2，ML Q1 | 补全并 **部分 CORRECTED**：Shange Tang、Yuanhao Wang、Chi Jin（Princeton），"Is Elo Rating Reliable? A Study Under Model Misspecification"（2025-02）。以下三点已证实：BT 模型在多数真实数据上被拒绝，但 Elo 预测仍常优于 mElo；Elo 可视为在线梯度下降，有 no-regret 保证；数据稀疏是 Elo 占优的原因。LIT 中"在任意匹配机制下，即使数据传递，Elo 也可能给不出一致排序"一句**没有找到支持**，建议删除或标注未核验 | 中 |
| B13 | Szczecinski & Djebbi，arXiv:1910.06081：Elo 是随机梯度；κ-Elo | ML Q1 | CONFIRMED（INRS；期刊版为 "Understanding draws in Elo rating algorithm"，*JQAS* 2020, 16(3):211–220）。另有 Szczecinski 2026 年的 arXiv:2604.03840 明确写到 "online maximum likelihood estimation via stochastic gradient ascent" | 中高 |
| B14 | arXiv:2411.00119 Soft Condorcet Optimization（Lanctot 等，DeepMind） | ML Q1 | CONFIRMED（AAMAS 2025 pp.1253–1262）。摘要层面能证实"Elo 不一定把 Condorcet 赢家排第一"；ML 引用的梯度推导细节没能看到原文，但推导本身数学上正确（见 D1） | 中 |
| B15 | Thurstone 1927 *Psych. Rev.* 34(4)；Zermelo 1929 *Math. Z.* 29:436–460 | LIT Q1 | CONFIRMED（Thurstone 的页码 273–286 未在摘要中出现） | 高 / 中 |
| B16 | TrueSkill Through Time，NIPS 2007 pp.931–938 | LIT Q2 | CONFIRMED（NIPS 20；约 350 万局、150 年国际象棋数据） | 高 |
| B17 | Aldous 2017，*Statistical Science* 32(4):616–629 | LIT Q1 | CONFIRMED（另见第三节 F6） | 高 |
| B18 | α-Rank（Omidshafiei et al. 2019，*Sci. Rep.* 9:9937） | ML Q5（标未核实） | CONFIRMED（DOI 10.1038/s41598-019-45619-9；Markov–Conley chains；在 AlphaGo、AlphaZero、MuJoCo Soccer、Poker 上验证） | 高 |
| B19 | Dehpanah et al.，IEEE CoG 2021，团队聚合：MAX 在多数情形最好 | LIT Q2/Q5 | CONFIRMED（DePaul；3 个数据集，10 万+ 场） | 高 |
| B20 | Yuksel 2024，I3D / PACM CGIT，DOI 10.1145/3651303，目标胜率匹配 | LIT Q3/Q5 | CONFIRMED（作者单位含 University of Utah 与 **Roblox**） | 高 |
| B21 | Emek, Kutten, Wattenhofer，STOC 2016（MPMD） | LIT Q3 | CONFIRMED（pp.333–344；竞争比 O(log²n + logΔ)） | 高 |
| B22 | "Elo Uncovered"（Boubdir et al. 2023）：Elo 对 K 和对局顺序敏感 | LIT Q5（标未核验） | CONFIRMED（GEM 2023 workshop，Cohere For AI 团队）。原文还写到"胜率接近 0.5 时 Elo 波动最大"，以及需要 ≥100 次顺序置换取平均 | 高 |

### C. 匹配机制、竞赛与规章
| # | 主张 | 出处 | 结论 | 置信度 |
|---|---|---|---|---|
| C1 | Delalleau et al. 2012，IEEE TCIAIG 4(3):167–177，Ghost Recon Online | LIT Q3 | CONFIRMED（多篇引用一致；模型名为 FunNet，乐趣标签来自游戏内问卷） | 中高 |
| C2 | EOMM，WWW 2017，EA，7 位作者，仿真，仅 1v1；LIT 称"没拿到留存提升百分比" | LIT Q3，ML Q7 | CONFIRMED，并补全数字：相对 SkillMM，每轮多留存 **0.3% / 0.9% / 1.1% / 0.6%（等待池 P=200/300/400/500），平均 0.7%**。"1.007²⁰ ≈ 1.15，即 8 小时内多留 15%"是**外推**，不是测量值。P=100 时不显著优于随机匹配，甚至少于 SkillMM | 中高 |
| C3 | Chen–Elmachtoub–Lei，*Management Science*，DOI 10.1287/mnsc.2023.02957；Lichess 540 万场对局，参与度 +4–6% | LIT Q3 | CONFIRMED（INFORMS 官方新闻稿逐条一致，2026-06）。补充两点：论文版本表述为"+4–6% 参与度，或机器人比例 −3%"；理论情形下最高 +50%（只是理论值） | 中高 |
| C4 | EnMatch，AAAI 2024, 38(8):9098–9106，网易伏羲，10 位作者 | LIT Q3/Q6 | CONFIRMED | 高 |
| C5 | Heliyon 2024 面板研究：作者、数据规模、效应方向"相互冲突" | LIT Q3 | **CORRECTED（澄清）**：作者 Kang, Suh, Kim，*Heliyon* 10(3):e24891。数据为 42 天日志，**约 600 万场、26.2 万名玩家**，"2700 万场"没有任何支持。效应方向：连胜率系数 −0.0104（显著，降低流失）；**连败率系数 ≈ 0.0001，不显著**；总胜率 −0.0037（显著）；对上更强对手时流失上升，对上较弱对手比均衡对局更能降低流失 | 中（系数来自单一检索摘要读到的表格） |
| C6 | Regan & Haworth，AAAI 2011，"Intrinsic Chess Ratings"："little or no 'rating inflation'" | LIT Q5 | CONFIRMED（pp.834–839；后续演讲的措辞更谨慎） | 高 |
| C7 | Kaggle 2010：8,631 名棋手、6.5 万+ 局、预测约 7,800 局；Sonas 的 Elo 基准一度排第 1，一周后跌到 80 份中的第 14；冠军 Elo++（Sismanis，正则化） | LIT Q4 | CONFIRMED（65,053 行、预测 7,809 局；Elo++ 用 SGD 训练 + l2 正则；评分指标 RMSE 有提及，但"按月汇总"没有证实） | 高 |
| C8 | Deloitte/FIDE 2011：约 184 万局、5.4 万+ 名棋手、预测其后 3 个月的 10 万局；Glickman 以 Glicko-boost 参赛 | LIT Q4 | CONFIRMED（奖金 1 万美元、雅典汇报两点没有单独核对） | 中高 |
| C9 | EA DDA（Xue et al.，WWW 2017 Companion pp.465–471）："参与度最多提升 9%，对付费中性" | ML Q7 | CONFIRMED（DOI 10.1145/3041021.3054170；部署于多款 EA 游戏） | 高 |
| C10 | QuickSkill："arXiv 预印本"，"知名手机 MOBA"，"一边倒对局减少 20% 以上" | LIT Q3/Q6 | **CORRECTED**：这是同行评审论文，发表于 **CIKM 2022**（DOI 10.1145/3511808.3557070），作者 Chaoyun Zhang 等 7 人（据检索摘要为腾讯）。MSR 页面摘要只写 "a popular mobile multiplayer game"，没写 MOBA。"20%"在摘要中找不到，属 UNVERIFIABLE | 中 |
| C11 | CUPID：胜率预测准确率比基线平均相对提升 7.18%，已部署，做过 A/B 测试 | LIT Q3 | CONFIRMED（7.18% 指离线预测精度，不是 A/B 结果；作者来自腾讯、微软、字节跳动、深圳大学、哈工大深圳） | 高 |
| C12 | FIDE K 值：新棋手前 30 局 K=40，18 岁以下且 <2300 时 K=40，<2400 时 K=20，达到 2400 后 K=10；400 分规则 | LIT Q1 | CONFIRMED，附细节：K=10 一旦达到 2400 就永久适用，即使之后跌破；另有 K×局数 ≤ 700 的上限。"400 分规则"见于旧版规章，2024 年后的文本没有逐字核对 | 中高 |

### D. 数学推导（独立复算）
| # | 主张 | 出处 | 结论 | 置信度 |
|---|---|---|---|---|
| D1 | Elo 更新 = 对 BT/logistic 对数损失做一步 SGD；p = σ(c·Δ)，c = ln10/400 ≈ 0.005756；K = η·c；400 分差 ↔ 10:1 赔率（约 90.9%） | LIT Q1，ML Q1 | CONFIRMED。数值梯度与解析式 −c(y−p) 一致到 1e-9，SGD 一步与 Elo 公式结果相同。文献支持：Szczecinski & Djebbi 2019/2020；Tang–Wang–Jin 2025（OGD）；Szczecinski 2026（2604.03840）；Olesker-Taylor & Zanetti NeurIPS 2024（把 η 作为学习率分析 Elo 收敛） | 高 |
| D2 | 单局对评分差 d 的 Fisher 信息 I(d) = c²·p(1−p)，在 p=0.5 时最大，为 c²/4 | ML Q3 | CONFIRMED（数值核对：d=0/100/200/400 时 I 与 c²p(1−p) 完全一致）。这一点没有找到专门的文献原话，属于标准结论 | 高 |
| D3 | 恒定 K 的稳态方差 ≈ K/(2c)；K=32 时标准差约 53 分，约 ±7.5 个百分点；分辨 5 分 Elo 需约 19,000 局，50 分约 190 局；log₂(8!) ≈ 15.3 | ML Q3/Q8 | CONFIRMED（解析值 52.7；模拟 40 万局得 54.1，一阶近似略偏小；19,314 局 / 193 局；15.30） | 高 |

### E. 电竞赛前预测
| # | 主张 | 出处 | 结论 | 置信度 |
|---|---|---|---|---|
| E1 | Conley & Perry（CS229, 2013）：仅用阵容的逻辑回归约 69.8% | ML Q4 | CONFIRMED-as-reported（一篇二手论文给出 69.8%；Scribd 摘要另有"63%"的说法，原 PDF 不可达） | 中 |
| E2 | Song 等（CS229, 2015）：最佳逻辑回归约 58%，加英雄组合约 61%（"据 arXiv:2106.01782 转述"） | ML Q4 | **UNVERIFIABLE**：Song 报告只能证实结论是"仅凭阵容不足以预测"。2106.01782（Akhmedov & Phan）的摘要里没有 58%/61%。怀疑"58%"与 1701.03162 的 58.69% 混淆 | 低 |
| E3 | arXiv:1701.03162：仅用英雄的逻辑回归 60.07%，加玩家与玩家-英雄特征后 71.49% | ML Q4 | **CORRECTED**：摘要原文是"随着加入更多赛前特征，准确率从 **58.69%** 升到 71.49%"。"60.07%"找不到出处。作者 Yifan Yang、Tian Qin、Yu-Heng Lei（CMU），78,362 场对局；第 40 分钟的实时预测可达 93.73% | 中高 |
| E4 | Yashkov/Semenov 等：选人阶段 AUC 0.66–0.70，分段越高越难预测 | ML Q4 | CONFIRMED-as-reported：幻灯片给出 AUC 约 0.66–0.70；阵容在极高分段只解释约 6% 的信息，普通分段约 10%。论文为 Semenov et al., AIST 2016, CCIS pp.26–37，DOI 10.1007/978-3-319-52920-2_3 | 中 |
| E5 | LoL：Do et al.，FDG 2021，开局前 75.1% | ML Q4 | CONFIRMED（DBLP：FDG'21 pp.46:1–46:5；作者 Tiffany D. Do, Seong Ioi Wang, Dylan S. Yu, Matthew G. McMillian, Ryan P. McMahan） | 高 |
| E6 | 板球 arXiv:2603.02574：Elo 的 Brier 0.1896、log-loss 0.6570；Glicko 的 Brier 0.2050、log-loss 0.6889 | ML Q2 | 论文身份 CONFIRMED（Bandyopadhyay & Mukherjee，"An Augmented Rating System for Test Cricket: adapting Glicko's model"，2026-03）。**数值 UNVERIFIABLE**。注意论文主旨是改进 Glicko，引用"Elo 优于 Glicko"时要说明比较的是未改进的 Glicko | 低 |

### M. 自博弈与 ML 中的 BT/Elo
| # | 主张 | 出处 | 结论 | 置信度 |
|---|---|---|---|---|
| M1 | OpenAI Five 自博弈：80% 对当前自己，20% 对历史版本 | ML Q5（标二手） | CONFIRMED（OpenAI 官方博客原句："To avoid 'strategy collapse', the agent trains 80% of its games against itself and the other 20% against its past selves"） | 高 |
| M2 | PFSP 权重 f_hard = (1−x)^p、f_var = x(1−x)；DI-engine 中 'squared' = (1−x)²、'variance' = x(1−x) | ML Q3/Q5 | DI-engine 部分 CONFIRMED（直接读了源码）；(1−x)^p 与 x(1−x) 为 CONFIRMED-as-reported（自博弈综述 2408.01072、FootsiesGym 写"按 Vinyals 2019 用 (1−p̂)^{1/2}"）。AlphaStar 论文 Methods 原文不可达 | 中 |
| M3 | AlphaGo Zero 评分：5185 / Master 4858；Lee 约 3500–3700 | ML Q5 | **CORRECTED（精确化）**：论文图 6b 为 Zero(40 block) **5185**、Master **4858**、Lee **3739**、Fan **3144**。"3500–3700"是 DeepMind 博客图的目测值。100:0 战胜 Lee、89:11 战胜 Master 有两处二手来源 | 中高 |
| M4 | AlphaGo Zero 以 55% 胜率为替换门槛；Elo 用 BayesElo 计算 | ML Q5（标记忆） | 55% / 400 局：CONFIRMED-as-reported（≥2 个二手来源）。BayesElo + c_elo = 1/400：AlphaZero 论文明确如此；用于 AlphaGo Zero 只有单一二手来源，属 UNVERIFIABLE。lifein19x19 有帖称 5185 仅基于对 Lee/Master 的结果（未核实） | 中 |
| M5 | Chatbot Arena 于 2023-12-07 由在线 Elo 改为 Bradley–Terry；理由是在线 Elo 依赖对局顺序，BT "significantly more stable ratings and precise confidence intervals" | ML Q1/Q6 | CONFIRMED（博文 "Chatbot Arena: New models & Elo system update"，作者 Chiang, Li, Gonzalez, Stoica；arena.ai 镜像日期为 12-08）。Chiang et al. ICML 2024，arXiv 2403.04132 | 高 |
| M6 | Christiano 2017 的奖励模型是 Bradley–Terry 型 | ML Q6（标未核实） | CONFIRMED（原文："This follows the Bradley-Terry model … specialization of the Luce-Shephard choice rule"，并与 Elo 作类比） | 高 |
| M7 | InstructGPT 损失：−1/C(K,2) · E[log σ(r(x,y_w) − r(x,y_l))]，把 K 个回答拆成成对比较 | ML Q6 | CONFIRMED-as-reported（rlhfbook；Zhu–Jordan–Jiao 2023；K=4–9） | 中高 |
| M8 | OpenAI Five：83 个参考智能体，TrueSkill 0（随机）到 254（击败世界冠军的版本）；每个版本报告 750 局后记录 | ML Q5 | CONFIRMED（论文 Appendix J 摘要）。补充：8.3 TrueSkill 差 ≈ 80% 胜率；评估时避开相差 >10 分（胜率 <15% 或 >85%）的对手；参数 σ=25/3、β=σ/2、τ=0 | 高 |
| M9 | Leela Chess Zero 的自博弈 Elo 通胀，不可跨 run 比较 | ML Q5 | CONFIRMED（维基条目原句："Measuring Elo relative to previous networks fails to measure general strength since networks are trained to anticipate and beat the predictions made by prior Lc0 networks"；TalkChess 有用户实测：官方 +241/+311，实测 −8/−57） | 中高 |
| M10 | AlphaStar：宗师级、高于 99.8% 的活跃玩家；DeepMind 称"只为赢而下是不够的" | ML Q5 | 前半 CONFIRMED（三族均达宗师）。**后半引语 UNVERIFIABLE**：DeepMind 博客原文不可达，检索没找到这句，引用时不要加引号 | 中 |
| M11 | GAN：D* = p_data/(p_data+p_g)，均衡处 D=1/2，C(G) = −log4 + 2·JSD | ML Q6 | CONFIRMED（标准结论；多份二手来源一致） | 高 |

### F. 其他补充核对
| # | 主张 | 出处 | 结论 | 置信度 |
|---|---|---|---|---|
| F1 | ML Q8："TrueSkill 对 8 人对局给出的观察收敛约为 10 局（信息论极限约 5 局/人）" | ML Q8 | CONFIRMED，但需补充语境：这只是"两名最高分玩家"的示例轨迹（"two exemplary convergence trajectories"），**不是平均值**。LIT/ML 中"Elo 定级约 20 局"取自原文 "provisional … say, 20 games"，是举例，不是规定 | 高 |
| F2 | Graepel & Herbrich，"Ranking and Matchmaking"，*Game Developer Magazine* 2006 | LIT Q3 | CONFIRMED（MSR 镜像 PDF 可读，共 10 页） | 高 |

---

## 二、详细说明（按主题）

### 1. TrueSkill（Herbrich, Minka, Graepel, NIPS 2006）
- 来源：https://www.microsoft.com/en-us/research/wp-content/uploads/2007/01/NIPS2006_0688.pdf （本次直接下载，共 8 页）。第 6、7 页渲染成图片核对。
- **表格**（第 6 页，四列依次为 ELO full / TrueSkill full / ELO challenged / TrueSkill challenged，粗体为原表加粗）：

  | 模式 | ELO full | TrueSkill full | ELO challenged | TrueSkill challenged |
  |---|---|---|---|---|
  | FFA | 32.14 | **30.82** | 38.30 | **35.64** |
  | Small Teams | **34.92** | 35.23 | 42.55 | **37.17** |
  | Head to Head | 33.24 | **32.44** | 40.57 | **30.83** |
  | Large Teams | 39.49 | **38.15** | 44.12 | **29.94** |

  与 LIT 完全一致。挑战集 "was always 20% of the total number of games in each game mode"。
- **α 与 K**：原文 "We compared the TrueSkill algorithm to Elo with a Gaussian performance distribution (1) and **α = 0.07**; this corresponds to a K factor of 24 on the Elo scale which is considered a good and stable dynamics"。ML Q1 写作 β=0.07 是笔误。在 TrueSkill 中 β 是表现噪声参数，混用会误导读者。
- **胜率与公平性**（第 7 页）：原文 "measured the average deviation of the winning probability from 50% (the 'optimal' winning ratio). The resulting plot on the right (for the 'Head to Head' game mode) shows that with TrueSkill ever[sic] players with very few games got mostly fair matches (with a winning probability within 35% to 65%)"。前提是 "rejected games that did not meet a certain match quality threshold"。图中 TrueSkill 的平均偏离约 14 个百分点，Elo 约 20–25。
- **匹配质量**："is performed using a match quality criterion derived as the draw probability relative to the highest possible draw probability in the limit ε → 0"。原文还承认，在 Small Teams 模式下 TrueSkill 的匹配质量排序不如 Elo，"possibly due to the violation of the additive team performance model as most games in this mode are Capture-the-Flag games"。**这是 TrueSkill 作者自己承认"求和聚合"假设在团队模式中失效**，可以直接加强 LIT Q2/Q5 关于车队和求和假设的论证。
- **收敛**："TrueSkill automatically chooses the correct learning rate whereas Elo only slowly converges to the target skill … For 8 player games, the information theoretic limit is log(n)/log(8) ≈ 5 games per player on average and the observed convergence for these two players is ≈ 10 games!"。注意"10 局"只针对两名示例玩家。
- **历史与数据**："In 1959, Arpad Elo developed a statistical rating system for Chess, which was adopted by the World Chess Federation FIDE in 1970"；数据 "generated by Bungie Studios during the beta testing of the Xbox title Halo 2"。
- **书目**：MSR 出版物页写的是 "Advances in Neural Information Processing Systems 20 | January 2007"，但 NIPS 2006 论文集是第 19 卷，pp.569–576（papers.nips.cc 2006 年目录、mlanthology、Herbrich 主页三处一致）。**报告应引作 NIPS 19。**

### 2. TrueSkill FAQ（MSR 项目页，直接抓取）
- https://www.microsoft.com/en-us/research/project/trueskill-ranking-system/
- 逐字："Interestingly, every match-made game where the game outcome is not predictable ahead of time ensures that the game is informative!"
- 逐字："In general, with t teams of p players in each team, one game outcome provides log2(t!) bits but it needs t*p players per game so in the most general case, the system needs t*p*log2(n)/log2(t!) many games per player."
- 补充原文："Each game is not providing 1 bit of information because the best player does not always win … This can eventually lead to the loss of 75% of the information per game!"
- "The primary purpose of the TrueSkill system is to minimize the number of games necessary to find out a gamer's skill in order to optimize matchmaking."；"The TrueSkill value is then μ-3*σ"。

### 3. TrueSkill 2（Minka, Cleven, Zaykov, 2018）
- PDF：https://www.microsoft.com/en-us/research/uploads/prod/2018/03/trueskill2.pdf （PDF 日期 2018-03-22）；出版物页注明 "MSR-TR-2018-8 | March 2018"。作者单位：Minka、Zaykov 为 MSR，Cleven 为 The Coalition。
- 摘要原文："TrueSkill2 predicts historical match outcomes with 68% accuracy, compared to 52% accuracy for TrueSkill."
- **准确率的定义**："we only ask the model to predict the identity of the winning team, or predict 'draw' when there is a tie for first place. Thus the number of options is the number of teams plus 1." 预测时只用队伍组成和车队信息。按时间顺序先预测、后在线更新，即 prequential 方式。训练集 2300 万局，测试集其后 300 万局；"no need to report error bars … since they are tiny"。
- **车队表**（经典 TrueSkill 预期）：1:47/47，2:50/50，3:50/50，4:57/52，5:53/49，6:56/48，7:62/49，8:68/49，9:70/54，≥10:89/67。原文："the assumption about squads is false. The skill rating of a squad should be larger than the sum of its players, and the effect grows with the size of the squad … some playlists in Halo 5 and Gears of War 4 prohibit large squads"。加入车队偏移后，TrueSkill2 的预期为 46/51/50/57/53/54/59/61/66/87。注意原文第二张表中 6 人组实际胜率印作 55，与第一张表的 56 不一致，是原文自身的小矛盾。
- **激励与 shift ambiguity**：ML Q2/Q3 的转述正确（"if we add 2 to all skills, then the distribution over outcomes is the same"；"The incentive should be to play the game well, not to queue up at particular times of day or with particular teammates"）。
- **Gears of War 4**：自 2016 年发售起使用 TrueSkill2；赛季前用 TrueSkill Through Time 批量重算；bot 按难度视为实力恒定的"玩家"。

### 4. 书目类关键更正与补全
- **B4 NIPS 卷号**：见上文第 1 节。
- **B11 Bertrand et al.**：确有其文。PMLR 206:2905–2921（AISTATS 2023），arXiv 2206.12301（2022-06）。结论是 Elo "can fail to extract this transitive component, even in elementary transitive games"，并提出 disc ranking，给每名玩家 skill 和 consistency 两个分数。LIT 可以删去"未核验"标记。
- **B12 arXiv 2502.10985**：Tang, Wang, Jin（Princeton），"Is Elo Rating Reliable? A Study Under Model Misspecification"。似然比检验在多数真实数据集上拒绝 BT 模型，但 Elo 预测仍常优于 mElo 和 pairwise 模型。作者给的解释有三：(1) Elo = 在线梯度下降，在设定有误和非平稳情形下有 sublinear regret；(2) 真实数据的稀疏性；(3) 预测精度与排名表现强相关。LIT 中"任意匹配下即使传递也可能给不出一致排序"一句没有找到依据。
- **B13 Szczecinski & Djebbi**：INRS（蒙特利尔）。期刊版为 *JQAS* 2020, 16(3):211–220，题为 "Understanding draws in Elo rating algorithm"。据摘要，Elo 隐含假设平局率为 50%。TalkChess 上有人质疑其新颖性（非同行评审意见）。
- **B9 / B18**：Balduzzi 2019（PMLR 97:434–443）与 α-Rank（*Sci. Rep.* 9:9937，2019-07-09）都确认无误，ML 可以去掉"未核实"。
- **B16 TTT**：NIPS 20 (2007) pp.931–938，用约 350 万局、跨 150 年的数据，发现总体棋力随时间上升。这与 Regan & Haworth 的"无评分通胀"并不矛盾：前者估计跨时代的绝对棋力，后者检验同一评分对应的走子质量是否随年代漂移。

### 5. 匹配研究：数字补全与澄清
- **EOMM 的效应量**：据 arXiv 1702.06820 正文，经检索摘要转引。原文："The improvement of EOMM over SkillMM … in terms of the average number of retained players are 0.3%, 0.9%, 1.1%, and 0.6% when P=200, 300, 400 and 500 respectively. On average EOMM retains 0.7% more player compared with SkillMM after one round of matchmaking." 然后外推 "1.007^20≈1.15"，即 8 小时内多留存 15%。P=100 时不显著优于 RandomMM，且留存少于 SkillMM。**报告引用时应写"仿真中每轮 +0.7%"，不宜写"留存 +15%"。**
- **Chen–Elmachtoub–Lei**：INFORMS 新闻稿（https://www.informs.org/News-Room/INFORMS-Releases/News-Releases/Smarter-Matchmaking-Not-Just-Equal-Skill-Could-Keep-Millions-More-Gamers-Playing-Study-Finds）写明 "5.4 million matches from the online chess platform Lichess … increased engagement by 4% to 6%"，理论情形下最高 +50%。论文摘要另一版本写 "improve engagement by 4%–6% or reduce the percentage of bots by 3%"。EC'22 → *Management Science*，DOI 10.1287/mnsc.2023.02957。
- **Heliyon 2024**：Kang, Suh（Netmarble）, Kim（高丽大学），*Heliyon* 10(3):e24891，DOI 10.1016/j.heliyon.2024.e24891。数据为 *Everybody's Marble*（모두의마블）的 42 天服务器日志，约 600 万场、26.2 万+ 玩家，用双向固定效应模型。主表系数（经检索摘要读出，未见原表）：连胜率 −0.0104（显著）；连败率 0.0001（不显著）；胜率 −0.0037（显著）。**结论：连胜降低流失，没有证据表明连败增加流失**；对上更强对手增加流失。这一点直接关系到第 3 部分"连败导致流失"的论证。
- **QuickSkill**：MSR 出版物页（https://www.microsoft.com/en-us/research/?p=890235）显示发表于 "Conference on Information and Knowledge Management | October 2022"，作者 Chaoyun Zhang, Kai Wang, Hao Chen, Ge Fan, Yingjie Li, Lifang Wu, Bingchao Zheng。摘要写的是 "a popular mobile multiplayer game"、"significantly lower team skill disparities"，没有"20%"。这同时回答了 LIT Q6 的缺口：QuickSkill 与 CUPID 都有腾讯背景（CUPID 作者来自腾讯、微软、字节跳动、深大、哈工大深圳）。

### 6. ML 训练部分
- **OpenAI Five**（arXiv 1912.06680 Appendix J，经检索摘要）：参考池共 83 个智能体，TrueSkill 从 0（随机）到 254（击败世界冠军的版本）。μ 对齐到随机智能体为 0。评估时参考智能体评分固定，"After 750 games have been reported, the version's TrueSkill is logged"。"8.3 TrueSkill ≈ 80% winrate"。评估匹配会避开相差 10 分以上（胜率 <15% 或 >85%）的对手。**这是"只与胜率不太极端的对手对局才有信息量"在 AI 训练中的实例，可以加强 ML Q3 的论证。**
- **80/20**：OpenAI 官方博客 "OpenAI Five" 原句："To avoid 'strategy collapse', the agent trains 80% of its games against itself and the other 20% against its past selves."
- **PFSP**：DI-engine 源码（https://raw.githubusercontent.com/opendilab/DI-engine/main/ding/league/algorithm.py）直接读到 `'squared': lambda x: (1 - x) ** 2, 'variance': lambda x: x * (1 - x)`，与 ML 一致。AlphaStar 原文中 f_hard = (1−x)^p 的定义只有二手来源（综述 2408.01072；FootsiesGym 称 "following Vinyals et al. (2019) … (1 − p̂_i)^{1/2}"）。另一检索摘要凭记忆说 f_hard 是"胜率 <30% 的硬截断"，与上述来源冲突且没有任何出处，不采信。
- **AlphaGo Zero**：精确 Elo 为 Zero 5185、Master 4858、Lee 3739、Fan 3144。55% 门槛（400 局）有两个二手来源。BayesElo 与 c_elo = 1/400 在 AlphaZero 论文（arXiv 1712.01815）中明确写出，并锚定外部引擎的公开评分。
- **Chatbot Arena**：LMSYS 2023-12-07 博文（arena.ai 镜像为 12-08）"transition from the online Elo system to the Bradley-Terry model, which gives us significantly more stable ratings and precise confidence intervals"。"在线 Elo 依赖顺序"的说法有多个二手来源支持，与 Elo Uncovered 的结论一致。
- **Leela**：维基条目经检索摘要的原句见 M9。另有用户博客称 Test 60 网络自博弈 Elo 约 2900，而早期 Test 71.4 已接近 4000，可作为"跨 run 不可比"的例证（非正式来源）。

### 7. 电竞预测数字
- **E3 1701.03162**：摘要原句为 "accuracy … from 58.69% to 71.49%" when adding more prior features。ML 写的"仅英雄 60.07%"没有出处，应改为 58.69%（起点特征集）。
- **E2 Song 2015**：只能证实"hero lineup alone does not predict the game result well enough"。58%/61% 两个数字找不到来源，建议删除或标为未核实。
- **E4**：Yashkov 幻灯片（MLSA16）写 AUC 约 0.66–0.70，并有"阵容在极高分段只解释约 6% 的信息，普通分段约 10%"，支持"分段越高越难预测"。原论文为 Semenov, Romov, Korolev, Yashkov, Neklyudov, AIST 2016（CCIS，2017 年出版）。
- **E5**：DBLP 显示 FDG'21 pp.46:1–46:5。原文："75.1% accuracy after all players have selected champions, which occurs before gameplay begins"。

---

## 三、笔记中缺失、但会实质加强或修正报告的事实

1. **TrueSkill 作者自认求和团队模型失效**（NIPS 2006，第 7 页）：Small Teams（多为夺旗）模式下匹配质量不如 Elo，"possibly due to the violation of the additive team performance model"。这比单独引用 TrueSkill 2 的车队表更早、更直接。
2. **EOMM 的真实效应量很小**：每轮留存仅多 0.3–1.1%（平均 0.7%）；"15%"是复利外推；小等待池（P=100）时无效甚至更差。这能显著修正"EOMM 效果大"的印象。
   — 来源：arXiv 1702.06820（经检索摘要转引原句）
3. **Heliyon 2024 中连败对流失不显著，连胜显著降低流失**。这与"连败导致流失、所以系统要安排连胜"的流行叙事不同：数据支持的是"赢能留人"，不支持"输会赶人"。
   — 来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10839887/ （经检索摘要）
4. **Aldous (2017)** 明确质疑流行的"30 局就够收敛"说法："a much-copied '30 matches suffice' claim, which our simulation study casts doubt upon"。这与 FIDE"前 30 局 K=40"、游戏定级赛的设计直接相关。
   — 来源：https://www.stat.berkeley.edu/~aldous/Papers/me-Elo-SS.pdf ，DOI 10.1214/17-STS628
5. **FIDE 2024 年反通缩调整**：2024-03-01 起，2000 分以下按 新分 = 旧分 + 0.4×(2000 − 旧分) 一次性上调，评分下限从 1000 提到 1400（Sonas 提案，原定 2024-01，后推迟）。此外 K×局数 ≤ 700。这能填补 LIT Q1/Q5 的缺口，也是"封闭池通缩真实存在、需要人工干预"的实证。
   — 来源：https://new.uschess.org/sites/default/files/media/documents/4-15-2024-rc-report-24-mm-eedit.pdf ；https://www.chess.com/news/view/fide-set-to-implement-drastic-rating-changes ；https://fide.com/news/2538
6. **Elo 收敛理论的新文献**：
   - Olesker-Taylor & Zanetti，"An Analysis of Elo Rating Systems via Markov Chains"，NeurIPS 2024（arXiv 2406.05869）：在 BTL 模型下，时间平均且截断后的 Elo 以接近最优的速率学到参数，并把对局设计与比较图谱隙（fastest-mixing Markov chain）联系起来。
   - Szczecinski 2026，"New insights into Elo algorithm for practitioners and statisticians"（arXiv 2604.03840）：Elo = 通过随机梯度上升做在线最大似然；给出 K 和标度 s 如何决定估计噪声与收敛速度的闭式结果。
   - 两者都直接支持 LIT/ML 的"Elo = SGD，K = 学习率"推导，可以替代"推导为我独立完成"的表述。
7. **OpenAI Five 的评估匹配**刻意避开胜率 <15% 或 >85% 的对手，并给出"8.3 TrueSkill ≈ 80% 胜率"的标定。这是 AI 训练中"有信息量的对局在 50% 附近"的工程实例。
8. **Elo Uncovered（2023）**：胜率接近 0.5 时 Elo 波动最大；需要 ≥100 次顺序置换取平均才稳定；模型相近时传递性不成立。这为"收敛后评分仍在 ±K/2 抖动"（ML Q3）提供了跨领域实证。
9. **Bertrand et al. (AISTATS 2023)**：Elo 甚至在简单传递博弈中也可能失败（"transitive, not additive"），并提出 skill + consistency 两维评分。对"单一 MMR 能否刻画酒馆战棋"一类讨论有直接意义。
10. **Yuksel 2024 的作者单位含 Roblox**：说明"目标胜率匹配（抑制连胜连败）"有业界背景，不只是学术提案。

## 四、给报告撰写者的修改清单（按优先级）
1. ML Q1：把 "β=0.07" 改为 "α=0.07"。
2. LIT Q2：TrueSkill 统一引作 "NIPS 19 (2006), pp.569–576"。
3. LIT Q3：Heliyon 一条改为"约 600 万场、26.2 万玩家；连胜降低流失，连败不显著"，删除"2700 万"和"方向冲突"的说法。
4. LIT Q3 / ML Q7：EOMM 补上"每轮 +0.7%（仿真）；15% 为外推"。
5. ML Q4：1701.03162 的起点改为 58.69%；Song 2015 的 58%/61% 删除或标为未核实。
6. LIT Q2：删除对 2502.10985 "任意匹配下不一致排序"的转述，或标为未核实；补上作者。
7. LIT Q2：Bertrand 2023、Balduzzi 2019、α-Rank 去掉"未核验"标记。
8. ML Q5：AlphaGo Lee 写 3739；DeepMind"只为赢而下是不够的"不要加引号。
9. LIT Q3：QuickSkill 改为 CIKM 2022、"手机多人游戏"，"20%"标为未核实。
10. 引用 TrueSkill 2 的 52% 时，注明它是"预测获胜队或平局"的多选准确率。

## 五、主要来源
- TrueSkill PDF：https://www.microsoft.com/en-us/research/wp-content/uploads/2007/01/NIPS2006_0688.pdf （直接读取）
- TrueSkill 2 PDF：https://www.microsoft.com/en-us/research/uploads/prod/2018/03/trueskill2.pdf （直接读取）
- MSR TrueSkill 项目页：https://www.microsoft.com/en-us/research/project/trueskill-ranking-system/ （直接读取）
- MSR 出版物页（TrueSkill / TrueSkill 2 / QuickSkill）：https://www.microsoft.com/en-us/research/publication/trueskilltm-a-bayesian-skill-rating-system/ ，https://www.microsoft.com/en-us/research/publication/trueskill-2-improved-bayesian-skill-rating-system/ ，https://www.microsoft.com/en-us/research/?p=890235
- Graepel & Herbrich，Game Developer：https://microsoft.com/en-us/research/wp-content/uploads/2006/10/Game-Developer-Feature-Article-Graepel-Herbrich.pdf
- DI-engine PFSP：https://raw.githubusercontent.com/opendilab/DI-engine/main/ding/league/algorithm.py
- NIPS 2006 卷号：https://mlanthology.org/neurips/2006/herbrich2006neurips-trueskilltm ；https://hpi.de/herbrich/publications/2006.html
- Bertrand et al.：https://proceedings.mlr.press/v206/bertrand23a.html
- Tang–Wang–Jin：https://arxiv.org/abs/2502.10985
- Szczecinski & Djebbi：https://arxiv.org/abs/1910.06081 ；https://ideas.repec.org/a/bpj/jqsprt/v16y2020i3p211-220n5.html
- EOMM：https://arxiv.org/pdf/1702.06820
- INFORMS 新闻稿（Chen–Elmachtoub–Lei）：见第二节第 5 小节
- Heliyon：https://pmc.ncbi.nlm.nih.gov/articles/PMC10839887/ ；https://pubmed.ncbi.nlm.nih.gov/38318006
- Regan & Haworth：https://ojs.aaai.org/index.php/AAAI/article/view/7951
- Kaggle 2010：https://arxiv.org/abs/1012.4571 ；https://heliosphan.org/kagglechessratingscomp.html
- EA DDA：https://archives.iw3c2.org/www2017/proceedings/companion/p465.pdf
- FIDE 规章（中文版）：https://cn.fide.com/wp-content/uploads/2025/09/B02-国际棋联等级分条例-FIDE-Rating-Regulations-CHN.pdf
- OpenAI Five 论文：https://cdn.openai.com/dota-2.pdf ；博客：https://openai.com/index/openai-five/
- AlphaGo Zero 评分：https://blog.acolyer.org/2017/11/17/mastering-the-game-of-go-without-human-knowledge/
- AlphaZero BayesElo：https://arxiv.org/pdf/1712.01815
- LMSYS 博文：https://lmsys.org/blog/2023-12-07-leaderboard/
- Christiano 2017：https://arxiv.org/abs/1706.03741
- 电竞预测：https://arxiv.org/abs/1701.03162 ；https://arxiv.org/abs/2108.02799 ；https://dblp.dagstuhl.de/db/conf/fdg/fdg2021.html ；https://dtai.cs.kuleuven.be/events/MLSA16/slides/05_Daniil_Yashkov.pdf
- Elo 理论：https://proceedings.neurips.cc/paper_files/paper/2024/hash/f9db8bd38c36391ddc4ccc0d23effdbe-Abstract.html ；https://arxiv.org/abs/2604.03840 ；https://aclanthology.org/2023.gem-1.28.pdf
