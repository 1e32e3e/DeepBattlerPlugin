# 事实核查：industry_patents.md（行业披露、专利与公司论文）

> 核查对象：`industry_patents.md`（原文件未修改）。核查日期 2026-10-18。
> 方法：用 WebSearch 结果摘要做交叉核对。WebFetch 与 curl 访问 justia、blizzard、uspto、crossref、semanticscholar 等主机全部失败（DNS ENOTFOUND / 代理 CONNECT 403），所以**本文件的结论和原笔记一样，都只基于搜索摘要**，没有逐字通读原始页面。
> 判定规则：CONFIRMED = 至少两个独立摘要一致，或某个一手来源（官方页/专利记录/论文索引）的摘要明确给出；CONFIRMED-as-reported = 只能确认"媒体/转引确实这么写"，一手原文未见；CORRECTED = 原说法有误、出处或日期不精确，并给出更正；REFUTED = 与证据相反；UNVERIFIABLE = 查不到可靠支持。
> 结果概览：共核查 66 条。CONFIRMED（含 as-reported 与部分确认）53 条；CORRECTED 11 条（P3、P7、P13、P15、C2、B6、H4、H5、H8、X2、I1）；UNVERIFIABLE 1 条（P16）；仅补充信息 1 条（P17）；REFUTED 0 条。没有发现"方向性错误"，修正集中在**出处、日期精度、权利人**三类。

## 一、汇总表

### 专利
| # | 主张（原笔记） | 结论 | 置信度 |
|---|------|------|--------|
| P1 | Activision US 9,789,406 "System and method for driving microtransactions in multiplayer video games"，2015 申请，2017-10-17 授权 | CONFIRMED | 高 |
| P2 | Activision 声明："exploratory patent filed in 2015 by an R&D team working independently from our game studios. It has not been implemented in-game" | CONFIRMED（多家媒体逐字一致） | 高 |
| P3 | Bungie Deej："None of this functionality appears in Destiny"，并确认 Destiny 2 也没有 | CORRECTED：推文（2017-10-17）原文只写 "Destiny"；"Destiny 2 也没有"是媒体的解读/标题 | 中 |
| P4 | US 10,322,351 Activision，优先权 2014-07，2019 授权 | CONFIRMED（授权 2019-06-18，优先权 2014-07-03） | 高 |
| P5 | US 10,376,792 "Group composition matchmaking…"，Activision | CONFIRMED（申请 2015-05-14；发明人 Bansi、Kerby、Hall、Wilson；授权日按相邻号 10,376,793 推定为 2019-08-13） | 中 |
| P6 | EA US 10,286,327：图模型+流失率预测的匹配 | CONFIRMED（授权 2019-05-14；说明书写明为每个用户计算 churn risk、在加权连通图上选边） | 高 |
| P7 | US 10,751,629 授权年份（笔记称 2020/2019 冲突） | CORRECTED → 2020-08-25 授权；"2019"是其公开文本 US 2019/0262718 A1 的年份。发明人 Su Xue、Kazi Zaman、Navid Aghdaie、John Kolen、Zhengxing Chen（与 EOMM 论文作者重合） | 中高 |
| P8 | US 11,344,814 2022-05-31 授权 | CONFIRMED（单一聚合页） | 中 |
| P9 | EA US 10,610,786 "Multiplayer video game matchmaking optimization"，2020-04-07 授权 | CONFIRMED（优先权 2016-03-08；同族续案 US 11,141,663，2021-10-12） | 高 |
| P10 | EA US 9,919,217 "Dynamic difficulty adjustment"，2018-03-20，发明人含 Navid Aghdaie | CONFIRMED | 中高 |
| P11 | DDA 同族 US 10,286,323（2019）、US 10,807,004（2020） | CONFIRMED（2019-05-14；2020-10-20；另有续案 US 11,369,880） | 中高 |
| P12 | Microsoft US 8,538,910 "Determining relative skills of players"，Minka/Graepel/Herbrich，公开号 US 2009/0227313 | CONFIRMED（2013-09-17 授权）。补充：它是对 TrueSkill 的**后续改进**专利；TrueSkill 的原始专利是 US 7,050,868（2006-05-23）与其续案 US 7,376,474 "Bayesian scoring"（Graepel、Herbrich） | 高 |
| P13 | Riot US 11,484,801（2021-03-23 申请，2022-11-01 授权），按常用游戏时段相似度组队；"另有申请 Activity-factored team formation（2022-09-29 公开，非授权）" | 前半 CONFIRMED。后半 CORRECTED：11,484,801 的标题就是 "Activity-factored team formation in multiplayer online gaming"，2022-09 公开的是**同一件**申请的公开文本，不是另一件申请 | 高 |
| P14 | Riot US 11,065,547：部分依据玩家档案中的行为数据匹配 | CONFIRMED（补充：是 US 9,795,887 的续案，发明人 Jeffrey Lin、Paul Sottosanti；行为分类如 Leader/Teammate/Mentor/Verbal Aggressor；另有续案 US 11,865,460） | 高 |
| P15 | US 12,533,594 "Method and apparatus for game matching…"，权利人未确认（笔记放在"Tencent / 中国专利"下） | CORRECTED → 原始权利人为 **Beijing ByteDance Network Technology Co., Ltd.（字节跳动）**，发明人 Shuai Hao、Guande Qi、Jierui Chen，申请 US 18/323,707，公开号 US 2023/0381666 A1（据 Google Patents 摘要，两次检索一致） | 中 |
| P16 | CN112221161B（申请号 CN202011228107.3），权利人未确认，"命名格式与腾讯常见专利一致" | UNVERIFIABLE：4 次检索都没拿到申请人字段。"像腾讯"只是推测，报告中不应写成腾讯专利 | — |
| P17 | US 11,478,715 "User-controllable model-driven matchmaking"，权利人未确认 | 补充：Patent Arcade 列为 Electronic Arts（单一二手来源） | 低中 |

