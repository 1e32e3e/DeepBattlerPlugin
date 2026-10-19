# 待核对来源：第一章 1a（学术研究）

本次写作时能读到 arXiv、微软研究院、AAAI、JMLR、glicko.net、FIDE、PMC、Nature 等站点的全文；下表列出仍未读到全文、或只能依据摘要/二手转述的来源。正文对应位置有 `\needcheck` 脚注。整合时并入 `docs/TO_VERIFY.md`。

| 章节 | 来源键名 | 需要核对的说法 | 原因 |
|---|---|---|---|
| 1a §成对比较 | thurstone1927law, mosteller1951remarks, zermelo1929berechnung, bradley1952rank, luce1959individual, plackett1975analysis | 各模型的公式与“Zermelo 用该模型从循环赛结果推算棋手实力” | 经典原文未重读，只核对题录；模型形式依据 Glickman 1995、TrueSkill 论文、Aldous 2017 的转述。优先级低 |
| 1a §Elo 理论 | jabin2015continuous | “在一定假设下评分密度收敛到实力密度” | SIAM 付费墙；结论来自 Aldous 2017 与 Düring 等 2022 的转述 |
| 1a §Elo 理论 | during2019boltzmann | “加入学习效应” | 只核对了题录（Crossref），未读全文。优先级低 |
| 1a §组队 | gong2020optmatch | OptMatch 在《潮人篮球》上的线上实验及效果 | ACM 页面无法访问，只读到 Semantic Scholar 上的摘要 |
| 1a §组队 | deng2021globally | GloMatch 用自注意力和强化学习做全局优化 | 只读到 EnMatch 论文对它的描述 |
| 1a §参与度匹配 | delalleau2012beyond | “享受”标签来自赛后问卷还是启发式 | IEEE Xplore 无法访问；EOMM 论文的描述（问卷）与检索到的摘要片段（问卷数据不可得、改用启发式）相互矛盾，需看原文 |
| 1a §参与度匹配 | chen2026matchmaking | Lichess 案例：参与度 +4%—6% 或机器人比例 −3%；会议版“把不会流失的低水平玩家配给再输一局就流失的高手”；数据 540 万局 | 只读到 Crossref 摘要与 INFORMS 新闻稿；期刊全文（Management Science 72(10)）需校园网 |
| 1a §DDA | hunicke2005case | 2005 年论文报告的用户研究结果 | ACM 全文未读到；正文只说“报告了用户研究”，未引具体数字 |
| 1a §连胜连败 | kou2018playing | 连胜连败都损害体验、脱离游戏是主要应对 | ACM 全文无法访问，只读到 Penn State 机构库摘要 |
| 1a §连胜连败 | deng2024streaks | 597680 场、相关显著但很小、休息在输局后略改善表现 | 论文为 CC-BY，但 ACM 页面拒绝本环境访问，只读到摘要 |
| 1a §英雄联盟 | veron2014matchmaking | 2800 多万局公开数据、分析匹配服务需求 | HAL/作者主页下载失败，只读到摘要 |
| 1a §Dota 2 | semenov2017performance | 仅凭阵容预测能力有限，分段越高越难预测 | Springer 付费；依据第一轮笔记引用的作者报告幻灯片（AUC 约 0.66—0.70），本次幻灯片站点连接失败 |
| 1a §星际争霸 II | vinyals2019grandmaster | AlphaStar 在 Battle.net 上“按天梯 MMR 评估”的细节（宗师级、高于 99.8% 已由摘要证实） | 只读到《自然》摘要，正文需订阅 |
| 1a §中文文献 | wang2019jingji | 王瑞 2019 安徽大学硕士论文的存在与题录（导师吴建国） | 知网/万方无法从本环境访问，仅见掌桥科研第三方题录 |
| 1a §中文文献 | chen2012pinggu | “ELO 未收敛导致团队配对失衡；估计玩家与团队影响力补足” | 台湾交通大学机构库连接失败，只读到检索摘要；原题为繁体，文中转为简体 |
| 1a §中文文献 | huang2010tuanti | 用团体动力学加入团体结构与沟通因素改善团队配对 | 同上 |

## 本次已核对、并更正了第一轮报告的条目（供整合参考）

| 来源键名 | 第一轮说法 | 本次核对结论 |
|---|---|---|
| kang2024match | 数据约 600 万场；“2700 万场”无依据 | 两个数字都在原文：分析面板约 600 万局（26.27 万名流失玩家、150 万个玩家—日）；整个 42 天日志约 2700 万局（图 1 说明）。连败在主模型中不显著（p=0.773），但加入游戏阶段交互后显著且因阶段而异 |
| bober2024skill | “在 CS:GO 大数据集上比较评分系统” | 数据是 HLTV 的 9929 场职业/半职业比赛，不是官方匹配；Glicko-2 在队伍层面略优，按选手评分的 TrueSkill 最好（64.1%） |
| zhang2022quickskill | “20%”在摘要中找不到 | arXiv 全文引言写明“可消除新手阶段 20% 以上的一边倒对局” |
| fan2024cupid | 只报告 7.18% 的离线提升 | 全文还透露：对照组为某数千万玩家手机 MOBA 排位模式的“基于 TrueSkill 的一步式 MMR 匹配”，MMR 预测准确率 52.83%；30 天、10% 流量 A/B |
| wang2024enmatch | 无线上效应量 | 两周 A/B：总对局数 +1.64%（3v3 篮球）、+7.19%（15v15） |
| fide2024rating | “400 分规则”适用于所有人 | 自 2025-10-01 起只适用于 2650 分以下；FIDE 换算表与单人标准差约 200 的正态曲线吻合（最大偏差 19 分），并非逻辑斯蒂 |
| rosenthal2025investigation | 列在 Lichess 下 | 数据来自 Chess.com（应其首席执行官之邀，平台提供数据） |
| do2021using | 未提样本量 | 只有 5000 场排位对局 |
| chen2026matchmaking | 期刊信息未定 | Management Science 72(10): 8770–8788（2026 年 10 月） |
