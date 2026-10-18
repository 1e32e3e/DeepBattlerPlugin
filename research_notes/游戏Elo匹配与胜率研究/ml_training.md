# 第 4 部分：Elo 与机器学习模型训练 —— 学习目标是“胜率”还是“实力”？收敛后胜负数据长什么样？

> 研究说明（给报告撰写者）：
> - 本会话中 arXiv / Nature / JMLR / NeurIPS / Wikipedia 等站点的直接抓取被出口代理拒绝（HTTP 403），因此大部分事实来自 WebSearch 摘要并给出权威原始 URL；**唯一能直接读取原文的是 Microsoft Research 的 TrueSkill 页面与 TrueSkill / TrueSkill 2 论文 PDF**（下文凡标注“原文”者均为逐字核对过的内容）。
> - 凡是我自己推导或推理的内容，均放在各节 “Inferences” 中并标注【推导】或【推理】，与已发表结论分开。
> - 术语对照：skill / rating = 实力（潜变量）；win probability = 胜率（模型输出/预测）；outcome / label = 胜负结果（训练标签）；log-loss = 对数损失；Brier score = 布里尔分数；calibration = 校准。

---

## Q1. Elo 本身就是一个机器学习算法：Elo 更新 = 对 Bradley–Terry/逻辑回归对数损失做一步随机梯度下降（K = 学习率）；Glicko / TrueSkill = 贝叶斯在线推断

### Takeaway
Elo 的更新公式 R ← R + K(S − E) 恰好是“以胜负为标签、以评分差的 logistic 函数为预测胜率”的对数损失上的一步在线随机梯度下降（SGD），K 就是（带尺度系数的）学习率；TrueSkill 则把同一个问题当作贝叶斯推断，用高斯假设密度滤波（ADF）/期望传播（EP）在因子图上在线更新“实力的均值 μ 与不确定度 σ”，相当于自动调节学习率。