### EA 诉讼
| # | 主张 | 结论 | 置信度 |
|---|------|------|--------|
| L1 | Zajonc v. Electronic Arts，美国北加州联邦地区法院，2020-11 起诉 | CONFIRMED（案号 3:20-cv-07871，2020-11-09 起诉；原告 Jason Zajonc、Danyael Williams、Pranko Lozano；涉及 Madden/FIFA/NHL 2017–2021 版） | 高 |
| L2 | 2021-02-11 原告在获得技术资料、与工程师交流后自愿撤诉 | CONFIRMED（撤诉原因只见 EA 自述及据此的报道，案卷原文未见） | 高 |
| L3 | EA 回应："baseless and misrepresent our games"；"never was in FIFA, Madden or NHL, and never will be"；不用 DDA 影响任何游戏的在线多人 | CONFIRMED（EA 官方 "Fair Play & Dynamic Difficulty Adjustment" 页："We would not use DDA technology to give players an advantage or disadvantage in online multiplayer modes in any of our games"） | 高 |

### Call of Duty
| # | 主张 | 结论 | 置信度 |
|---|------|------|--------|
| C1 | "An Inside Look at Matchmaking"（2024-01，2024-04-04 更新）：连接权重最高，其次是匹配用时，技能不是主导变量 | CONFIRMED（原帖 2024-01-29；原文 "most critical and heavily weighted factor"，Time to Match 为 "second most critical"） | 高 |
| C2 | "money spent is in no way a factor in multiplayer matchmaking"（笔记称依赖媒体转述） | CORRECTED（措辞）：博客原文为 "money spent does not in any way, shape or form, factor into matchmaking"（GameSpot 引述），意思一致 | 中高 |
| C3 | 白皮书 #1 Ping（2024-04）、#2 Skill（2024-07）、#3 Ranked（PDF 2024-12-23） | CONFIRMED（#1 发布于 2024-04-04，由 #2 自述；#3 日期取自 PDF 文件名） | 高 |
| C4 | Deprioritize Skill Test：MWIII、北美、50% 玩家进入放宽技能约束的处理组 | CONFIRMED（Activision PDF 摘要原文："a treatment group of 50% of the population… we loosened the skill constraints"，时间为 early 2024） | 高 |
| C5 | 一个月后按技能分 10 组，90% 的组回流显著下降，只有最高 10% 回流增加；高手最终也会流失 | CONFIRMED（实质内容，多家媒体一致，含 "10 equally sized groups—sorted by skill" 和 "top 10%→top 20%→top 30%"）；Activision PDF 中这句的逐字原文未见。**注意**：TweakTown 等把它写成"回流率下降 90%"，是误读 | 中 |
| C6 | "Players who frequently experience blowouts are seen to quit matches in progress and the game itself" | CONFIRMED-as-reported（媒体引作白皮书原句） | 中 |
| X1 | BO7 Beta "Open Moshpit"（"skill consideration is drastically reduced"）；上线后 Open（"minimally considered"）/ Standard（"important consideration"），多数列表为 Open | CONFIRMED（Treyarch Beta 补丁说明及多家媒体） | 高 |

### Blizzard（酒馆战棋 / OW2）
| # | 主张 | 结论 | 置信度 |
|---|------|------|--------|
| B1 | BG "Developer Insights: Personal Rating"：Elo/Glicko 为两人设计，"not a good option for us"；自研算法 "fastest runtime… highest accuracy"；评分+隐藏方差 | CONFIRMED（作者 Tian，Senior Data Scientist；时间约 2019-11，文中讨论"11 月 19 日"改动） | 高 |
| B2 | 每局计算 8 人两两胜率共 56 次 | CONFIRMED（原文 "to be precise, 56"，即 8×7 个有序对，每对都纳入方差等因素） | 高 |
| B3 | 6500 以下每局小幅保底加分（无论胜负） | CONFIRMED（2019 原帖："small, always-positive progression adjustment… if you are below 6500"；2020 18.4 更新帖重申并举 53/47 的例子） | 高 |
| B4 | 11-19 改动：首局第一约 +240→+195（另转引 190），第 150 局起约 +24→+98（另转引 95） | CONFIRMED。两组数字都出自暴雪：开发者洞察帖为 195/98，论坛"Battlegrounds Update – November 19"为 190/95 | 高 |
| B5 | "Rating System Update"（23523064）：区分内部与外显评分，外显评分不参与匹配 | CONFIRMED（补充：18.4 补丁，2020-09；外显评分每赛季清零，≤2000 不掉分，2000–6000 每 500 一道保底，单局外显最多 +300，外显低于内部时有追赶倍率；内部评分永不重置、无保底、无加分，可能做"归一化"） | 中高 |
| B6 | Icy Veins"12 月 5 日 MMR 更新"（高分段调整、MMR 归一化设想） | CORRECTED：该改动是误随 12-05 补丁上线的，暴雪 12-06 宣布**回滚**（"everything will be just as it was before"）；"5500 以上压回 5500"的计划未见落地 | 中高 |
| O1 | OW2 part 1：只看 MMR；新手初始 MMR 先设为略低于平均、再降到 Bronze 5 等价，"sub-40% win-rate" 新手显著改善；初期 MMR 调整更快 | CONFIRMED（补充：同时加入 "streak modifier" 让错位玩家更快归位）。精确发布日期未取得（约 2023 年初） | 中高 |
| O2 | OW2 part 2：不强制 50%、无赢家/输家队列、"Your current MMR is the only thing the matchmaker takes into consideration…" | CONFIRMED（补充：S3 起段位更新从"7 胜/20 负"改为"5 胜/15 负"） | 高 |

### Riot / Valve / 其他西方厂商
| # | 主张 | 结论 | 置信度 |
|---|------|------|--------|
| R1 | Riot 2018-02 "/dev: Matchmaking Real Talk"："most teams have an expected win rate of 50 +/-1%" | CONFIRMED（作者 Riot Gortok；文中称"连胜后给差队友"是 "pretty much an urban myth"） | 高 |
| R2 | Phroxzon（15.14 预告）："We're not matching you on your honor score, your number of pings, your runes, whether you're on a loss streak…"，只用 MMR + on-role parity | CONFIRMED（GGScore 转述；X 原帖未直接看到） | 中 |
| R3 | Auberaun："No, we don't do that. Aim for as close to 50% every time" | CONFIRMED-as-reported（只有 Dot Esports，日期不明） | 中 |
| R4 | Valorant EvrMoar 2022 回应 Shroud："There is no loser's queue… We do not manipulate the queue"；variance 解释（"This is why win-streaking… really helps you climb"） | CONFIRMED。补充：EvrMoar 就是 Jonathan "EvrMoar" Walker，与笔记 Valorant 第一条里的 "Jon Walker" 是同一人 | 高 |
| V1 | Valve Jeff Hill："a 50% lifetime win rate isn't an explicit goal or constraint of the matchmaker…" | CONFIRMED-as-reported（只见于 Steam 讨论帖和俄文转引，Valve/Reddit 原帖未见；笔记已标注） | 中 |
| V2 | Dota 2 天梯帖："win/loss is the primary criteria used to update MMR, but individual performance also plays a role, especially when our uncertainty about your MMR is high"；10 场定级 | CONFIRMED（PCGamesN 与 DotaFire 转载一致） | 高 |
| V3 | CS:GO "started with ideas based on the Glicko-2 rating model"（约 2015 年 Reddit 员工） | CONFIRMED（员工账号 u/vitaliy_valve，经 AFK Gaming、PC Gamer 转述） | 中高 |
| X2 | Apex 2023 博文（Samy Duc）：以预组队中最强玩家的技能分为准、考虑队伍人数；"改用更细粒度（更多分桶）的系统" | 前半 CONFIRMED（2023-01-17）。后半 CORRECTED：博文说旧 SBMM 本身就是"分桶"法（"uses the Bucket approach, but that is changing"），新系统是**替换**分桶法，不是"更多分桶" | 中 |
| F1 | Fortnite 2019-09 v10.40 引入 SBMM；机器人随实力提高而减少；竞技列表无机器人 | CONFIRMED（"face fewer bots"是 EGM 的转述，Epic 原话为 bots "will work in conjunction with the new matchmaking system"） | 高 |
| HL1 | Halo Infinite：MMR 由 TrueSkill2 计算，CSR "is not directly used in the matchmaking process" | CONFIRMED（Halo Waypoint 原文） | 高 |
| A6 | TrueSkill 2（MSR-TR-2018-8，2018-03）：Halo 5 历史对局预测准确率 68% vs 52% | CONFIRMED（作者 Minka、Cleven、Zaykov） | 高 |
| LC1 | Lichess 用 Glicko-2，新账号 1500，计算时考虑执黑加权；Chess.com 用 Glicko-1 | CONFIRMED（Lichess 官方页："more points awarded for results with the black pieces"） | 高 |