### Cited Findings
- Szczecinski & Djebbi 将 Elo 形式化为随机梯度：最速下降解假设实力恒定，而 Elo 只对“最新一场比赛”计算梯度并执行一步更新，写作“旧评分 + 步长 × 特征向量 × (实际结果 − 预测胜率)”，步长吸收了导数中的常数因子；文中还指出 Elo 隐含了一个特定的平局模型并提出 κ-Elo 扩展 — [Szczecinski & Djebbi, *Understanding and Pushing the Limits of the Elo Rating Algorithm*, arXiv:1910.06081](https://arxiv.org/abs/1910.06081)
- DeepMind 的 Soft Condorcet Optimization 论文同样推导：利用 σ′(x)=σ(x)(1−σ(x))，单场对数损失的梯度为 (σ(θᵀx_k) − y_k)·x_k，i 胜 j 时把更新量加到 θ_i、从 θ_j 减去，即 Elo 更新对应标准负对数似然损失 — [Lanctot et al., *Soft Condorcet Optimization for Ranking of General Agents*, arXiv:2411.00119](https://arxiv.org/abs/2411.00119)
- 2025 年的论文把 Elo 重新解释为在线梯度下降（online gradient descent），并给出 no-regret（无悔）保证 — [arXiv:2502.10985](https://arxiv.org/abs/2502.10985)
- Zanco、Szczecinski 等对 Elo 在循环赛中的收敛做了随机分析，结论与步长（K）有关，并用排球数据检验 — [*Stochastic analysis of the Elo rating algorithm*, arXiv:2212.12015](https://arxiv.org/abs/2212.12015)
- 开源 Python 包 EloGrad 直接把 Elo 实现为“用 SGD 训练的逻辑回归”，并引用 stmorse 博客作为推导参考（该博客本会话无法打开，内容未核实） — [EloGrad on PyPI](https://pypi.org/project/elo-grad/)；[stmorse 博客](https://stmorse.github.io/journal/Elo.html)
- TrueSkill 原文（逐字核对）：自称是“Elo 系统的推广”，“跟踪玩家实力的不确定性、显式建模平局、可处理任意数量参赛方、可从团队结果推断个人实力”；“推断通过因子图上的近似消息传递完成”；为了每场后都能报告实力，采用称为 **Gaussian density filtering**（高斯密度滤波，即 assumed-density filtering）的在线学习方案：后验被近似为高斯并作为下一场的先验 — [Herbrich, Minka & Graepel, *TrueSkill™: A Bayesian Skill Rating System*, NIPS 2006（MSR 页面）](https://www.microsoft.com/en-us/research/publication/trueskilltm-a-bayesian-skill-rating-system/)
- TrueSkill 原文：在 Halo 2 实验中，作为对照的 Elo 取 β=0.07，“对应 Elo 尺度上 K=24”；TrueSkill “自动选择正确的学习率，而 Elo 只能缓慢收敛到目标实力” — [TrueSkill NIPS 2006](https://www.microsoft.com/en-us/research/publication/trueskilltm-a-bayesian-skill-rating-system/)
- TrueSkill 2 原文：该模型“特别适合期望传播（Expectation Propagation）[Minka 2001]”；用 Infer.NET 自动生成 EP 代码；区分只向前传播的 online（在线）模式与 batch（批量）模式，“在线 TrueSkill 更新是对后验的快速实时近似” — [Minka, Cleven & Zaykov, *TrueSkill 2*, MSR-TR-2018-8](https://www.microsoft.com/en-us/research/publication/trueskill-2-improved-bayesian-skill-rating-system/)
- Weng & Lin (JMLR 2011) 提出一种在线排名的贝叶斯近似方法，适用于多队多人对局，关键词含 Bradley–Terry、Thurstone–Mosteller、Plackett–Luce；通过近似团队/玩家表现的期望得到解析更新规则、免去数值积分；准确率与 TrueSkill 相当而运行更快、代码更短（这是 OpenSkill 等开源库的理论基础） — [Weng & Lin, *A Bayesian Approximation Method for Online Ranking*, JMLR 12:267–300](https://jmlr.org/papers/v12/weng11a.html)
- LMSYS 指出在线 Elo 的最终评分依赖比赛顺序（最近的比赛权重更大，打乱顺序会得到不同数值），因此 Chatbot Arena 改用对全部对局联合拟合的 Bradley–Terry 最大似然 — [LMSYS 博客 2023-12-07](https://lmsys.org/blog/2023-12-07-leaderboard/)

### Inferences
- 【推导：Elo = SGD】设 A 对 B 的预测胜率 p = E_A = 1/(1+10^{(R_B−R_A)/400}) = σ(c·(R_A−R_B))，其中 c = ln10/400 ≈ 0.005756，σ 为 logistic 函数。以实际得分 y∈{0, ½, 1} 为标签，单场交叉熵（对数损失）ℓ = −[y ln p + (1−y) ln(1−p)]。由 σ′=σ(1−σ) 得 ∂ℓ/∂R_A = −c(y−p)，∂ℓ/∂R_B = +c(y−p)。以学习率 η 做一步 SGD：R_A ← R_A + ηc(y−p)，R_B ← R_B − ηc(y−p)。令 K = ηc，即得 Elo 公式 R_A ← R_A + K(S_A − E_A)。因此：**Elo 的“训练标签”是胜负，“模型输出”是胜率 E，“被学习的参数”是评分 R；K 就是学习率。**
- 【推理】在线 SGD 用恒定学习率时，参数不会收敛到一个点，而是在最优点附近的“噪声球”里游走；且越近的样本权重越大（指数遗忘）。这正是 LMSYS 观察到的“顺序依赖”，也是 Elo 能“跟踪”实力变化的原因——它更像一个跟踪滤波器而非一次性的批量估计。TrueSkill 用 σ 自适应学习率（新玩家 σ 大→步长大；老玩家 σ 小→步长小），并通过动态方差 τ 防止 σ 收缩到 0，从而保持跟踪能力。
- 【推理】Glicko（Glickman 1999）在同一谱系中属于“近似贝叶斯更新 + 评分偏差 RD”，可视为 TrueSkill 的两人特例的前身；本会话未检索其原文（见 Gaps）。

### Gaps
- 未能打开 stmorse 博客与 Szczecinski 论文全文（arXiv 被拒），上面关于 1910.06081 的表述来自搜索摘要；推导部分为我独立完成，与摘要所述一致。
- Glicko 原始论文（Glickman 1999, *Applied Statistics* 48:377–394，作者主页 glicko.net）未在本会话核实。

---

## Q2. 学习目标（target）与潜变量（latent）：标签是胜负，输出是胜率，“实力”是被学到的潜参数；如何评估评分系统；为何实力只在“加一个常数”与“相对于对手池”的意义下可辨识

### Takeaway
在 Bradley–Terry / logistic 模型里，训练数据只有胜负（0/1），模型预测的是胜率，“实力”只是让预测胜率尽量贴合胜负的中间参数；因此评估评分系统必须看“预测胜率 vs 实际胜负”（准确率、对数损失、Brier 分数、分组校准），而实力的绝对数值没有意义——给所有人同时加一个常数，预测完全不变，实力只在同一对手池内相对可比。

### Cited Findings
- TrueSkill 2 原文：“在两人游戏中，模型存在**平移不确定性（shift ambiguity）**：若给所有实力都加 2，结果的分布完全相同”，因此先验均值 m0 在这类游戏中无关紧要 — [TrueSkill 2](https://www.microsoft.com/en-us/research/publication/trueskill-2-improved-bayesian-skill-rating-system/)
- TrueSkill 2 原文：评估原则是“**指标应位于数据空间，或更一般地位于模型的外部接口，而不是参数空间**”；对生成式对局模型，核心指标是对最终名次的预测能力，称为 predictive accuracy；为得到易计算的指标，只让模型预测获胜队伍（或平局）— [TrueSkill 2](https://www.microsoft.com/en-us/research/publication/trueskill-2-improved-bayesian-skill-rating-system/)
- TrueSkill 2 原文：除准确率外，还比较“模型认为某类队伍/玩家会赢的频率”与“实际赢的频率”（即分组校准）。例：按组队人数分组，单排玩家实际胜率 47%、TrueSkill 预期 47%；4 人组实际 57% vs 预期 52%；≥10 人组实际 89% vs 预期 67%——说明“队伍实力=成员实力之和”的假设错误 — [TrueSkill 2](https://www.microsoft.com/en-us/research/publication/trueskill-2-improved-bayesian-skill-rating-system/)
- TrueSkill 2 原文：评估流程为按时间顺序逐场处理测试集，**先**用赛前信息预测胜方并给出概率，**再**用赛后信息在线更新实力（prequential / 先预测后学习的评估）；训练集 2300 万场、测试集其后 300 万场 Halo 5 对局 — [TrueSkill 2](https://www.microsoft.com/en-us/research/publication/trueskill-2-improved-bayesian-skill-rating-system/)
- TrueSkill 原文（项目页）：TrueSkill 用保守估计 μ − k·σ 来排排行榜 — [MSR TrueSkill 项目页](https://www.microsoft.com/en-us/research/project/trueskill-ranking-system/)
- 板球研究用适当评分规则（proper scoring rules）比较 Elo 与 Glicko：Elo（K 调到使 Brier 最小）在 WTC 2021–23 周期 Brier = 0.1896、log-loss = 0.6570；未改进的 Glicko 为 Brier 0.2050、log-loss 0.6889，并被作者评为校准较差 — [arXiv:2603.02574](https://arxiv.org/abs/2603.02574)
- Dehpanah 等对 10 万+ 场多人自由混战（free-for-all）对局评估 6 种评分系统评估指标，发现一些指标不考虑名次间的偏差、受新玩家影响过大、不区分高名次与低名次的错误，推荐使用可调的 NDCG — [Dehpanah et al., *The Evaluation of Rating Systems in Online Free-for-All Games*, arXiv:2008.06787](https://arxiv.org/abs/2008.06787)
- 同组作者在 PUBG 团队大逃杀数据上评估三种流行评分系统，指出新玩家的引入会显著降低评分系统表现 — [arXiv:2105.14069](https://arxiv.org/abs/2105.14069)；第三方转述见 [*Skill Issues: An Analysis of CS:GO Skill Rating Systems*, arXiv:2410.02831](https://arxiv.org/abs/2410.02831)

### Inferences
- 【推理：三层结构】可以把评分系统看成一个三层模型：
  1. **观测/标签层**：胜负 y（或名次）。这是唯一真正“被观测到”的东西。
  2. **预测层**：胜率 p = σ(c·(R_A − R_B))。这是模型的输出，也是损失函数比较的对象。
  3. **潜变量层**：实力 R。它只是使预测贴合标签的参数，本身不被观测，也不被直接“优化”。
  所以“训练目标是胜率还是实力？”的精确回答是：**损失函数优化的是“预测胜率对实际胜负的拟合程度”；实力是这一优化的副产品（被估计的潜参数）；胜率本身则是模型的输出，而不是目标值。**
- 【推导：可辨识性】预测只依赖差值 R_A − R_B，所以 (R + C) 与 R 给出完全相同的似然，实力只能确定到一个加性常数；此外 logistic 尺度（400/ln10）也是人为约定。Elo 每场更新零和（ΔR_A = −ΔR_B），所以在玩家池封闭时所有评分之和守恒——常数由“初始分”锚定。由此：(a) 一个 1500 分在 A 游戏和 B 游戏、或在同一游戏的不同年份，都不可直接比较；(b) 评分是“相对于你实际碰到的对手池”的；新玩家涌入、老玩家流失、赛季重置都会使“同一个数字”代表的绝对水平漂移。
- 【推理】正因为指标要在“数据空间”，所以“这个评分系统好不好”只能用“它预测胜负准不准、校准好不好”来回答，不能用“它给出的实力数字对不对”来回答（我们没有实力的真值）。
- 【推理】板球例子中 Elo 的 log-loss 0.657 只略低于“抛硬币”的 ln2 ≈ 0.693，说明即使是表现良好的评分系统，单场胜负的大部分不确定性也是不可约的（aleatoric）。

### Gaps
- 未找到对 Elo、Glicko、TrueSkill 在多个数据集上同时用 log-loss、Brier 与校准做严谨对比的权威综述；板球研究只是单一数据集。

---

## Q3. 收敛后的状态：模型“稳定”后还有胜负数据吗？胜负看起来像抛硬币；p(1−p) 在 p=0.5 时信息量最大

### Takeaway
当评分已收敛且匹配系统把评分相近的人配在一起时，模型对每局的预测胜率≈50%，胜负在模型看来就像抛硬币（准确率≈50%、log-loss≈ln2、Brier≈0.25）——但胜负数据仍然持续产生、持续驱动更新：它只通过“实际结果偏离预测”的残差 (y − p) 携带信息；而且恰恰是 50/50 的对局，对“相对实力差”的单局信息量（Fisher 信息 ∝ p(1−p)）最大。TrueSkill 的原始论文与官方 FAQ 明确把“胜率接近 50%”当作匹配做得好的标志，并指出在匹配系统下“可达到的最小预测错误率可能高达 50%”。

### Cited Findings
- TrueSkill 原文（Halo 2 实验）：预测错误率“难以解读，因为排名与匹配之间存在相互作用：**取决于所有玩家（未知的）真实实力，可达到的最小预测错误率可能高达 50%**”；为此作者让 Elo 与 TrueSkill 互相把自认为“最势均力敌”的对局拿给对方预测。全量预测错误率：自由混战 Elo 32.14% / TrueSkill 30.82%，1v1 Elo 33.24% / TrueSkill 32.44%，大团队 Elo 39.49% / TrueSkill 38.15%；在“互相挑战”的最胶着子集上 TrueSkill 错误率 29.94%–37.17%，Elo 38.30%–44.12% — [TrueSkill NIPS 2006](https://www.microsoft.com/en-us/research/publication/trueskilltm-a-bayesian-skill-rating-system/)
- TrueSkill 原文：“玩家感知的评分系统质量体现在其胜率上：**如果胜率高，说明系统错误地给他分配了过弱的对手**（反之亦然）”；作者统计每个玩家胜率偏离 50%（“最优”胜率）的平均幅度，显示 TrueSkill 下即使对局很少的玩家也基本获得公平对局（胜率在 35%–65% 之内）— [TrueSkill NIPS 2006](https://www.microsoft.com/en-us/research/publication/trueskilltm-a-bayesian-skill-rating-system/)
- TrueSkill 官方 FAQ 原文：系统“试图确定 n 名玩家的正确排序，需要 log₂(n!) ≈ n·log₂(n) 比特信息”；若强者总赢，一局 1v1 提供 1 比特；“**有趣的是，每一局结果无法事先预测的匹配对局，都保证了这局是有信息量的！**”；一般情形下 t 队、每队 p 人的一局提供 log₂(t!) 比特；但“强者并不总赢”，个人表现波动越大，每局信息越少 — [MSR TrueSkill 项目页 FAQ](https://www.microsoft.com/en-us/research/project/trueskill-ranking-system/)
- TrueSkill 官方 FAQ 原文：“TrueSkill 系统的首要目的是**最小化识别玩家实力所需的对局数，以优化匹配**” — [MSR TrueSkill 项目页](https://www.microsoft.com/en-us/research/project/trueskill-ranking-system/)
- TrueSkill 项目页原文：把双方获胜机会非常不平衡的对局称为“无趣”（“很少有人喜欢一场赢不了或输不了的比赛”），把各方获胜机会相对均等的对局称为“有趣”；匹配质量用（重标度的）平局概率衡量，0 最差、1 最好，即使 μ 相同，σ 大也会使匹配质量明显小于 1 — [MSR TrueSkill 项目页](https://www.microsoft.com/en-us/research/project/trueskill-ranking-system/)
- TrueSkill 2 原文：经典 TrueSkill 在 Halo 5 测试集上的预测准确率仅 **52%**，TrueSkill 2 达到 68%（额外利用了玩家经验、组队、击杀数、退出倾向、其他模式实力等）— [TrueSkill 2](https://www.microsoft.com/en-us/research/publication/trueskill-2-improved-bayesian-skill-rating-system/)
- TrueSkill 2 原文：“由于基于实力的匹配，与高手对位的玩家本身更可能也是高手”；从统计上把这些相关性纳入模型会得到更好的实力估计，但 TrueSkill 刻意不这样做，因为会制造不良激励（“激励应当是把游戏打好，而不是挑时间段排队或挑队友”）— [TrueSkill 2](https://www.microsoft.com/en-us/research/publication/trueskill-2-improved-bayesian-skill-rating-system/)
- 伯努利变量方差 Var(Y)=p(1−p) 在 p=0.5 时最大；单次 Bradley–Terry 比较在双方实力相等时的 Fisher 信息为 1/4（以 logit 尺度计），实力差越大单次比较的信息越少 — [MetricGate Bradley–Terry 文档（二手，较弱来源）](https://metricgate.com/docs/bradley-terry-model)；BTL 模型 MLE 的 Fisher 信息矩阵同时依赖比较图的拓扑与胜率取值 — [Bong & Rinaldo, ICML 2022](https://proceedings.mlr.press/v162/bong22a.html)
- AlphaStar 一类的自博弈课程中，按胜率 x 选择对手的权重 f_var(x) = x(1−x) 在 50% 胜率处达到峰值，用于优先与“水平相当”的对手训练 — [A Survey on Self-play Methods in RL, arXiv:2408.01072](https://arxiv.org/abs/2408.01072)

### Inferences
- 【推导：收敛态的三个数】若一局的真实胜率为 p，且模型完全校准，则：期望准确率 = max(p, 1−p)；期望 log-loss = 二元熵 H(p) = −p ln p − (1−p) ln(1−p)；期望 Brier = p(1−p)。在 p = 0.5 时分别为 **50%、ln2 ≈ 0.693 nats（= 1 比特）、0.25**——这是“完美模型”在完美平衡对局上的下限，任何模型都无法更好。所以“收敛后胜负像抛硬币”不是模型失败，而是匹配目标达成的直接结果。
- 【推导：Fisher 信息】对评分差 d = R_A − R_B，单局对数似然对 d 的 Fisher 信息 I(d) = c²·p(1−p)，在 p=0.5 时取最大值 c²/4。直观上：实力悬殊的对局结果几乎是确定的（强者赢），赢了也不告诉你多少新东西；五五开的对局结果最“意外”，因而每局最能区分“A 略强”还是“B 略强”。**“最难预测”与“最有信息量”在这里是同一件事的两面**——前者说的是对结果 y 的预测，后者说的是对参数 d 的估计。这与 TrueSkill FAQ 的说法“结果无法事先预测的对局保证是有信息量的”一致。
- 【推导：收敛后仍有胜负、而且仍在更新】Elo 每局更新量 ΔR = K(y − p)。在 p = 0.5 时，每局恰好 ±K/2（K=32 时 ±16 分），期望为 0、但从不为 0。用线性化近似：设误差 e = R − R_true，则 e_{t+1} ≈ (1 − Kc·p(1−p))·e_t + K·ξ_t，Var(ξ)=p(1−p)，平稳方差 ≈ K²p(1−p) / (2Kc·p(1−p)) = **K/(2c)**。K=32 时约 2780，即评分在真实值附近有约 **±53 分**的标准差抖动（假设对手评分准确、只有自己在动）。±53 分对应胜率约 50% ± 7.5 个百分点。结论：恒定 K 的 Elo 永远不会“停在”真实实力上，收敛的意思是“在真实值附近随机游走”；胜负数据一直在产生、一直在推动评分（这也与恒定步长 SGD 的一般性质一致）。
- 【推导：要多少局才能看出小差距】在 p≈0.5 附近，dp/dd = c·p(1−p) ≈ 0.00144/分，即 1 分 Elo ≈ 0.144 个百分点胜率。N 局平均得分的标准误 ≈ 0.5/√N。要以 2 倍标准误分辨 5 分 Elo（0.72 个百分点）需 N ≈ 19,000 局；分辨 50 分 Elo（约 7.2 个百分点）仍需约 190 局。这解释了为什么在平衡匹配下，个人的胜负序列在几十局尺度上主要由随机性主导。
- 【推理：实力藏在哪里？】在收敛的匹配系统中，**你的胜率被匹配“钉”在 50% 附近，因此胜率几乎不携带关于你绝对实力的信息；实力体现在“系统给你匹配的对手有多强”——即你能对之打成 50% 的那个对手水平（你的评分）**。用户问题“收敛后还有没有胜负数据、是否能直接解释胜负情况”的回答是：有，且胜负仍在流入；但在模型眼中每局近似独立的硬币，胜负的“情况”（包括连胜连败）大多可由二项随机性解释；只有“实际偏离预测”的系统性残差（如你在进步、或模型遗漏了某个因素）才代表新信息。
- 【推理：50/50 是“相对于做匹配的那个模型”的】TrueSkill 在 Halo 5 上只有 52% 准确率，而 TrueSkill 2 用更多特征达到 68%，说明“用旧模型配出的 50/50 局”在更好的模型看来并不是 50/50——例如大组队实际胜率远高于预期。所以“胜负像抛硬币”只对**做匹配的那个模型**成立；只要模型遗漏了系统性因素（组队、英雄熟练度、掉线倾向、阵容克制等），更好的模型就能从同一批胜负数据里挖出可预测性。

### Gaps
- 未找到直接、权威地以“Fisher 信息 p(1−p) 在 50% 处最大”为论据论证匹配设计的同行评审文献（找到的是二手文档与 BTL 最优设计文献的旁证）；以上 Fisher 信息与稳态方差推导是我的独立推导。
- 未找到公开的、各大游戏官方披露的“收敛后玩家胜率分布”数据（例如有多少比例玩家长期胜率落在 48%–52%）。

---

## Q4. 电竞中用赛前信息预测胜负的模型能达到多高准确率？为什么平衡匹配给可预测性设了上限？

### Takeaway
在 Dota 2 中，只用双方阵容（英雄选择）的赛前模型准确率通常在约 58%–70%（AUC 约 0.66–0.70，且分段越高越难预测）；加入玩家/玩家×英雄特征可升到约 71%；英雄联盟用“玩家对所选英雄的熟练度”可在开局前达到约 75%；而 Halo 5 上仅用经典 TrueSkill 评分预测只有 52%。规律是：匹配系统已经把“它所用的那个实力指标”平衡掉了，剩余可预测性只来自匹配没有平衡的因素。

### Cited Findings
- Conley & Perry（Stanford CS229, 2013）：仅用阵容的逻辑回归在约 1.8 万场训练数据上测试准确率约 69.8%；他们指出线性模型无法捕捉英雄间协同/克制 — [Conley & Perry 2013](https://cs229.stanford.edu/proj2013/PerryConley-HowDoesHeSawMeARecommendationEngineForPickingHeroesInDota2.pdf)
- Song 等（Stanford CS229, 2015）：结论更悲观——“仅凭英雄阵容不足以预测比赛结果”；后续综述转述其最佳逻辑回归约 58%，加入英雄组合特征约 61% — [Song et al. 2015](https://cs229.stanford.edu/proj2015/249_report.pdf)；综述见 [*Machine learning models for DOTA 2 outcomes prediction*, arXiv:2106.01782](https://arxiv.org/abs/2106.01782)
- 实时电竞结果预测论文：仅用英雄的逻辑回归 60.07%；加入玩家与“玩家-英雄”特征后升至 71.49%；作者认为早期更高的数字来自较短对局的数据集（数字据搜索摘要，未读全文）— [*Real-time eSports Match Result Prediction*, arXiv:1701.03162](https://arxiv.org/abs/1701.03162)
- Yashkov、Romov、Neklyudov、Semenov、Kireev 的报告：基于选人阶段数据的胜负预测 AUC 为 **0.66–0.70，随分段而变**（对应 Semenov et al. 2017 的研究，摘要中称越高分段越难预测；具体对应关系依据幻灯片摘要）— [MLSA16 幻灯片](https://dtai.cs.kuleuven.be/events/MLSA16/slides/05_Daniil_Yashkov.pdf)
- 混合分段 MOBA 胜负预测的相关研究 — [Hodge et al., *Win Prediction in Esports: Mixed-Rank Match Prediction in MOBA Games*, arXiv:1711.06498](https://arxiv.org/abs/1711.06498)
- 英雄联盟：基于“每位玩家对所选英雄的经验”的深度网络在所有人选完英雄、开局之前达到 **75.1%** 准确率；作者指出“即使经过基于实力的匹配，开局前两队实力仍存在很大差异” — [Do et al., *Using Machine Learning to Predict Game Outcomes Based on Player-Champion Experience in LoL*, FDG 2021, arXiv:2108.02799](https://arxiv.org/abs/2108.02799)
- 一些更高的报告值（如草稿数据上 MLP 88.63%、朴素贝叶斯+AdaBoost 80%）存在数据集问题（如 AI 填充队伍），不宜推广（据搜索摘要转述的综述）— [arXiv:2106.01782](https://arxiv.org/abs/2106.01782)
- Halo 5：仅用经典 TrueSkill 评分预测胜方准确率 52%；TrueSkill 2 加入更多信息后 68% — [TrueSkill 2](https://www.microsoft.com/en-us/research/publication/trueskill-2-improved-bayesian-skill-rating-system/)
- TrueSkill 原文：在匹配环境中“可达到的最小预测错误率可能高达 50%” — [TrueSkill NIPS 2006](https://www.microsoft.com/en-us/research/publication/trueskilltm-a-bayesian-skill-rating-system/)

### Inferences
- 【推理：可预测性上限的来源】若匹配器用评分 R 把双方配到预测胜率 50%，那么以 R 为唯一特征的任何模型都只能给出 ≈50%；可预测性只能来自 (a) R 的估计误差（新号、刚进步/退步的玩家、小号）、(b) 匹配器没有平衡的特征（阵容克制、英雄熟练度、组队、网络、掉线倾向）、(c) 匹配宽松（排队时间压力下放宽分差）。Dota 2 中阵容 ~60%、LoL 英雄熟练度 ~75%、Halo 5 评分本身 52%，都符合这一图景。
- 【推理】分段越高越难预测（AUC 0.70→0.66）与“高分段玩家水平更接近、阵容理解更对称、匹配池更小但评分更精确”一致，但具体原因未见论文直接论证（见 Gaps）。
- 【推理】对用户问题的意义：如果一个外部模型在某游戏里能用赛前信息把胜负预测到显著高于 50%，这本身说明该游戏的匹配**没有**把所有影响胜负的因素都平衡掉，而不是说明匹配在“操纵”结果；反之预测率≈50% 是平衡匹配的正常表现。

### Gaps
- 未找到 CS:GO/CS2 用纯赛前信息（非回合内信息）预测天梯对局的可靠准确率数据。
- Semenov et al. 2017 原文未能打开，分段与 AUC 的精确对应未核实。
- 未找到 Riot/Valve 官方公布的“匹配后预测胜率分布”数据。

---

## Q5. 自博弈强化学习：AlphaGo/AlphaZero、OpenAI Five、AlphaStar——为何“对自己 50%”说明不了绝对强度；非传递性问题

### Takeaway
在自博弈 RL 中，训练目标确实是“胜率”（奖励 = 胜负，最大化期望回报 = 最大化对给定对手分布的胜率），但进步只能用固定参照系来测量：OpenAI Five 用 83 个参考智能体组成的 TrueSkill 池，AlphaGo Zero 用跨检查点与外部程序的 Elo，AlphaStar 用 Battle.net 天梯 MMR；与“当前的自己”对战的胜率由对称性必然≈50%，不含绝对强度信息。由于真实游戏存在大量非传递性（石头剪刀布式循环），单一 Elo 可能误导，因此出现了 mElo、Nash averaging、α-Rank、“陀螺”几何等评估工具，以及按胜率挑选对手的联赛训练（PFSP）。

### Cited Findings
- **OpenAI Five**：论文附录称通过让各参考智能体互相大量对局来评估其 TrueSkill；参考池含 83 个智能体，TrueSkill 从 0（随机策略）到 254（击败世界冠军的版本）；训练中每个版本在上报 750 局后记录其 TrueSkill 并换到新版本 — [Berner et al., *Dota 2 with Large Scale Deep Reinforcement Learning*, arXiv:1912.06680](https://arxiv.org/abs/1912.06680)
- OpenAI Five 自博弈：每代约 80% 对局与当前策略自身对战、20% 与历史版本对战，以避免“策略坍塌”并提高对多样对手的鲁棒性；历史版本按动态质量分抽样，分数随训练对局胜负调整（来自二手综述，原文措辞未核实）— [AI in Human-computer Gaming 综述, arXiv:2111.07631](https://arxiv.org/abs/2111.07631)；[分布式 RL 综述, arXiv:2212.00253](https://arxiv.org/abs/2212.00253)
- **AlphaStar**：联赛（League）把虚拟自博弈（fictitious self-play）扩展到一组智能体；主智能体（main agents）按每个对手对自己的胜率调整对手混合概率，从而更多练习最难的对手；主剥削者（main exploiters）只对当前主智能体，专找其弱点；联赛剥削者（league exploiters）用类似 PFSP 机制但不被主剥削者针对；剥削者在加入联赛时可被重置为监督学习初始模型；DeepMind 称“**只为赢而下是不够的**” — [DeepMind 博客 2019-10-30](https://deepmind.google/discover/blog/alphastar-grandmaster-level-in-starcraft-ii-using-multi-agent-reinforcement-learning/)；[Vinyals et al., Nature 575:350–354 (2019), DOI:10.1038/s41586-019-1724-z](https://www.nature.com/articles/s41586-019-1724-z)
- PFSP 的权重函数：按 f(胜率) 归一化选择冻结对手；f_hard(x) = (1−x)^p 聚焦最难对手（p 控制分布熵）；f_var(x) = x(1−x) 聚焦水平相当的对手 — [Self-play 综述, arXiv:2408.01072](https://arxiv.org/abs/2408.01072)；开源实现（DI-engine）中 'squared' = (1−x)²、'variance' = x(1−x) — [DI-engine league/algorithm.py](https://huggingface.co/spaces/OpenDILabCommunity/gomoku/blob/main/DI-engine/ding/league/algorithm.py)
- AlphaStar 最终在 Battle.net 达到宗师（Grandmaster）级别（DeepMind 宣称高于 99.8% 的天梯人类玩家）— [DeepMind 博客](https://deepmind.google/discover/blog/alphastar-grandmaster-level-in-starcraft-ii-using-multi-agent-reinforcement-learning/)
- **AlphaGo Zero**：自博弈 3 天后以 100:0 击败击败李世石的版本（同样时限）；常被引用的评分：40 block 版 5185、AlphaGo Master 4858，DeepMind 图中 AlphaGo Lee 约 3500–3700 — [DeepMind 博客](https://deepmind.google/discover/blog/alphago-zero-starting-from-scratch/)；[the morning paper 解读](https://blog.acolyer.org/2017/11/17/mastering-the-game-of-go-without-human-knowledge/)；[Silver et al., Nature 550:354 (2017)](https://www.nature.com/articles/nature24270)
- **Leela Chess Zero（自博弈 Elo 通胀）**：相对前代网络测得的 Elo 无法衡量一般强度，因为网络是对其前代训练的；训练中的累计 Elo 通胀差异极大；社区观察到自博弈 Elo 远远夸大了网络间的强度差 — [Leela Chess Zero 维基条目（经搜索摘要）](https://en.wikipedia.org/wiki/Leela_Chess_Zero)；[TalkChess 讨论 2018](https://talkchess.com/viewtopic.php?p=762548)；[LessWrong 评论](https://www.greaterwrong.com/posts/LF3DDZ67knxuyadbm/contra-yudkowsky-on-doom-from-foom-2/comment/x8W5NwnkJXKhzQEk5)
- **Balduzzi et al. 2018（Re-evaluating Evaluation, NeurIPS）**：提出多维 Elo（mElo），去掉传递性假设、可表示循环的胜负关系；提出 Nash averaging——在评估数据上玩一个元博弈，取其唯一的最大熵纳什均衡，使评估对冗余任务/智能体不敏感（不会因加入大量弱智能体或简单任务而偏置）；以 AlphaGo 训练为例，并在 Atari 上发现 Nash averaging 下人类与最佳智能体打平 — [arXiv:1806.02643](https://arxiv.org/abs/1806.02643)；[NeurIPS 2018](https://papers.nips.cc/paper/2018/hash/cdf1035c34ec380218a8cc9a43d438f9-Abstract.html)
- **Czarnecki et al. 2020（Real World Games Look Like Spinning Tops, NeurIPS）**：真实博弈的策略空间像陀螺——纵轴是传递性强度，径向是同一强度层上的非传递循环数量；中等强度层循环最多，这解释了为什么训练需要策略“种群”，以及种群规模与博弈结构的关系；在 9 个真实两人零和对称游戏上用 Nash 聚类验证；作者也承认很多游戏（如 Kuhn 扑克、石头剪刀布）不符合此结构 — [arXiv:2004.09468](https://arxiv.org/abs/2004.09468)；[NeurIPS 2020 作者回复](https://proceedings.nips.cc/paper_files/paper/2020/file/ca172e964907a97d5ebd876bfdd4adbd-AuthorFeedback.pdf)
- **Balduzzi et al. 2019（Open-ended Learning in Symmetric Zero-sum Games, ICML）** 与 **α-Rank（Omidshafiei et al. 2019, Scientific Reports）**：前者引入 gamescape 与有效多样性、提出 PSRO_rN，论证在非传递博弈中单纯自博弈可能陷入循环；后者用演化动力学的马尔可夫-康利链给多智能体排名，替代 Elo/Nash（**这两条来自我的背景知识，本会话未能检索核实**）— [arXiv:1901.08106](https://arxiv.org/abs/1901.08106)；[α-Rank, Sci Rep 9:9937](https://www.nature.com/articles/s41598-019-45619-9)

### Inferences
- 【推理：为什么对自己 ≈50%】在对称零和博弈中，策略 π 对其完全相同的副本，期望得分由对称性恰为 0.5（仅受先后手/阵营不对称影响，如黑白、天辉夜魇）。所以“当前智能体对当前自己的胜率”恒为≈50%，不论它是新手级还是世界冠军级——**这与天梯中“收敛后人人≈50%”是同一个数学事实**：50% 只说明“对手与你同水平”，不说明“你的水平是多少”。
- 【推理：如何测绝对进步】必须引入一个**不随训练移动的参照系**：(a) 固定的参考智能体池 + TrueSkill/Elo（OpenAI Five）；(b) 跨检查点的 Elo 曲线，并锚定外部程序或历史版本（AlphaGo 系列）；(c) 人类天梯 MMR（AlphaStar）。Leela 的经验显示，即使跨检查点，只和“前代自己”比较也会让 Elo 通胀——因为每一代恰好学会了击败前代的特定弱点（非传递性），而这未必转化为对其他对手的强度。
- 【推理：RL 与评分系统中“目标”的角色互换】评分系统里，胜负是**标签**、实力是**潜参数**；自博弈 RL 里，胜率（对某对手分布的期望得分）就是**优化目标**，而 Elo/TrueSkill 是**事后测量工具**；AlphaStar 的 PFSP 又把“胜率”用作**课程设计的控制变量**（f_var(x)=x(1−x) 正是伯努利方差/Fisher 信息的形状，偏好 50% 对手；f_hard 偏好赢不了的对手）。三者都用同一个“胜率”，但含义完全不同，这正是用户“到底是胜率还是实力”困惑的来源。
- 【推理：非传递性对单一 Elo 的冲击】当 A>B>C>A 循环存在时，没有一组一维评分能同时把三对胜率都预测对；单一 Elo 只能拟合“平均”传递分量。卡牌游戏（包括酒馆战棋的流派克制、炉石天梯的卡组克制）天然有较强的非传递成分，因此单一评分对单局胜负的解释力会进一步下降。

### Gaps
- AlphaStar 论文 Methods 中主智能体实际采用的 PFSP 权重（f_hard 的 p 值、与 f_var 的混合比例）未能从原文核实。
- AlphaGo Zero 评分的计算方法（我记忆中为基于评估对局的 BayesElo 类方法，且 AlphaGo Zero 用“新网络对当前最佳≥55%胜率才替换”的门槛）未在本会话核实，报告中如引用需标注。
- OpenAI Five 80%/20% 比例来自二手综述，原文措辞未核实。
- 未找到炉石传说（构筑或酒馆战棋）公开的、以 Elo/TrueSkill 跟踪自博弈进展的 AI 项目文献。

---

## Q6. Elo/Bradley–Terry 在其他 ML 场景：LLM 排行榜（Chatbot Arena）、RLHF 奖励模型、GAN 的 50% 均衡

### Takeaway
Chatbot Arena 把“人类两两投票”当作胜负标签、用 Bradley–Terry 逻辑回归估计各模型实力（从在线 Elo 改为批量 BT 以消除顺序依赖并得到置信区间）；RLHF 的奖励模型用的就是 BT 损失 −log σ(r_w − r_l)，“奖励”就是潜在实力分；GAN 在理论均衡处判别器输出处处 1/2——三者与“收敛后对局≈50/50”是同一结构：训练信号来自成对比较的胜负，学到的是潜在分数，均衡时预测退化为 50%。

### Cited Findings
- Chatbot Arena 最初用在线 Elo 计算模型评分，后改为 Bradley–Terry 分数以获得更好的统计估计 — [Chiang et al., *Chatbot Arena*, ICML 2024, arXiv:2403.04132](https://arxiv.org/abs/2403.04132)（转述见 [vote rigging 论文 arXiv:2501.17858](https://arxiv.org/abs/2501.17858)）
- LMSYS 2023 年 12 月博文：改用 BT 后评分“显著更稳定、置信区间更精确”；在线 Elo 的结果依赖对局顺序 — [LMSYS 博客](https://lmsys.org/blog/2023-12-07-leaderboard/)
- LMArena 后续文章：Chatbot Arena 用 Bradley–Terry 模型对模型实力做统计推断，并讨论 BT/Elo 的统计扩展 — [LMArena: Statistical Extensions of the Bradley-Terry and Elo Models](https://news.lmarena.ai/extended-arena)
- RLHF 奖励模型的标准成对损失为 −log σ(r(x, y_w) − r(x, y_l))，即偏好（胜）回答与被拒（负）回答得分差的负对数 sigmoid — [Lambert, *RLHF Book*, 奖励模型章](https://rlhfbook.com/c/07-reward-models.html)；[TorchRL reward_model_loss 文档](https://docs.pytorch.org/rl/main/reference/generated/torchrl.objectives.llm.reward_model_loss.html)
- InstructGPT 将 K 个回答的排序拆成成对比较批量训练，并以负对数 sigmoid 形式写损失（Stiennon et al. 2020 写法符号不同）— [Ouyang et al. 2022, arXiv:2203.02155](https://arxiv.org/abs/2203.02155)；[Stiennon et al. 2020, arXiv:2009.01325](https://arxiv.org/abs/2009.01325)；[讨论帖](https://community.deeplearning.ai/t/is-it-a-typo-in-the-loss-function-of-reward-model-in-week3/429918)
- 从人类偏好学习奖励的开创工作采用 Bradley–Terry 型偏好模型（背景知识，未在本会话逐字核实）— [Christiano et al. 2017, arXiv:1706.03741](https://arxiv.org/abs/1706.03741)
- GAN：固定生成器时最优判别器 D*(x) = p_data(x)/(p_data(x)+p_g(x))；当 p_g = p_data 时 D(x) = 1/2，判别器无法区分两者；代入后目标为 −log4 + 2·JSD(p_data‖p_g)，全局最优在 p_g = p_data — [Goodfellow et al. 2014, arXiv:1406.2661](https://arxiv.org/abs/1406.2661)；[Hacettepe 课程讲义](https://web.cs.hacettepe.edu.tr/~erkut/cmp784.f24/slides/lec10-generative-models-part2.pdf)

### Inferences
- 【推理：同构关系】Chatbot Arena：模型 = 玩家，一次投票 = 一局，BT 分 = Elo 分；RLHF：回答 = 玩家，人类偏好 = 胜负，奖励 r = 实力；BT 损失与 Elo 的对数损失是同一个函数。所以“奖励模型学的是胜率还是实力？”与本题同构：**标签是胜负（偏好），预测是胜率 σ(r_w − r_l)，奖励值本身是只确定到常数的潜变量**（RLHF 中常对奖励做归一化，正是因为常数不可辨识）。
- 【推理：奖励模型的“50% 天花板”】若比较对中两回答质量接近（类比势均力敌的对局），或标注者之间本身就不一致，则即便完美的奖励模型准确率也有上限——与“平衡匹配下胜负预测上限≈50%”同理：不可约噪声来自标签过程本身。
- 【推理：GAN 的类比与其限度】GAN 均衡时判别器准确率 50%，类比“完美匹配后胜负 50%”：50% 是双方都无法再单方面改进的均衡标志，而不是“判别器没用”。但类比有限：GAN 是两个网络互相对抗、双方都在变；天梯里是评分系统在估计固定（或缓慢变化）的人类实力。实践中 GAN 常振荡而非稳定收敛，这与自博弈中的非传递循环相似。

### Gaps
- InstructGPT 原文中的标注者一致率与奖励模型验证准确率（我记忆中约 72%–77% 区间）未能核实，如需引用须回查原文。
- Chatbot Arena 的锚定方式（固定某参考模型的分数以消除平移不确定性）未核实。

---

## Q7. “胜率”被直接当作训练/优化目标的情形：以目标胜率做匹配、EOMM 优化留存、动态难度调整（DDA）

### Takeaway
在业界与学界确实存在把“胜率”或“胜负序列”直接当作优化对象的系统：TrueSkill 把“匹配后胜率接近 50%”作为匹配质量目标；EA 的 EOMM 证明“公平匹配”只是在简化假设下的特例，转而以最小化流失（churn）为目标来配对；EA 的 DDA 研究以最大化参与度为目标调节难度，相关专利出现“为每个用户计算使参与度最大的最优胜率”。后果是：一旦优化目标从“准确估计实力”换成“操纵胜负体验”，胜负数据就不再只是实力的噪声观测，而混入了系统的意图。

### Cited Findings
- TrueSkill：系统三大模块为更新（Update）、匹配（Matchmaking）、排行榜；匹配要安排“有趣”的对局，即各方获胜机会相对均等的对局；匹配质量 = 重标度的平局概率 — [MSR TrueSkill 项目页](https://www.microsoft.com/en-us/research/project/trueskill-ranking-system/)
- TrueSkill 论文以“每位玩家胜率偏离 50% 的平均幅度”作为评价匹配质量的指标之一 — [TrueSkill NIPS 2006](https://www.microsoft.com/en-us/research/publication/trueskilltm-a-bayesian-skill-rating-system/)
- EOMM（Chen, Xue, Kolen, Aghdaie, Zaman, Sun, Seif El-Nasr；WWW 2017，EA）：认为“公平优先”的匹配不一定最大化参与度，**同等实力配对只是其框架在简化假设下的特例**；把等待中的玩家建模为完全图，边权为该配对的联合流失风险，用最小权完美匹配最小化总流失；框架由实力模型、流失预测模型与图匹配三部分组成；在基于 EA 某热门 PvP 游戏真实数据的模拟中留存优于其他方法；仅限 1v1 — [arXiv:1702.06820](https://arxiv.org/abs/1702.06820)
- EA 的 DDA 研究（Xue, Wu, Kolen, Aghdaie, Zaman；WWW 2017 Companion, pp. 465–471）：以最大化玩家整个游戏过程中的参与度为全局目标，把关卡进度建模为图，DDA 即优化转移概率以最大化停留时间；报告参与度最多提升 9%，对付费影响中性 — [Xue et al. 2017, DOI:10.1145/3041021.3054170](https://archives.iw3c2.org/www2017/proceedings/companion/p465.pdf)
- 一项 EA 的 DDA 专利描述了“为用户计算一个使参与度最大化的最优胜率”（依据搜索摘要；具体专利号对应关系未逐字核实）— [US 10,286,323 “Dynamic difficulty adjustment”](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10286323)
- TrueSkill 2 刻意不把“与高手对位者也更可能是高手”等相关性纳入模型，理由是会产生错误激励 — [TrueSkill 2](https://www.microsoft.com/en-us/research/publication/trueskill-2-improved-bayesian-skill-rating-system/)
- Elo-MMR 论文证明其系统是激励相容的：追求评分最大化的玩家永远不会想故意打差 — [Ebtekar & Liu, *Elo-MMR*, WWW 2021, DOI:10.1145/3442381.3450091](https://dl.acm.org/doi/10.1145/3442381.3450091)

### Inferences
- 【推理：三种“以胜率为目标”的含义不同】
  1. **以 50% 预测胜率为匹配约束**（TrueSkill 式公平匹配）：目标是让每局最有信息量、最“有趣”，副作用是长期胜率被钉在 50%，这本身不扭曲实力估计。
  2. **以个体最优胜率/留存为目标**（EOMM、DDA 专利）：系统根据流失预测，有意给某些玩家配更易赢或更难赢的对局。此时“胜负序列”不再是“实力 + 随机噪声”，而是“实力 + 噪声 + 系统干预”。
  3. **以胜率为 RL 训练目标**（自博弈）：见 Q5。
- 【推理：对评分模型的后果】若匹配器按非公平目标选择对手，只要评分更新仍使用正确的预测胜率 E（即对手实力已知），Elo/BT 的估计在理论上仍无偏——因为对手选择依赖的是可观测变量（评分），而非结果本身；但会降低每局的信息量（偏离 50% 的对局 p(1−p) 更小），使实力估计收敛更慢；如果系统还依赖评分以外的隐藏变量（如流失风险）来挑选对手，而这些变量又与表现相关，则可能引入偏差。这是我基于统计推理的判断，未找到直接论证该点的文献。
- 【推理】这也给出一个可检验的区分：在纯公平匹配下，玩家的“胜负残差”(y − p) 应近似独立同分布；在 EOMM/DDA 式干预下，残差应与流失风险、连败长度等变量相关。（是否存在这种干预、如何检验，属本研究其他部分的范围。）

### Gaps
- 未找到公开证据显示某款具体商业游戏在天梯中部署了 EOMM 式匹配（EOMM 论文仅为模拟）。
- 未找到关于 DDA/目标胜率对玩家长期实力估计准确性的实证研究。

---

## Q8. 对 8 人游戏（如炉石传说·酒馆战棋，名次 1–8 而非胜负）的意义：排序损失（Plackett–Luce）、多人评分、名次预测与公开 AI/评分研究

### Takeaway
8 人名次比 1v1 胜负信息量大得多（一局完整名次最多约 log₂(8!) ≈ 15.3 比特，而 1v1 至多 1 比特），可以用 Plackett–Luce 似然（或拆成 28 个两两比较）把“名次”当标签来学潜在实力；TrueSkill、Weng–Lin（OpenSkill）、Elo-MMR 都原生支持多人排名，评估宜用面向名次的指标（如 NDCG）。同样的“收敛”逻辑适用：大厅成员评分相近时，每人的期望名次≈4.5、前四率≈50%，名次分布接近均匀。公开的酒馆战棋 AI/名次预测文献极少。

### Cited Findings
- TrueSkill FAQ 原文：t 队、每队 p 人的一局结果提供 log₂(t!) 比特信息；一般情形下每名玩家需约 t·p·log₂(n)/log₂(t!) 局 — [MSR TrueSkill 项目页](https://www.microsoft.com/en-us/research/project/trueskill-ranking-system/)
- TrueSkill 原文：Halo 2 Beta 数据包含 8 人自由混战（Free for All）模式；作者称 TrueSkill 接近 n·log(n) 比特的信息论极限，对 8 人对局给出的观察收敛约为 10 局（文中给出的信息论极限约 5 局/人）；对 Elo 则用“对决启发式（duelling heuristic）”——对每名玩家与其他每名玩家两两比较后取平均更新 — [TrueSkill NIPS 2006](https://www.microsoft.com/en-us/research/publication/trueskilltm-a-bayesian-skill-rating-system/)
- Weng & Lin：处理多队多人对局，把 k 队对局视为多个两队对局；关键词含 Plackett–Luce — [JMLR 2011](https://jmlr.org/papers/v12/weng11a.html)；作者实现页 [NTU 林智仁](https://www.csie.ntu.edu.tw/~cjlin/papers/online_ranking)
- Elo-MMR：面向参赛人数众多的排名式比赛（编程竞赛、障碍赛跑、电子游戏），声称预测准确率超过现有系统、速度最多快一个数量级、可处理数千到数百万名个人排名选手，并证明激励相容；DMOJ 于 2021 年 8 月迁移到 Elo-MMR — [Ebtekar & Liu, WWW 2021](https://dl.acm.org/doi/10.1145/3442381.3450091)；[DMOJ 公告](https://dmoj.ca/post/206-ratings-migrated-to-elo-mmr)；[PyPI elommr](https://pypi.org/project/elommr/)
- Dehpanah 等：在 10 万+ 场自由混战对局上评估评分系统的评价指标，推荐 NDCG；Elo 与 Glicko 原为两人设计，TrueSkill 可处理多队多人 — [arXiv:2008.06787](https://arxiv.org/abs/2008.06787)；团队实力聚合（PUBG/LoL/CS:GO）研究中 TrueSkill+MAX 聚合在 PUBG 全体玩家上 NDCG 约 62.2% — [arXiv:2106.11397](https://arxiv.org/abs/2106.11397)
- 炉石相关 ML：Bursztein 用卡牌优势等指标预测炉石构筑对局结果 — [elie.net 2016](https://www.elie.net/blog/hearthstone/predicting-hearthstone-game-outcome-with-machine-learning)；FedCSIS/AAIA 数据挖掘挑战中有炉石胜率预测任务 — [Annals CSIS Vol.11](https://annals-csis.org/Volume_11/drp/pdf/563.pdf)、[Vol.15](https://annals-csis.org/Volume_15/drp/pdf/363.pdf)；有一篇面向酒馆战棋的蒙特卡洛模拟决策辅助论文（据搜索摘要，用顶级玩家的历史数据训练、帮助玩家冲分；细节未核实）— [EasyChair 预印本](https://easychair.org/publications/paper/Kftf)

### Inferences
- 【推导：信息量】8 人完整名次 log₂(8!) = log₂ 40320 ≈ 15.3 比特，等价于约 15 局“完美”1v1 的上限；即使只看“是否前四”，一局也提供至多 1 比特 × 每人。因此 8 人名次制游戏的评分理论上收敛更快——但单局名次受随机性（发牌/酒馆刷新/对手配对）影响大，实际信息远低于上限（TrueSkill FAQ 所说的“强者并不总赢”）。
- 【推导：Plackett–Luce 下的“Elo 式”更新】设玩家实力 s_i，名次序列 π（π(1) 为第一名），PL 似然 P(π) = Π_{i=1}^{8} exp(s_{π(i)}) / Σ_{j≥i} exp(s_{π(j)})。对玩家 k（名次 r_k）求导：∂log P/∂s_k = 1 − Σ_{i=1}^{r_k} P_i(k)，其中 P_i(k) = exp(s_k)/Σ_{j≥i} exp(s_{π(j)}) 是“第 i 轮从剩余者中选出 k”的模型概率。第一名得到正梯度 1 − P_1(k)，第八名得到 1 − Σ…（最后一项为 1）< 0，中间名次视情况。这仍然是“实际 − 期望”的残差形式，即 Elo 在名次数据上的自然推广；对其做 SGD 就是一个“名次版 Elo”。另一常用做法是把一局拆成 28 个两两胜负再用 Elo/BT（即 TrueSkill 论文里的对决启发式）。
- 【推理：收敛态】若 8 人大厅评分完全相同，则在任何对称模型下每人每个名次的概率均为 1/8，期望名次 4.5，前四率 50%，第一名率 12.5%；此时模型对名次的预测完全退化为均匀分布（多类 log-loss = ln 8 ≈ 2.08 nats）。与 1v1 一样，这不是模型失败，而是“同水平大厅”的直接结果；实力体现在你所在大厅的平均评分上，而非你的平均名次上。
- 【推理：对酒馆战棋 MMR 解读的启示】若天梯 MMR 用“名次 − 期望名次（由大厅平均分决定）”来更新（这是 Elo 式多人系统的通用结构），则长期平均名次会被推向约 4.5（加减随机游走），与 1v1 中胜率被推向 50% 同理。这一点需与本研究其他部分关于 Battlegrounds 实际 MMR 公式的调查交叉核对。
- 【推理】非传递性（流派/英雄克制、同大厅抢同一种族）在酒馆战棋中可能很强，单一标量 MMR 对单局名次的解释力有限；评估此类系统宜用名次感知指标（NDCG、名次 log-loss），而不是“预测第一名准确率”。

### Gaps
- 未找到暴雪官方公开的酒馆战棋 MMR 更新公式或其评分系统的同行评审分析（属于本研究其他部分的范围，需交叉引用）。
- 未找到公开的酒馆战棋“名次预测模型”及其准确率数据，也未找到以 Plackett–Luce/TrueSkill 拟合酒馆战棋对局的公开研究。
- EasyChair 上酒馆战棋决策辅助论文的标题、作者与结论均未能核实。