### 王者荣耀 / 腾讯 / 网易
| # | 主张 | 结论 | 置信度 |
|---|------|------|--------|
| H1 | 孙千和 2024-06 向深圳市南山区法院起诉，要求公开匹配因素及权重 | CONFIRMED（注意：Inven Global 英文稿把"起诉"写成 2025-08，实际是混淆了开庭时间） | 高 |
| H2 | 2025-08-12 开庭；腾讯提交近 1000 页证据，主张核心商业秘密 | CONFIRMED（补充：庭审约 5 小时，未当庭宣判） | 高 |
| H3 | 2026-01-22 案由由"网络服务合同纠纷"改为"数据纠纷" | CONFIRMED | 中高 |
| H4 | 2026-04-07 一审驳回全部诉求；理由：超出知情权合理范围、已披露主要因素、公开可能被恶意利用 | 驳回及理由 CONFIRMED。CORRECTED（日期精度）：4-07 是原告在自己的新媒体账号**公布**一审结果的日期，媒体 4-08 集中报道，判决书的作出日期没有报道。补充理由：本案不涉及社会公共利益，不能参照其他平台的算法公开要求；判决建议运营商可提供"关闭算法推荐"等选项。原告称尚未决定是否上诉；截至 2026-10 未检索到上诉或二审报道 | 中高 |
| H5 | 腾讯："我们没有任何动机去干预召唤师们的对局结果与胜率" | CORRECTED（出处）：这句话出自 **2018 年**官网《狄仁杰答疑｜匹配算法全面解析》，下半句是"这样做对《王者荣耀》毫无好处"，2025–26 年媒体重新引用。不是诉讼期间的新声明 | 中 |
| H6 | 庭审中腾讯展示 500–2500 场、胜率 >70% 的玩家样本 | CONFIRMED-as-reported（源自南方都市报，36氪等转载；另一篇评论称其中最多的一名玩家 2398 场、胜率约 71%） | 中 |
| H7 | S42（2026-01-08）"以段位为主"；官方称 90% 以上对局双方段位差在 2 星内 | CONFIRMED（1-04 官宣，12-30 预告"90% 以上 2 星内"）；灰度测试自 2025-11-13 起 | 中高 |
| H8 | 段位差 5 星内 66.8%→99.6%、2 星内 36.1%→90.7%（笔记挂在 S42 条目下） | CORRECTED（出处/时间）：这组数字见于 **2026-08** "对局环境优化专栏"首期，是对此前匹配优化成效的回顾，不是 S42 上线时的公告 | 中 |
| H9 | 2026-08 排位匹配新增"负面信誉"维度，邀请职业教练复盘连败对局 | CONFIRMED（补充：官方称收集了 7000 多条反馈） | 中高 |
| H10 | 2018-05 策划 Donny 发微博介绍 ELO | CONFIRMED-as-reported（虎嗅转述，原微博未见） | 中 |
| N1 | Marvel Rivals 2025-08 中旬官方声明不使用 EOMM；Guangguang 在 Rivals Assembled 访谈中否认；随后有 Zhiyong 主讲的官方视频 | CONFIRMED（视频约一周后发布；"Zhiyong 主讲"只在部分来源出现） | 中 |

### 公司论文
| # | 主张 | 结论 | 置信度 |
|---|------|------|--------|
| A1 | EOMM：WWW 2017，pp.1143–1150，DOI 10.1145/3038912.3052559，作者 Chen, Xue, Kolen, Aghdaie, Zaman, Sun, Seif El-Nasr | CONFIRMED | 高 |
| A2 | OptMatch KDD 2020 pp.2300–2310（Gong, Feng, Ye, Li, Wu, Tao, Fan, Cui）；网易归属 | 书目 CONFIRMED（DBLP）。网易归属仍是**推断**：多名作者（Runze Wu、Changjie Fan、Xiaochuan Feng）在 EnMatch 中署名网易伏羲，Linxia Gong 在 GDC 2021 讲过网易匹配实践；论文本身的单位信息未见 | 中 |
| A3 | EnMatch：AAAI-38(8):9098–9106，作者全部署名网易伏羲（杭州），"online deployments on two games" | CONFIRMED（10 位作者，DOI 10.1609/aaai.v38i8.28760） | 高 |
| A4 | CUPID：arXiv 2406.19720，PACM HCI DOI 10.1145/3686978，胜率预测平均相对提升 7.18%，部署于一款热门 MOBA | CONFIRMED。补充作者单位：Ge Fan、Yingjie Li（腾讯），Chaoyun Zhang（微软），Kai Wang（字节跳动），另两位来自深圳大学和哈工大（深圳）。期刊 2024-11 出版 | 高 |
| A5 | WWW 2019 王者荣耀团队构成研究：9600 万场、1 亿玩家、含腾讯合著 | CONFIRMED（WWW'19 pp.2666–2672，DOI 10.1145/3308558.3313530；arXiv 版是长版。作者 Ziqiang Cheng, Yang Yang, Chenhao Tan, Denny Cheng, Yueting Zhuang, Alex Cheng） | 高 |
| A7 | Ubisoft "Beyond Skill Rating…Ghost Recon Online"，IEEE TCIAIG 4(3):167–177，2012 | CONFIRMED（只确认了书目，内容未核） | 中 |
| A8 | Josh Menke（时任 Activision）GDC 2016 "Skill, Matchmaking, and Ranking Systems Design" | CONFIRMED（GDC 2015 公告称他为 Activision senior systems designer） | 高 |

### 对 DeepBattler 相关推论的修正
| # | 主张 | 结论 | 置信度 |
|---|------|------|--------|
| I1 | 问题五推论："BG 中'长期分数'会因保底加分而缓慢上漂" | CORRECTED（需区分时期）：2019–2020-09 只有一个评分，保底加分直接作用于匹配用的评分；18.4（2020-09）起，加分**只加在外显评分上**，内部（匹配）评分"no floors or bonus"。所以现行系统中上漂的只是显示分，不影响匹配 | 中高 |

## 二、详细说明（只列有更正或需特别注意的条目）

**P15：US 12,533,594 属于字节跳动，不是腾讯。** 检索 "Method and apparatus for game matching, storage medium, and electronic device" 和公开号 US20230381666 时，Google Patents 摘要两次都给出 Original Assignee: Beijing ByteDance Network Technology Co Ltd。GlobalData/Verdict 也报道过字节跳动申请"game team matching"专利（没有点名这一件）。报告里应把它移出"腾讯"小节。来源：https://patents.google.com/patent/US12533594 ；https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12533594 ；https://www.verdict.co.uk/?p=346347

**P16：CN112221161B 的权利人仍未知。** 我用中文标题、申请号、"腾讯"关键词检索了 4 次，Google Patents 摘要都在申请人字段之前就截断了。建议报告只写"一件中国授权专利（权利人待查）"，或干脆删去。来源：https://patents.google.com/patent/CN112221161B/zh

**P12 和补充：TrueSkill 专利链。** US 7,050,868（2006）和 US 7,376,474（2008，"Bayesian scoring"，Graepel、Herbrich）是原始的 TrueSkill 专利。US 8,538,910（2013）的说明书自称是在 "our earlier Bayesian Scoring system… commercially available under the trade name TrueSkill" 基础上做的加速改进。另外，微软还有 US 8,672,764 "Adaptive matchmaking for games"（2014-03-18；Graepel、Herbrich、Shaw），它按"实际等待时间 vs 目标等待时间"带阻尼地调整匹配阈值，是"排队时间换匹配质量"的一手专利证据。注意：有一条检索摘要曾把它误标为 Riot 的专利。来源：https://patents.justia.com/patent/7376474 ；https://patents.google.com/patent/US8538910B2/en ；https://patents.google.com/patent/US20080242420

**P13：Riot 11,484,801 就是 "Activity-factored team formation"。** Justia 摘要："Activity-factored team formation in multiplayer online gaming… Filed: March 23, 2021; Date of Patent: November 1, 2022"。eXputer 报道的 2022-09 公开文本是同一件申请。来源：https://patents.google.com/patent/US11484801 ；https://patents.justia.com/inventor/lawrence-lihuan-xie ；https://exputer.com/news/industry/riot-games-patent-better-team-formation/

**C5：90%/10% 数字。** Activision PDF（https://www.activision.com/cdn/research/CallofDuty_Matchmaking_Series_2.pdf）的摘要确认了试验设定：early 2024、MWIII、北美、50% 处理组、放宽而非移除技能约束。多家媒体（PC Gamer、Game Developer 转载页、TechRadar、VGC、Hitmarker）一致报道"按技能等分 10 组，只有最高 10% 回流增加，其余 90% 回流显著下降"，并引用了 "top 10% → top 20% → top 30%" 的连锁流失论证。但 "90% 的组下降" 这句在 Activision 原文中的逐字措辞我没有看到，报告引用时应写成"据 Activision 白皮书（媒体转述）"。TweakTown 和 wnhub 写的"回流率下降 90%"是误读，不要采用。另有一份摘要提到 Activision 也做过"收紧技能"的反向试验，效果相反（高手流失增加），只有单一模糊摘要，未采用。

**B3/B5/I1：酒馆战棋 6500 保底加分的两个时期。** 2019 原帖（23239989）："In theory, playing more games… will give you a small advantage in terms of 'boosting' your rating (if you are below 6500 rating)"。2020 年 18.4 更新帖（23523064）把它限定在外显评分上（"if your external rating is below 6500, we will give you a very small value of positive rating gain… 53 or 47"），并说明内部评分没有保底也没有加分。原笔记把两个时期混在一起，因此推论 I1 需要修正。

**B6：2019-12 的 MMR 调整已回滚。** HearthstoneTopDecks："(REVERTED) More Battlegrounds MMR Changes Live…"；"Yesterday's Battlegrounds MMR Changes Reverted – Rating Will Work Like It Did Before Update"。来源：https://www.hearthstonetopdecks.com/yesterdays-battlegrounds-mmr-changes-reverted-rating-will-work-like-it-did-before-update/ ；https://www.icy-veins.com/forums/topic/47288-battlegrounds-mmr-updates-december-5th/

**H4/H5/H8：王者荣耀三处出处问题。** (1) 4-07 是原告"在新媒体账号发布最新进展"的日期（17173、同花顺、扬子晚报 4-08 的报道均如此表述），判决书作出日期未公开报道。(2) "没有任何动机去干预……"出自 2018 年《狄仁杰答疑》（广州日报/羊城晚报 ycwb 稿与虎嗅转引）。(3) 66.8%→99.6%、36.1%→90.7% 出自 2026-08-12/13 的"对局环境优化专栏"报道（17173 转游民星空、快科技），原文写的是"此前的匹配优化把……"。来源：https://news.17173.com/content/04082026/171630771.shtml ；https://news.ycwb.com/ikimvkjtil/content_53930644.htm ；https://news.17173.com/content/08132026/020132459.shtml ；https://www.ithome.com/0/910/430.htm

**P3：Deej 推文。** GameSpot、MP1st、Push Square 引用的推文原文是 "None of this functionality appears in Destiny."；mein-mmo 等德语媒体的标题写了"Destiny 2 angeblich nicht betroffen"。报告应写"Bungie 称 Destiny 中没有此功能"。

**X2：Apex 分桶。** EA 博文原文："Apex Legends uses the Bucket approach, but that is changing… retiring our old Skill Based Matchmaking (SBMM) system for a new one that more accurately groups our players based on skill." 来源：https://www.ea.com/games/apex-legends/news/matchmaking-2023

## 三、原笔记缺失、但会实质加强报告的事实

1. **字节跳动也有"游戏匹配"美国专利**（US 12,533,594，见 P15）；**CUPID 论文的作者也跨腾讯、微软、字节**。"中国厂商匹配研究"不止腾讯和网易两家。
2. **TrueSkill 的原始专利是 US 7,050,868 / 7,376,474**；**微软 US 8,672,764 "Adaptive matchmaking for games"** 是按等待时间动态放宽匹配阈值的专利（见上）。
3. **EA 匹配专利比笔记列的更多**：US 11,141,663（10,610,786 的续案，2021-10-12）、US 11,071,909 与 US 11,845,005 "Game quality-centric matchmaking for online gaming"（发明人 Labate、Waller、Karlsen 等）、US 11,478,715（见 P17）、DDA 续案 US 11,369,880。EA 至少有 4 条与匹配/难度相关的专利家族，并且持续在申请续案。来源：https://patents.justia.com/inventor/glenn-arne-karlsen ；https://patents.google.com/patent/US11141663B2/en
4. **Activision US 10,322,351 的说明书附图中有一幅"通过匹配影响游戏内购买"的流程图**（与 9,789,406 同族、共用说明书）。所以"未见部署证据"之外，还应说明：付费导向匹配的思路在 Activision 这一整族专利中都出现过。来源：https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10322351 （检索摘要列出的附图目录）
5. **Riot 11,065,547 源自 2012 年申请的 US 9,795,887**（Jeffrey Lin 的行为/荣誉体系团队），可以说明 Riot 从 2012 年起就为"按行为数据匹配"申请保护。它和 Phroxzon 2025 年说"不按 honor score 匹配"并不矛盾（专利不代表部署），但值得并列写出。
6. **OW2 官方承认加入了 "streak modifier"**（part 1），即"连胜/连败影响评分更新速度"，与 Valorant 的 variance 说明属于同类，可加强笔记推论"连胜效应在评分侧而非匹配侧"。
7. **王者荣耀判决的附加内容**：法院认定游戏不涉及社会公共利益，不能参照其他互联网平台的算法公开义务；同时建议运营商可提供"关闭算法推荐"、引入社会监督、人工干预与投诉渠道。

## 四、酒馆战棋（Battlegrounds）MMR / 匹配：补充资料（按来源分级）

**官方（Blizzard 开发者洞察/补丁说明/论坛蓝帖）**
- 2019 年末《Personal Rating in Hearthstone Battlegrounds》（Tian，Senior Data Scientist）：Elo/Glicko 为两人对局设计，不适用 8 人；模拟中自研算法最快且最准；每人有评分和隐藏方差（新手高，随对局下降，意外结果会让方差回升）；赛后变化取决于自身评分、对手评分、名次、预测胜率、方差等；每局算 56 个两两胜率；6500 以下每局有小额正向进度加分。11-19 改动后，同分大厅中首局第一约 +195（论坛帖 190），第 150 局以后约 +98（论坛帖 95），原先为 +240/+24。https://hearthstone.blizzard.com/en-us/news/23239989
- 2019-12-05 高分段 MMR 调整（大厅平均分偏离自身时放大倍率；计划把 5500 以上压回 5500）误上线后，于 12-06 **回滚**。https://www.hearthstonetopdecks.com/yesterdays-battlegrounds-mmr-changes-reverted-rating-will-work-like-it-did-before-update/
- 2020 年 Iksar（Dean Ayala）谈组队：正在收集"组队相对单排优势"的数据，备选方案包括高 MMR 禁止组队、组队只匹配组队、分队列。https://outof.games/news/1873-dean-ayala-talks-battlegrounds-parties-and-matchmaking-fairness-mmr-reset-coming/
- 2020-09 18.4《Rating System Update》（双评分制）：外显评分每赛季清零，≤2000 不掉，2000–6000 每 500 一道保底，单局外显最多 +300；外显低于内部评分时按倍率追赶；6500 以下的进度加分只加在外显上；内部评分永不重置、无保底、无加分，呈钟形分布、可能归一化；匹配时"try to select eight players with the closest internal rating"，外显评分"plays no role in the matchmaking process"。https://hearthstone.blizzard.com/en-us/news/23523064 ；https://articles.hsreplay.net/2020/09/28/patch-notes-18-4/
- 约 2022（23.2 补丁前后）John McIntyre《Developer Insights: Battlegrounds Balance》给出活跃玩家（近 20 天 ≥5 局）MMR 分布：前 50% 为 5700，前 25% 为 6500，前 10% 为 7000，前 1% 为 8300（赛季末测量）；并指出普通玩家与前 1% 玩家的"前 10 强英雄"几乎完全不同。https://us.forums.blizzard.com/en/hearthstone/t/87311/1 ；https://www.hearthstonetopdecks.com/developer-insights-battlegrounds-balance/
- 2024-04 第 7 赛季引入双人模式（Duos）：单人与双人**评分、排行榜完全分开**，新赛季评分重置。https://hearthstone.blizzard.com/news/24064742
- 赛季重置一直持续到至少 2023 年的 25.2（第 3 赛季），此后每个新赛季都重置外显评分。未检索到 2025–2026 年对评分规则的官方修改公告。

**第三方/社区（未经官方确认）**
- 计算器（West Games）自称"rating formulas are not fully public"，其中第一名 +96 等名次表只是模型假设。https://west-games.com/hearthstone-battlegrounds-win-rate-calculator/
- esports.gg 攻略称"一般第一名约 +100"，并说高分玩家赢下低分大厅加分更少、输得更多；论坛玩家报告 5.5k 时第一名 +103、某局第一名只 +77。https://esports.gg/guides/hearthstone/hearthstone-battlegrounds-rating-system-mmr-and-matchmaking/ ；https://us.forums.blizzard.com/en/hearthstone/t/only-ever-getting-103-mmr-for-first/42575
- 代练站给出的区间（第一 +80~120，第 2–4 名 +20~60，第 5–8 名 −20~−80）没有方法说明，不可引用为事实。
- 没有找到可靠的社区逆向工程公式（HSReplay、Firestone 均未检索到 BG 评分公式研究）。"前四加分、后四扣分"只是社区经验法则，官方帖只说变化取决于名次相对预期的表现。

**对 DeepBattler 的含义（推论）**：官方只说明匹配看"最接近的内部评分"，没有任何基于近期胜负或连胜的匹配干预说明。评分更新是"名次 vs 预测"的 8 人模型加方差。现行系统下，6500 以下的加分和各档保底只影响外显分。所以用天梯分评估 AI 时，应尽量用**同一赛季、相近外显分区间、足够多局的平均名次/前四率**，而不是外显分的绝对值。如果比较跨赛季的外显分，赛季重置后的"追赶倍率"会造成系统性偏差。

## 五、主要来源
- 专利：https://patents.google.com/patent/US12533594 ；https://patents.google.com/patent/US10751629 ；https://patents.google.com/patent/US11484801 ；https://patents.google.com/patent/US11065547 ；https://patents.google.com/patent/US8538910B2/en ；https://patents.justia.com/patent/7376474 ；https://www.patentarcade.com/?p=5555 ；https://www.patentarcade.com/video-game-patent/US10322351/matchmaking-system-and-method-for-multiplayer-video-games ；https://patents.justia.com/assignee/activision-publishing-inc?page=8 ；https://companyprofiles.justia.com/company/electronic-arts/patents/patent?page=16 ；https://trea.com/person/su-xue/information/23020e6a-8c4a-4041-a04e-1841a4f33ec7
- Activision/Bungie：https://www.gamespot.com/articles/activision-clarifies-its-patent-for-encouraging-mi/1100-6454147 ；https://mp1st.com/news/call-of-duty-matchmaking-used-by-activision-to-encourage-players-to-buy-microtransactions ；https://www.pushsquare.com/news/2017/10/microtransactions_are_being_implemented_in_the_scariest_of_ways
- EA 诉讼：https://www.truthinadvertising.org/wp-content/uploads/2021/03/Zajonc-v-Electronic-Arts-complaint.pdf ；https://www.pocketgamer.biz/dynamic-difficulty-class-action-lawsuit-against-ea-gets-dropped ；https://www.videogameschronicle.com/news/ea-loot-box-lawsuit-dropped-after-company-convinces-lawyers-it-doesnt-adjust-difficulty ；https://ea.com/amp/news/fair-play-and-dynamic-difficulty-adjustment ；https://www.pcgamer.com/uk/class-action-lawsuit-claims-eas-dynamic-difficulty-tech-encourages-loot-box-spending/
- CoD：https://www.callofduty.com/blog/2024/01/call-of-duty-update-an-Inside-look-at-matchmaking ；https://www.callofduty.com/blog/2024/07/call-of-duty-matchmaking-intel ；https://www.activision.com/cdn/research/CallofDuty_Matchmaking_Series_2.pdf ；https://gamespot.com/articles/no-your-call-of-duty-matchmaking-conspiracy-theory-isnt-true-activision-insists/1100-6520677/ ；https://www.tweaktown.com/news/99605/activision-ran-secret-experiment-with-50-of-call-dutys-players/index.html ；https://www.callofduty.com/patchnotes/2025/10/call-of-duty-black-ops-7-beta-patch-notes
- Blizzard：https://hearthstone.blizzard.com/en-us/news/23239989 ；https://hearthstone.blizzard.com/en-us/news/23523064 ；https://overwatch.blizzard.com/en-us/news/23896785 ；https://overwatch.blizzard.com/en-us/news/23910161 ；https://devtrackers.gg/overwatch/p/52b2b895-overwatch-2-developer-blog-explaining-matchmaker-goals-and-plans-part-2
- Riot/Valve：https://nexus.leagueoflegends.com/en-us/2018/02/dev-matchmaking-real-talk/ ；https://ggscore.com/en/lol/news/70213 ；https://www.oneesports.gg/valorant/losers-queue-valorant-ranked-shroud/ ；https://www.oneesports.gg/valorant/ranked-mmr-hard-stuck-valorant-dev/ ；https://steamcommunity.com/app/570/discussions/0/4846526931624468081 ；https://pcgamesn.com/dota/dota-2-set-ranked-matchmaking ；https://afkgaming.com/csgo/guide/6825-csgo-ranks-explained-2021-how-ranking-system-works-tips-for-good-rank-complete-guide
- 王者荣耀：https://www.yzwb.net/news/sh/202604/t20260408_339832.html ；https://stock.10jqka.com.cn/20260408/c675813550.shtml ；https://news.17173.com/content/04082026/140318558.shtml ；https://www.36kr.com/p/3421408367627905 ；https://www.huxiu.com/article/4697662.html ；https://news.ycwb.com/ikimvkjtil/content_53930644.htm ；https://www.invenglobal.com/articles/20748/the-persistent-50-win-rate-conspiracy-what-did-the-chinese-court-decide
- 论文：https://ir.webis.de/anthology/2017.wwwconf_conference-2017.118/ ；https://dblp.org/pid/223/3141 ；https://ojs.aaai.org/index.php/AAAI/article/view/28760 ；https://api.crossref.org/works/10.1145%2F3686978 ；https://arxiv.org/abs/2406.19720v1 ；https://ir.webis.de/anthology/2019.wwwconf_conference-2019.248/ ；https://www.microsoft.com/en-us/research/publication/trueskill-2-improved-bayesian-skill-rating-system/ ；https://gdcvault.com/play/1023014/Skill-Matchmaking-and-Ranking-Systems
- 其他：https://www.ea.com/games/apex-legends/news/matchmaking-2023 ；https://insider-gaming.com/marvel-rivals-does-not-use-eomm-says-netease-games/ ；https://siege.gg/marvel-rivals/what-is-eomm-in-marvel-rivals ；https://www.halowaypoint.com/news/closer-look-halo-infinites-ranked-experience ；https://lichess.org/page/rating-systems ；https://stevivor.com/news/fornite-matchmaking-goes-skill-based-adds-bots/
