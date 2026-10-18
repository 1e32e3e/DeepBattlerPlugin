# 行业披露、专利与公司论文：各游戏/公司的评分与匹配机制（Part 1b）

> 研究方法说明（供报告撰写者参考）：本轮调研中 WebFetch 与 curl 均无法访问外网（DNS/代理 403），因此**所有条目均来自搜索引擎返回的页面摘要**，未能逐字通读原始页面。引号内英文为搜索摘要中给出的原文片段；数字与日期如与原文有出入，以原文为准。标签含义：【官方披露】=开发商官方博客/白皮书/官方人员公开发言；【专利】；【公司论文】=公司员工署名的学术论文/技术报告；【第三方分析】=媒体、独立研究者、第三方工具；【社区推测】=玩家论坛/攻略/自媒体。截至 2026 年 10 月。

## 问题一：各游戏开发商官方披露了什么（评分模型、隐藏分 vs 可见段位、团队实力处理、连胜/连败调整、是否以 50% 胜率为目标）

### Takeaway
几乎所有主流开发商（Riot、Valve、Blizzard、Activision、Respawn、Epic、Krafton、343/Microsoft、Tencent、NetEase/Marvel Rivals）的官方口径一致：匹配器以**隐藏 MMR**为主要依据、目标是让**单局双方预期胜率接近 50%**，并明确否认"强制长期 50% 胜率""输家队列""连胜后塞坑队友"；"长期胜率趋近 50%"被官方解释为"每局都公平"的数学后果而非设计目标。官方确实承认的"非纯实力"因素主要是：网络延迟（CoD 中权重最高）、排队时间、新手/回流玩家的初始分与不确定度（σ/variance）、组队处理、分路/位置、以及部分休闲模式中随实力递减的机器人（Fortnite、PUBG）。

### Cited Findings

**Riot Games — 英雄联盟（League of Legends）**
- 【官方披露｜2018-02】Riot Nexus 开发者博文 "/dev: Matchmaking Real Talk" 称匹配系统的目标是预期胜率接近 50%，"most teams have an expected win rate of 50 +/-1%"；同时承认原始数据会漏掉陌生位置、预组队、小号（smurf）、状态不佳等因素，并认为"运气差"的感受很大程度是感知问题。— [Riot Nexus 2018](https://nexus.leagueoflegends.com/en-us/2018/02/dev-matchmaking-real-talk/)（经搜索摘要转述）
- 【官方披露｜2025 年 7 月前后，15.14 补丁预告】首席玩法设计师 Matt "Phroxzon" Leung-Harrison 在 X 上称："We're not matching you on your honor score, your number of pings, your runes, whether you're on a loss streak or any of that"；匹配只用 MMR，并尽量做到双方"同位置对位"（on-role parity）。— [GGScore](https://ggscore.com/en/lol/news/70213)；[EarlyGame](https://earlygame.com/news/lol/losers-queue-doesnt-exist)
- 【官方披露｜某年 10 月视频，年份未核实】Phroxzon 称系统不会在连胜后故意给弱队友以"强制 50% 胜率"，连胜/连败感是系统的自然副产品；并承认匹配同时要压低排队时间，偶尔会放宽实力跨度。— [EarlyGame](https://earlygame.com/news/lol/losers-queue-doesnt-exist)
- 【官方披露｜Reddit，日期未核实】Riot 员工 Auberaun 回应"故意不公平"指控："No, we don't do that. Aim for as close to 50% every time"，并称胜率不是分配玩家的标准。— [Dot Esports](https://dotesports.com/league-of-legends/news/riot-dev-responds-to-claims-league-ranked)
- 【第三方分析｜2015】NERFPLZ 汇总 Riot 当年说法：不存在"连败岛"（Losing Streak Island），连败之后下一局胜率仍为 50% 左右。— [NERFPLZ 2015](https://www.nerfplz.com/2015/05/riots-losing-streak-island-prisoner.html)

**Riot Games — VALORANT**
- 【官方披露｜日期未核实（Ask VALORANT – Rank Rating Edition）】Competitive Designer Jon Walker 与制作人 Ian Fielding：MMR 隐藏、玩家永远看不到；可见的 Rank Rating（RR）与 MMR 分离；当 MMR 高于显示段位时赢得多、输得少。新/回流玩家被放在"我们认为你所属区间的低端"。— [playvalorant.com](https://playvalorant.com/en-us/news/dev/ask-valorant-rank-rating-edition/)；[AFK Gaming](https://afkgaming.com/esports/news/7187-valorant-devs-explain-how-ranked-rating-and-mmr-works)
- 【官方披露】Senior Competitive Designer EvrMoar 解释 MMR 的不确定度（variance）机制：表现符合预期时 variance 收缩、MMR 难以移动；表现超出预期时 variance 放大、MMR 快速移动——"This is why win-streaking, and why winning duels against higher-ranked players, really helps you climb"。即**连胜加速的是"评分调整"，不是"匹配惩罚"**。— [AFK Gaming](https://afkgaming.com/esports/news/6197-riot-dev-reveals-how-valorants-mmr-system-really-works)
- 【官方披露｜2022】EvrMoar 回应 Shroud："There is no loser's queue in Valorant… We do not manipulate the queue"，并称匹配目标是找到"互相有 50% 胜率"的两队。另一次（5 月 14 日排位热修后，年份未核实）称 winners/losers queue "There is no such thing"，认为是确认偏误。— [ONE Esports](https://www.oneesports.gg/valorant/losers-queue-valorant-ranked-shroud/)；[Dexerto](https://www.dexerto.com/valorant/riot-responds-valorant-ranked-backlash-1575392)

**Valve — Dota 2**
- 【官方披露｜Valve Dota 2 博客 "Ranked Matchmaking" 帖，原帖日期未在检索中确认】匹配器一直在计算 MMR，天梯只是让其可见；天梯 MMR 与普通 MMR 分开；天梯 MMR 仅自己和好友可见，普通 MMR 不可见；10 场定级；"win/loss is the primary criteria used to update MMR, but individual performance also plays a role, especially when our uncertainty about your MMR is high"；个别情况下输了也可能涨分、赢了也可能掉分。— [GosuGamers](https://gosugamers.net/dota2/news/26227-ranked-matchmaking-and-mmr-coming-to-dota-2)；[PCGamesN](https://pcgamesn.com/dota/dota-2-set-ranked-matchmaking)；[DotaFire 转载](https://www.dotafire.com/dota-2/forum/news/matchmaking-4493)
- 【官方披露（经论坛转引）｜日期未核实】Valve 开发者 Jeff Hill：匹配器优化的是"每一局都平衡（双方预测胜率相等）"，"a 50% lifetime win rate isn't an explicit goal or constraint of the matchmaker, rather it's a consequence of trying to make the teams for each individual game fairly"；语言、延迟、行为分、场次等非 MMR 因素用于提升对局质量而非改变胜负概率。该引述来自 Steam 讨论帖转引，非 Valve 原帖。— [Steam 社区](https://steamcommunity.com/app/570/discussions/0/2789369598124752294)；[ESCORE（俄文）](https://escorenews.com/ru/dota-2/article/25530-prinuditelnyj-vinreyt-v-50-mif-razrabotchik-dota-2-podelilsya-podrobnostyami-o-matchmeykinge)
- 【官方披露（经媒体转述）】第二个天梯赛季的重新定级中，Valve 开发者表示移除了"个人表现加分"。— [GosuGamers](https://www.gosugamers.net/dota2/features/47277-pain-and-gain-analyzing-the-new-re-calibration-system)

**Valve — CS:GO / CS2**
- 【官方披露（非正式，约 2015 年 Reddit 员工评论）】Valve 员工称 CS:GO 段位计算"started with ideas based on the Glicko-2 rating model"并随后针对玩家群体改进，结果在后端以 Skill Group 形式呈现；Valve 从未正式发布算法。— [PC Gamer](https://pcgamer.com/csgo-ranks-explained)；[AFK Gaming](https://afkgaming.com/csgo/guide/6825-csgo-ranks-explained-2021-how-ranking-system-works-tips-for-good-rank-complete-guide)
- 【第三方分析｜2024】arXiv 论文将 Valve 方法描述为"an unpublished variant of the Glicko2 rating system"。— [arXiv 2410.02831](https://arxiv.org/html/2410.02831v1)
- 【第三方分析】CS2 Premier 的 CS Rating 为连续、开放上限的 Elo 式数字；已确认的输入只有胜负与对方队伍平均分相对自己的高低；"回合差影响分数"属社区推测；Valve 未公布 Premier 公式，也未公布与 CS:GO 段位的对应关系；有报道称 Valve 曾通过提高胜场加分"通胀"分布。— [wecoach.gg](https://wecoach.gg/blog/article/cs2-ranks-premier-rating-and-competitive-system-explained-2026)；[ESCORE](https://escorenews.com/en/csgo/news/53226-rank-distribution-reportedly-changes-in-cs2-as-valve-inflates-the-system-with-more-elo-points-for-winning-in-premier-mode)；[csdb.gg](https://csdb.gg/de/guides/cs2-premier-rank-equivalent/)

**Blizzard — Overwatch 2**
- 【官方披露｜2023（任务方称 2023 年深度博文；搜索未显示精确日期）】"Matchmaker and competitive deep dive, part 1"：每名玩家有内部 MMR；"all our game modes, including Competitive, only look at MMR when forming a match"；新玩家初期输得过多，目标是让新手胜率分布以 50% 为中心；先把初始 MMR 设在略低于平均，再下调到约 Bronze 5 等价，此后"instantly saw huge improvements for new players with a sub-40% win-rate"；初期对局采用更快的 MMR 调整速度。— [Overwatch 官方](https://overwatch.blizzard.com/en-us/news/23896785)；[Blizzard News](https://news.blizzard.com/en-us/article/23896785/overwatch-2-developer-blog-matchmaker-and-competitive-deep-dive-part-1)；[EGM](https://egmnow.com/overwatch-2-devs-admit-matchmaking-is-broken-pledge-to-fix-it/)
- 【官方披露｜2023】"Explaining matchmaker goals and plans, part 2" FAQ：匹配器**不**对任何玩家强制 50% 胜率；**不存在**赢家/输家队列；"Your current MMR is the only thing the matchmaker takes into consideration when forming your matches"；极长的连胜/连败"is indicative that their internal rating is not well-calibrated"，也可能只是短期运气；团队表示正在测试减少此类"streaking"的改动。— [Overwatch 官方 part 2](https://overwatch.blizzard.com/en-us/news/23910161)
- 【第三方分析】EGM 指出博文未解释为何可见段位滞后于隐藏 MMR（当时需 7 胜或 20 负才更新段位）。— [EGM](https://egmnow.com/overwatch-2-devs-admit-matchmaking-is-broken-pledge-to-fix-it/)
- 【社区推测｜2023-02~03】一名玩家用 202 场第 3 赛季数据声称胜率移动平均呈"周期性"而非收敛；单人、单平台样本，属轶事。— [Blizzard 论坛](https://us.forums.blizzard.com/en/overwatch/t/mmr-fails-to-converge-shows-conspicuous-periodicity)

**Blizzard — Hearthstone（构筑/竞技场）**
- 【官方披露｜约 2015】首席设计师 Ben Brode：竞技场匹配只看胜负战绩（新玩家除外），竞技场无 MMR。— [Icy Veins](https://www.icy-veins.com/forums/topic/20151-hearthstones-ben-brode-clarifies-that-there-is-no-mmr-in-arena/)
- 【第三方分析｜2020-04 天梯改版】新天梯为 5 个联赛×10 级+传说，每级 3 星、输一局掉一星、每联赛 10 级与 5 级为保底；"Matchmaking is decided by MMR"；月初重置到青铜 10，并按上月 MMR 与段位给予"星级加成"（winning-star multiplier）。MMR 不跨赛季重置、对玩家隐藏（维基说法）。— [Hearthstone Wiki – Ranked](https://hearthstone.wiki.gg/wiki/Ranked)；[Hearthstone Wiki – MMR](https://hearthstone.wiki.gg/wiki/MMR)；[PC Gamer](https://pcgamer.com/uk/new-hearthstone-ranking-system)

**Blizzard — Hearthstone Battlegrounds（酒馆战棋，8 人）**
- 【官方披露｜酒馆战棋公测期，约 2019 年末】"Developer Insights: Personal Rating in Hearthstone Battlegrounds"：明确说明 Elo、Glicko 主要为两人对局设计，"not a good option for us"；Blizzard 自研算法在模拟中"had the fastest runtime… and the highest accuracy"；每名玩家有评分+隐藏方差（variance，新手高、随对局下降）；赛后评分变化取决于自身评分、对手评分、名次、预测胜率、方差等；每局需计算 8 人两两胜率共 56 次；6500 分以下每局有小幅"保底加分"（无论胜负）。— [Hearthstone 官方 23239989](https://hearthstone.blizzard.com/en-us/news/23239989)；[HearthstoneTopDecks 转载](https://www.hearthstonetopdecks.com/developer-insights-personal-rating-in-hearthstone-battlegrounds/)
- 【官方披露｜后续更新，日期未核实】"Battlegrounds Rating System Update"：区分内部评分与外显评分，"we will try to select eight players with the closest internal rating… external rating plays no role in the matchmaking process"。— [Hearthstone 官方 23523064](https://hearthstone.blizzard.com/en-us/news/23523064)
- 【官方披露（经论坛转引）｜11 月 19 日改动】假设对手同分：原系统首局第一名约 +240、第 150 局起约 +24；改后首局约 +195（另一转引为 190）、第 150 局起约 +98（另一转引为 95）。两处转引数字略有出入。— [Blizzard 论坛](https://us.forums.blizzard.com/en/hearthstone/t/battlegrounds-ranking-points/17554)；[Icy Veins（12 月 5 日 MMR 更新，含高分段调整与"MMR 归一化"设想）](https://www.icy-veins.com/forums/topic/47288-battlegrounds-mmr-updates-december-5th/)
- 【社区推测】玩家经验法则：前四加分、后四扣分，变化幅度取决于大厅平均分；大幅高于大厅时第一名加分少、第四名甚至可能扣分；实测高分段第一名约 +100 左右。第三方计算器（West Games）给出的 +96/+68 等名次表未经验证。— [Blizzard 论坛](https://us.forums.blizzard.com/en/hearthstone/t/battleground-mmr-question/18736)；[Blizzard 论坛 103 MMR](https://us.forums.blizzard.com/en/hearthstone/t/only-ever-getting-103-mmr-for-first/42575)；[West Games 计算器](https://west-games.com/hearthstone-battlegrounds-win-rate-calculator/)

**Blizzard — StarCraft II**
- 【官方披露｜2013】"Situation Report: The StarCraft II Multiplayer Ladder"：隐藏评分决定联赛定位；引入"MMR decay"（长期不玩后轻微下调隐藏分），原因是回流玩家常遭连败；目标是让联赛人口分布接近设定比例。— [starcraft2.com](https://starcraft2.com/news/12055065)
- 【第三方分析｜2016】Blizzard 天梯改版使 MMR 更可见、联赛分档。— [Ubergizmo](https://ubergizmo.com/2016/06/starcraft-2-ladder-to-get-revamp)
- 【社区推测】"匹配让双方胜率约 50%"的说法出自 Team Liquid 社区指南；暂定（provisional）MMR 约 25 场后消失之说来自论坛版主。— [Team Liquid](https://tl.net/forum/starcraft-2/311954-understanding-mmr)；[Blizzard 论坛](https://us.forums.blizzard.com/en/sc2/t/matchmaking-system/1781)

**Activision — Call of Duty**
- 【官方披露｜2024-01，2024-04-04 更新】CoD 官方博客 "An Inside Look at Matchmaking"：连接质量（ping/Delta Ping）权重最高，其次是匹配用时，技能只是因素之一；匹配不考虑游玩时长/频率；媒体报道开发团队称"money spent is in no way a factor in multiplayer matchmaking"（英文原文片段未在摘要中直接看到，此点依赖媒体转述）。— [callofduty.com](https://www.callofduty.com/blog/2024/01/call-of-duty-update-an-Inside-look-at-matchmaking)；[Windows Central](https://www.windowscentral.com/gaming/ping-is-king-call-of-duty-modern-warfare-3-multiplayer-matchmaking-is-demystified-in-the-latest-intel-drop)；[TechRadar](https://www.techradar.com/gaming/consoles-pc/call-of-duty-matchmaking-consists-of-many-factors-with-connection-being-the-most-critical)
- 【官方披露｜白皮书系列】#1 Ping（2024-04）；#2 "The Role of Skill in Matchmaking"（2024-07，博客 2024-07-26）；#3 Ranked Play（PDF 日期 2024-12-23）；原计划中的 "Experimentation Methods" 篇未检索到发布记录。— [Activision Research #1](https://research.activision.com/publications/2024/04/callofduty-matchmaking-intel-ping)；[#2](https://research.activision.com/publications/2024/07/Call-of-Duty-Matchmaking-Intel-02)；[#2 PDF](https://www.activision.com/cdn/research/CallofDuty_Matchmaking_Series_2.pdf)；[#3](https://research.activision.com/publications/2024/12/Call-of-Duty-Matchmaking-Intel-03)；[#3 PDF](https://activision.com/content/dam/atvi/activision/atvi-touchui/research/publications/docs/Ranked-Play-Matchmaking-Whitepaper-12-23-24.pdf)
- 【官方披露｜白皮书 #2 内容，经媒体转述】组局时技能目标比 Delta Ping 目标放宽得更快；在《MWIII》北美进行"Deprioritize Skill Test"，50% 玩家进入放宽技能约束的处理组；测量持续游玩、局内退出率、问卷与比赛结果；一个月后按技能分十组，**90% 的组回流率显著下降，只有技能最高的 10% 回流增加**；Activision 认为若持续下去高手最终也会流失；"players who frequently experience blowouts are seen to quit matches in progress and the game itself"。— [Game Developer](https://www.gamedeveloper.com/design/deprioritizing-skill-based-matchmaking-turned-call-of-duty-into-the-bad-place)；[PC Gamer](https://www.pcgamer.com/games/activision-secretly-experimented-on-50-of-call-of-duty-players-by-decreasing-skill-based-matchmaking-and-determined-players-like-sbmm-even-if-they-don-t-know-it/)；[MMORPG.com](https://www.mmorpg.com/news/players-ragequit-without-skill-based-matching-according-to-activision-white-papers-with-ab-testing-2000132327)；[esports.gg](https://esports.gg/news/call-of-duty/skill-based-matchmaking-is-good-for-call-of-duty/)
- 【第三方分析】TechSpot 批评该实验是"秘密"降低 SBMM 以"证明"玩家偏好 SBMM。— [TechSpot](https://www.techspot.com/news/104027-activision-secretly-reduced-skill-based-matchmaking-call-duty.html)
- 【官方披露｜2023-02 MWII 天梯】SR 决定分段，个人与团队表现都会影响加减分；连胜仅有外观奖励"Hot Streak Flames"（72 小时内 3 连胜以上），不加 SR；BO6 天梯移除段位保护星等旧机制。— [callofduty.com MWII Ranked](https://callofduty.com/blog/2023/02/call-of-duty-modern-warfare-II-ranked-play-features-challenges-rewards)；[Activision Support BO6](https://support.activision.com/black-ops-6/articles/black-ops-6-ranked-play)
- 【官方披露｜2025 年 Beta 至 11 月上线】《Black Ops 7》在 Beta 推出"Open Moshpit"（"skill consideration is drastically reduced"），上线后播放列表分为 Open（技能"minimally considered"）与 Standard（技能为"important consideration"），多数列表默认 Open；并引入持续大厅。媒体对"是否等于取消 SBMM"解读不一。— [PureXbox](https://www.purexbox.com/news/2025/11/call-of-duty-dev-clarifies-skill-based-matchmaking-options-in-black-ops-7)；[KitGuru](https://www.kitguru.net/gaming/mustafa-mahmoud/black-ops-7-beta-adds-new-mode-which-drastically-reduces-skill-based-matchmaking/)；[MP1st](https://mp1st.com/news/playlist-update-black-ops-7-beta-sbmm-takes-back-seat)；[Gfinity](https://www.gfinityesports.com/article/no-skill-based-matchmaking-in-call-of-duty-black-ops-7-multiplayer-at-launch)
- 【第三方分析】未找到 Activision 正式否认"使用 EOMM"的声明；"CoD 使用 EOMM"属社区推测、未经证实。— [esports.net](https://www.esports.net/news/cod/what-is-eomm-in-cod/)

**Respawn/EA — Apex Legends**
- 【官方披露｜2023-01，技术总监 Samy Duc】匹配博客：组队时以队内**最高技能玩家**的技能分为准，并考虑小队人数；技能分对玩家隐藏以防被利用；逐步淘汰旧 SBMM，改用更细粒度（更多分桶）的系统，已在部分地区的排位与匹配中上线。— [EA/Apex 官方](https://www.ea.com/games/apex-legends/news/matchmaking-2023)；[AFK Gaming](https://afkgaming.com/esports/news/apex-legends-matchmaking-woes-are-finally-being-addressed)
- 【官方披露｜2020】创意总监 Chad Grenier 为 SBMM 辩护：避免新手被碾压而流失。— [TheGamer](https://www.thegamer.com/why-apex-legends-skill-based-matchmaking-respawn-dev-explained/)

**Epic — Fortnite**
- 【官方披露｜2019-09，v10.40/第 11 赛季】Epic 宣布引入 SBMM（分地区逐步上线），并为新手加入机器人："as players improve in skill, they will face fewer bots"；竞技列表无机器人；后续说明跨平台/输入设备按相近技能分组。Epic 未公布技能评估算法细节。— [VGC](https://videogameschronicle.com/news/fortnite-is-adding-skill-based-matchmaking)；[EGM](https://egmnow.com/skill-based-matchmaking-and-bots-coming-to-fortnite/)；[EGM 后续回应](https://egmnow.com/epic-responds-to-feedback-about-fortnites-skill-based-matchmaking/)；[Complex](https://complex.com/pop-culture/2019/09/fortnite-skill-based-matchmaking-and-bots)

**Krafton — PUBG**
- 【官方披露｜2020，PC 7.2】普通模式加入机器人，"designed to appear less as your skill increases"，数量取决于"player skill"与服务器"matchmaking pool"；排位无机器人。— [Destructoid](https://www.destructoid.com/pubg-is-testing-ranked-mode-on-pc-and-bots-arent-invited/)；[KeenGamer](https://www.keengamer.com/articles/news/pubg-update-adds-bots-to-pc-to-shorten-player-skill-gaps/)
- 【官方披露｜Dev Letter "Matchmaking for Normal Match"（搜索摘要称 2024）】技能是普通模式匹配的输入之一（另有平台、地图轮换、组队类型、地区服务器），目标是匹配相近技能玩家。— [pubg.com Dev Letter](https://pubg.com/en/news/7174)

**343/Microsoft — Halo**
- 【官方披露】Halo Infinite：匹配使用按播放列表计算的 MMR（由 TrueSkill 2 计算），可见的 CSR "is not directly used in the matchmaking process"；CSR 变化还考虑个人表现及全场玩家 MMR。— [Halo Waypoint](https://www.halowaypoint.com/news/closer-look-halo-infinites-ranked-experience)；[Windows Central](https://www.windowscentral.com/how-halo-infinite-rank-and-csr-work)；[Halo Waypoint 排位更新](https://www.halowaypoint.com/news/halo-infinite-ranked-matchmaking-updates)
- 【官方披露】Microsoft Research 称 TrueSkill 2 首先随《Gears of War 4》上线，后用于 Halo 5、Gears 5、Halo Infinite、Forza Motorsport。— [MSR TrueSkill 项目页](https://www.microsoft.com/en-us/research/project/trueskill-ranking-system)

**Psyonix — Rocket League**
- 【第三方分析】隐藏 MMR/Skill Rating 决定段位，按播放列表与赛季独立；击败高分对手加分更多。检索中未找到 Psyonix 官方算法说明。— [Dot Esports](https://dotesports.com/rocket-league/news/rocket-league-mmr-and-ranking-system-explained)；[EarlyGame](https://earlygame.com/rocket-league/mmr-guide-match-making-rank/)

**国际象棋平台**
- 【官方披露｜Lichess 官方页面】Lichess 使用 Glicko-2，新账号 1500 起（初始 RD 很大，±1000 量级为论坛解释），且计算时考虑执黑加权；同页称 Chess.com 使用 Glicko-1（此为 Lichess 对他站的描述，非 Chess.com 自述）。Glicko/Glicko-2 由 Mark Glickman 提出且属公有领域。— [Lichess Rating Systems](https://lichess.org/page/rating-systems)；[Lichess 论坛](https://lichess.org/forum/general-chess-discussion/how-does-glicko-2-rating-works)；[glicko.net](https://www.glicko.net/glicko.html)

**EA — FIFA/EA SPORTS FC**
- 【官方披露｜FIFA 19 Division Rivals Pitch Notes】Rivals 核心为"a skill based ELO system"，按 Skill Rating 匹配，定级赛决定起始分段，每局持续校准。— [EA Pitch Notes FIFA 19](https://ea.com/games/fifa/news/fifa-19-ultimate-team-pitch-notes-division-rivals)
- 【官方披露｜FC 25】减少 Rivals 检查点以让对手更接近自身水平、顶部分段恢复降级、平局也计分。— [EA FC 25 Pitch Notes](https://www.ea.com/games/ea-sports-fc/fc-25/news/fc-25-community-update?cid=80807)

**NetEase — Marvel Rivals（漫威争锋）**
- 【官方披露｜2025 年 8 月中旬】官方声明游戏不使用 EOMM，并承诺进一步说明；创意总监 Guangguang 在 Rivals Assembled 访谈中否认 EOMM；随后由首席战斗设计师 Zhiyong 主讲的官方视频称匹配依据团队平衡与整体表现概率，输入包括阵容构成、竞技分、基础排位分、服务器节点，并处理离群值、服务器稳定性、常用角色。玩家仍普遍怀疑（"forced 50% win rate"之说）。— [Insider Gaming](https://insider-gaming.com/marvel-rivals-does-not-use-eomm-says-netease-games/)；[Siege.gg](https://siege.gg/marvel-rivals/what-is-eomm-in-marvel-rivals)；[Beebom](https://beebom.com/marvel-rivals-matchmaking-video-finally-answers-player-complaints-about-messy-lobbies/amp/)；[Gfinity](https://www.gfinityesports.com/article/netease-reveals-the-secret-to-fixing-your-marvel-rivals-losing-streak)；[AllThings.How](https://allthings.how/what-is-eomm-in-marvel-rivals-and-what-netease-says/)

**NetEase — 第五人格、永劫无间；Tencent — 和平精英**
- 【第三方分析】第五人格：B 站 Wiki 记载段位影响匹配、组队排位段位差上限两大段；攻略报道（2025-08）称排位做过"求生者遇到段位差距大的监管者可额外加分"、排位保护卡延长到 14 天等调整；未找到官方关于"隐藏分""连败"的正式说明。— [B 站 Wiki 排位模式](https://wiki.biligame.com/dwrg/%E6%8E%92%E4%BD%8D%E6%A8%A1%E5%BC%8F)；[17173 攻略](https://news.17173.com/content/08072025/201502955.shtml)
- 【检索结果为空】永劫无间：未找到官方对隐藏分/匹配/ELO 的正式说明。和平精英：攻略称光子工作室对"一局有多少人机"从未正面回应，人机数量随段位与在线人数变化（非官方）；澎湃 2023 年报道玩家体感真人数从 20 到 80 人不等。— [头条攻略](https://www.toutiao.com/zixun/7529370541652871203)；[澎湃新闻 2023](https://www.thepaper.cn/newsDetail_forward_21666428)

### Inferences
- 官方口径高度趋同的核心是一个可检验的区分：**"单局预期胜率≈50%"（官方承认）≠"个人长期胜率被强制到 50%"（官方否认）**。在纯 MMR 匹配下，玩家实力收敛后长期胜率自然趋近 50%，这正是 Jeff Hill（Valve）与 Riot 2018 博文的论证；但玩家把这一数学后果感知为"被控制"。
- 官方承认的"连胜/连败"效应集中在**评分更新侧**（variance/σ 放大使连胜涨分更快：Valorant、BG、TrueSkill 2）与**校准侧**（OW2 称长连胜=评分未校准；SC2 MMR decay），而非"匹配侧刻意塞坑队友"。
- CoD 白皮书是唯一公开了**A/B 实验**数据的案例，它直接证明了"匹配设计会显著影响留存"——这既支持 SBMM 的合理性，也恰好说明厂商**确实**以留存为目标评估匹配策略，这与"EOMM 式优化"在动机上并不矛盾。
- BO7 的"Open"列表说明即便公司内部数据支持 SBMM，社区压力也能推动厂商在默认列表中弱化技能权重。

### Gaps
- 由于无法直接打开页面，OW2 两篇博文、Riot 2018 博文、CoD 白皮书 #2 的精确发布日期与逐字表述未能核对；CoD 白皮书中具体百分比（如"90%/10%"）来自媒体转述。
- 未找到 Psyonix（Rocket League）官方算法说明（社区普遍称其类 TrueSkill，但本轮未检索到可靠来源）。
- 未找到 Valve 关于 CS2 Premier 算法的官方文档；Dota 2 "Ranked Matchmaking" 原帖日期未确认。
- 未找到 Riot 关于 LoL/Valorant 使用 TrueSkill/Elo/Glicko 具体变体的官方文件。
- 永劫无间、第五人格、和平精英未找到官方匹配机制说明。
- 未找到 Blizzard 官方确认 OW2"减少连胜"改动已上线的后续公告。

## 问题二：中文玩家语境中的"ELO机制"含义，以及腾讯等公司的官方回应

### Takeaway
中文社区的"ELO机制"已从"Elo 等级分算法"演变为一个**泛指隐藏分匹配、且常被理解为系统操控胜率**的贬义词：典型信念是"连胜后匹配猪队友/强对手、连败后给好队友，把胜率拉回 50%（或 60%）"。腾讯官方长期口径是"使用 ELO 评估实力、目标是水平相当的对局、无动机干预胜率"，并在 2024–2026 年的"孙千和诉腾讯"案中以商业秘密为由拒绝公开算法，法院一审（2026-04-07）驳回原告全部诉求；同期《王者荣耀》在 S42（2026-01-08）把匹配改为"段位为主、表现为辅"，2026-08 又新增"负面信誉"维度。

### Cited Findings
- 【第三方分析】萌娘百科：基于 Elo 或其变体、广泛用于竞技电子游戏的隐藏分机制在中文互联网常被称为"Elo机制"；多人游戏一般把双方视为两个整体，尽量使两队平均隐藏分相近。— [萌娘百科 等级分](https://mzh.moegirl.org.cn/%E7%AD%89%E7%BA%A7%E5%88%86)；[萌娘百科 ELO算法](https://zh.moegirl.org.cn/ELO%E7%AE%97%E6%B3%95)
- 【社区推测】玩家常见说法：系统参考隐藏分平衡两边"总分"，用来解释"打得好反而遇到弱队友"；有文章称隐藏分对胜率进行"宏观调控"；一篇 2021 年 B 站文章称算法操控使总胜率维持在 60% 左右（无官方证实）。也有博主反驳："所有讨论 elo 存在的博主都拿不出强相关的统计数据证明高 KDA 就一定会匹配低 KDA"。— [头条](https://www.toutiao.com/zixun/7489514358536570932/)；[B 站专栏](https://www.bilibili.com/read/cv44402038)；[B 站动态 2021](https://www.bilibili.com/opus/580988150354686332)；[少数派](https://sspai.com/post/90199)
- 【官方披露（经转述）｜2018-05】《王者荣耀》策划 Donny 发微博简介 ELO 算法，此后引发大量误解；同年官网发布《狄仁杰答疑 | 匹配算法全面解析》，提到 ELO 等级分系统用于评估技术等级、尽量保证每局公平，否认为连胜玩家匹配"坑队友"。— [虎嗅 2025-08](https://www.huxiu.com/article/4697662.html)；[IT之家](https://www.ithome.com/0/874/942.htm)
- 【第三方分析｜2018】人人都是产品经理文章《王者荣耀的匹配算法与产品设计-Elo rating system》（第三方解读）。— [woshipm](https://www.woshipm.com/pd/935349.html)
- 【诉讼/官方回应】青岛律师孙千和于 2024 年 6 月向深圳市南山区人民法院起诉，称"连胜后易连败、输输赢赢直到胜率趋近 50%"，要求公开匹配核心因素及各因素在不同模式下的占比与权重；2025-08-12 开庭；腾讯提交近 1000 页证据，主张匹配算法属核心商业秘密，并称已通过公众号、视频号等渠道公开部分内容；2026-01-22 案由由"网络服务合同纠纷"改为"数据纠纷"。— [IT之家](https://www.ithome.com/0/874/942.htm)；[扬子晚报 2025-08](https://www.yzwb.net/news/sh/202508/t20250815_250245.html)；[扬子晚报 2026-02](https://www.yzwb.net/news/zntt/202602/t20260202_317953.html)；[Sheep Esports](https://www.sheepesports.com/articles/tencent-sued-for-allegedly-hiding-a-winner-loser-queue-algorithm-in-honor-of-kings/en)
- 【官方回应（经媒体引述）】腾讯称不存在通过匹配算法刻意为连胜召唤师匹配"坑队友"的情况，匹配目标是把水平相当的玩家放入同一局、基于长期数据评估综合能力；"我们没有任何动机去干预召唤师们的对局结果与胜率"；匹配算法使用 ELO 等级分系统并考虑实力、分路意愿等因素；称其披露详细程度与抖音一致。— [IT之家](https://www.ithome.com/0/874/942.htm)；[17173 2026-04-08](https://news.17173.com/content/04082026/140318558.shtml)；[界面新闻](https://www.jiemian.com/article/13190483.html)
- 【诉讼证据（经媒体报道）】腾讯庭审中展示随机抽取的多名玩家数据：总场次约 500–2500 场、胜率超过 70%，用以反驳"控制胜率在 50%"。（另一检索摘要未找到"70%"数据，存在报道不一致。）— [17173 2026-04-08](https://news.17173.com/content/04082026/140318558.shtml)；[凤凰科技](https://tech.ifeng.com/c/8s9G5p5thMQ)
- 【判决｜2026-04-07 一审】南山区法院驳回原告全部诉讼请求：公开匹配算法具体技术细节超出消费者知情权合理范围；运营商已通过多渠道披露主要影响因素；公开细节可能被恶意利用、滋生黑灰产、破坏公平；判决同时对游戏算法监管提出建议。未检索到上诉信息。— [17173](https://news.17173.com/content/04082026/171630771.shtml)；[同花顺](https://stock.10jqka.com.cn/20260408/c675813550.shtml)；[扬子晚报 2026-04](https://www.yzwb.net/news/sh/202604/t20260408_339832.html)；[澎湃](https://m.thepaper.cn/newsDetail_forward_31398420)；[Inven Global](https://www.invenglobal.com/articles/20748/the-persistent-50-win-rate-conspiracy-what-did-the-chinese-court-decide)
- 【官方披露｜2026-01-08 S42 赛季】官方预热称匹配"以段位为主要依据"，使双方段位更接近；共创方案包括提高段位权重、在组队与加载界面显示队伍平均加权段位、新增"挑战强敌"机制；官方称 90% 以上对局双方段位差在 2 星内。媒体转述数据：段位差 5 星内对局占比 66.8%→99.6%，2 星内 36.1%→90.7%。— [IT之家 S42](https://www.ithome.com/0/910/430.htm)；[17173 2026-01](https://news.17173.com/content/01052026/171952540.shtml)
- 【第三方分析（灰度期媒体转述，非官方原文）】旧机制约 70% 看隐藏分，新机制 60% 看外显段位、40% 参考近期表现；官方称完全按段位匹配会导致新手长期卡段。— [17173 2025-11](https://news.17173.com/content/11112025/231259235.shtml)；[17173 2025-11-13](https://news.17173.com/content/11132025/104700646.shtml)
- 【官方披露｜2026-08】《王者荣耀》"对局环境优化专栏"首期：排位匹配新增"负面信誉"判断维度，使信誉正常玩家不再连续与负面信誉玩家同队；官方邀请职业教练复盘大量连败对局。— [17173 2026-08-13](https://news.17173.com/content/08132026/020132459.shtml)；[17173 2026-08-12](https://news.17173.com/content/08122026/080506636.shtml)
- 【检索结果为空】未找到腾讯官方承认"为连败/新手安排 AI 队友"的说法；可确认的官方 AI 功能为人机模式、"绝悟"AI 与挂机 AI 托管。— [虎嗅 2025-08-28](https://m.huxiu.com/article/4746172.html)；[爱范儿](https://www.ifanr.com/1152250)

### Inferences
- "ELO机制"一词的流行与 2018 年官方主动用"ELO"解释匹配有关：官方用词把一个评分算法与"匹配黑箱"绑在一起，之后所有不满都被归因于"ELO"。
- S42 改为"段位为主"可视为腾讯在诉讼与舆论压力下对"隐藏分不透明"的产品层回应：可见段位权重上升，减少"段位相同但对手明显更强/队友更弱"的体感，但也牺牲了一部分基于实力的平衡。
- 腾讯在法庭上展示长期胜率 >70% 的玩家样本，是反驳"强制 50%"的直接证据，但只是挑选样本，不能证明不存在任何短期调节；同样，原告的"趋近 50%"也未被法院认定为事实。

### Gaps
- 未能获取《狄仁杰答疑 | 匹配算法全面解析》（2018）原文与 Donny 微博原文。
- 未获取判决书原文；"70% 胜率样本"仅见于部分报道。
- 未找到和平精英、第五人格、永劫无间、蛋仔派对等腾讯/网易其他产品的官方匹配说明。
- 未检索到腾讯 2021 年另一起"成瘾"诉讼（Asia Times 报道）的匹配相关细节。

## 问题三：与匹配相关的公司专利（编号、权利人、年份、通俗含义、是否有部署证据）

### Takeaway
"以留存/付费为目标的匹配"在专利层面**真实存在**：Activision US 9,789,406（2017，按"诱导购买"匹配）与 EA 的 US 10,286,327/10,751,629/11,344,814/10,610,786（基于流失率预测的匹配）、EA 动态难度 US 9,919,217 等。但**没有任何公开证据表明这些专利已在线上游戏部署**：Activision 称 9,789,406 是独立研发团队的探索性专利、未在游戏中实施（Bungie 称 Destiny 无此功能）；EA 在 Zajonc 集体诉讼中向原告开放技术资料与工程师后，原告于 2021-02 自愿撤诉，EA 表态 DDA "never was in FIFA, Madden or NHL, and never will be"，并承诺不用 DDA 影响任何在线多人游戏。

### Cited Findings
**Activision**
- 【专利】US 9,789,406 "System and method for driving microtransactions in multiplayer video games"，2015 年申请、2017-10-17 授权，权利人 Activision Publishing。通俗含义：匹配引擎（考虑技能、延迟、好友等）可把"高手/明星玩家"与新手配在一起，诱导新手购买高手所用道具；也可把刚购买道具的玩家放进能让该道具"发挥作用"的对局以强化购买满足感。专利未指明任何具体游戏。— [Game Informer](https://gameinformer.com/b/news/archive/2017/10/17/activision-patent-encourages-microtransaction-spending-through-matchmaking)；[AV Club](https://www.avclub.com/activision-patent-for-microtransactions)；[Windows Central](https://www.windowscentral.com/activision-patent-reveals-plans-trick-gamers-buying-microtransactions-through-matchmaking)
- 【官方回应｜2017-10】Activision 发言人（向 Rolling Stone 旗下 Glixel，事后补充）："exploratory patent filed in 2015 by an R&D team working independently from our game studios. It has not been implemented in-game"；Bungie 社区经理 David "Deej" Dague："None of this functionality appears in Destiny"，并确认 Destiny 2 也没有。— [GameSpot](https://www.gamespot.com/articles/activision-clarifies-its-patent-for-encouraging-mi/1100-6454147)；[MP1st](https://mp1st.com/news/call-of-duty-matchmaking-used-by-activision-to-encourage-players-to-buy-microtransactions)
- 【第三方分析】Charlie Intel 补充：该类专利对候选对局按延迟、技能、队伍构成、好友在场、等待时间、地理位置打分，设计者可调各因素权重。— [Charlie Intel](https://www.charlieintel.com/activision/additional-details-activisions-new-matchmaking-patent-44189/)
- 【专利】US 10,322,351 "Matchmaking system and method for multiplayer video games"，Activision Publishing，优先权日 2014-07（2019 年授权）。通俗含义：认为僵硬的纯技能匹配会延迟组队，提出多因素打分优化匹配。未见部署证据（但其思路与 CoD 白皮书公开的"多因素、延迟优先"一致）。— [Patent Arcade](https://www.patentarcade.com/video-game-patent/US10322351/matchmaking-system-and-method-for-multiplayer-video-games)
- 【专利】US 10,376,792 "Group composition matchmaking system and method for multiplayer video games"（Activision，USPTO 全文链接；本轮未读取权利要求）。— [USPTO PDF](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10376792)

**Electronic Arts**
- 【专利】US 10,286,327 "Multiplayer video game matchmaking system and methods"（EA）。通俗含义：用图模型+机器学习，为排队玩家的不同对局组合**预测流失率（或留存率）**，选择使整体留存最高的匹配方案——与 EOMM 论文同一思路。同族续案 US 10,751,629（2020 授权，另一来源列 2019，日期有冲突）、US 11,344,814（2022-05-31 授权）。— [Patent Arcade 10,286,327](https://www.patentarcade.com/video-game-patent/US10286327/multiplayer-video-game-matchmaking-system-and-methods)；[Patent Arcade 10,751,629](https://www.patentarcade.com/video-game-patent/US10751629/multiplayer-video-game-matchmaking-system-and-methods)；[Patent Arcade 11,344,814](https://www.patentarcade.com/video-game-patent/US11344814/multiplayer-video-game-matchmaking-system-and-methods)
- 【专利】US 10,610,786 "Multiplayer video game matchmaking optimization"（EA，2020-04-07 授权）。通俗含义：从队列组队时用模型预测玩家会继续玩多久，若预测留存未达阈值，就把队伍中的玩家替换成队列中其他人。— [Patent Arcade](https://www.patentarcade.com/?p=5555)
- 【第三方分析】mein-mmo 等媒体据此称 EA"在研究更少依赖公平、让玩家花更多钱的匹配"——这是记者对专利的解读，EA 未确认产品使用。— [mein-mmo](https://mein-mmo.de/en/ea-patent-unfaires-matchmaking,199940/)；[TechRaptor](https://techraptor.net/content/ea-filed-patent-online-matchmaking-algorithm-focusing-player-engagement)
- 【专利】US 9,919,217 "Dynamic difficulty adjustment"（EA，2018-03-20 授权，发明人含 Navid Aghdaie）；同族 US 10,286,323（2019）、US 10,807,004（2020）。通俗含义：用历史行为数据训练"留存/游玩时长预测模型"，按预测动态调整难度，使玩家既不太难也不太易、持续进步。— [Google Patents US10286323](https://patents.google.com/patent/US10286323)；[Google Patents US10807004](https://patents.google.com/patent/US10807004)；[Patent Arcade](https://www.patentarcade.com/video-game-patent/US10286323/dynamic-difficulty-adjustment)；[Goodmans IP Blog](https://www.goodmans.ca/insights/post/goodmans-ip-blog/are-you-ready-for-a-challenge-electronic-arts-resubmits-patent-for-dynamic-difficulty-adjustment)
- 【诉讼与官方回应】Zajonc v. Electronic Arts（美国北加州联邦地区法院，2020-11 提起）指控 EA 在 FIFA、Madden、NHL 的 Ultimate Team 中秘密使用 DDA 以推动抽卡消费；EA 初始回应"baseless and misrepresent our games"；2021-02-11 原告在获得技术文档及工程师访谈后自愿撤诉；EA 声明 DDA "never was in FIFA, Madden or NHL, and never will be"，并承诺不用 DDA 影响任何游戏的在线多人。— [VGC](https://www.videogameschronicle.com/news/ea-loot-box-lawsuit-dropped-after-company-convinces-lawyers-it-doesnt-adjust-difficulty)；[GamingBolt](https://gamingbolt.com/ea-lawsuit-involving-dynamic-difficulty-adjustment-has-been-dismissed)；[PocketGamer.biz](https://www.pocketgamer.biz/news/75951/dynamic-difficulty-class-action-lawsuit-against-ea-gets-dropped/)；[PC Gamer](https://www.pcgamer.com/uk/class-action-lawsuit-claims-eas-dynamic-difficulty-tech-encourages-loot-box-spending/)
- 【第三方分析】Dexerto 报道称 EA 在诉讼中披露代码，"scripting"说法被驳斥。— [Dexerto](https://www.dexerto.com/fifa/ea-sports-debunk-fifa-scripting-claims-1526503)

**Microsoft**
- 【专利】US 8,538,910 B2 "Determining relative skills of players"，发明人 Thomas Minka、Thore Graepel、Ralf Herbrich，原权利人 Microsoft Corp（现 Microsoft Technology Licensing LLC），申请公开号 US 2009/0227313 A1。维基百科称 TrueSkill 已获专利、名称为商标，仅限微软项目及获许可的商业项目使用（其专利引用指向此申请）。部署：TrueSkill/TrueSkill 2 在 Xbox Live、Halo、Gears 等公开使用。— [Google Patents US8538910B2](https://patents.google.com/patent/US8538910B2/en)；[Wikipedia TrueSkill](https://en.wikipedia.org/wiki/TrueSkill)

**Riot Games**
- 【专利】US 11,484,801（2021-03-23 申请，2022-11-01 授权，Riot Games）：按玩家通常的游戏时段相似度排序候选账号、进行组队匹配。另有申请 "Activity-factored team formation in multiplayer online gaming"（2022-09-29 公开，非授权）。US 11,065,547（Riot）：部分基于玩家档案中的**行为数据**进行匹配。未见部署说明。— [Justia（发明人 Lawrence Lihuan Xie）](https://patents.justia.com/inventor/lawrence-lihuan-xie)；[Justia 11,065,547](https://patents.justia.com/patent/11065547)；[eXputer](https://exputer.com/news/industry/riot-games-patent-better-team-formation/)

**Tencent / 中国专利（权利人均未在检索中确认）**
- 【专利（权利人未确认）】美国专利 US 12,533,594 "Method and apparatus for game matching, storage medium, and electronic device"，优先权为 2022-05-25 中国申请 202210583584.4；背景为 MOBA 中先组队、再以队伍为单位匹配。搜索结果未显示权利要求与权利人。— [USPTO PDF](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12533594)
- 【专利（权利人未确认）】CN112221161B "对局参与方的匹配方法、装置、设备及可读存储介质"（申请号 CN202011228107.3，Google Patents 标注 Active，分类 A63F）。命名格式与腾讯常见专利一致，但本轮未能确认权利人及是否涉及胜率。— [Google Patents CN112221161B](https://patents.google.com/patent/CN112221161B/zh)
- 【检索结果为空】未找到以"胜率/连败"为权利要求核心的腾讯或网易专利；CN107920122A（游戏玩家匹配方法，针对网络延迟）权利人为杭州电子魂网络科技，与腾讯无关。— [Patsnap CN107920122A](https://eureka-patsnap-com.sutd.idm.oclc.org/patent-CN107920122A)

**Valve / Blizzard / Epic / NetEase**
- 【检索结果为空】未找到上述公司名下的匹配类授权专利（Valve 仅作为网络专利诉讼共同被告出现）。— [Bloomberg Law](https://news.bloomberglaw.com/ip-law/riot-gamess-networking-patent-win-affirmed-by-federal-circuit)

### Inferences
- 专利证明的是"公司研究过并寻求保护某种思路"，不等于产品上线；在 Activision 与 EA 两个最受关注的案例中，公司均公开否认部署，且 EA 的否认经过了诉讼程序中的技术披露检验（原告撤诉），证据强度高于单纯 PR 声明。
- EA 的留存导向匹配专利（10,286,327 族、10,610,786）与 EA 的 EOMM 论文作者/思路重合，说明"以流失率为目标函数的匹配"在 EA 内部是真实研究方向；EA 的公开承诺只覆盖"DDA 不用于在线多人"，并未明确覆盖"EOMM 式匹配"——这是一个值得在报告中指出的表述空白。

### Gaps
- 未能通读任何专利的权利要求原文；授权日期部分存在来源冲突（US 10,751,629、US 10,286,323）。
- 未能在 CNIPA/Google Patents 上按权利人检索腾讯、网易的"匹配+胜率/连败"专利（网络限制）；US 12,533,594 与 CN112221161B 的权利人待核实。
- 搜索中出现 US 11,478,715 "User-controllable model-driven matchmaking"（USPTO 链接），权利人未确认：[USPTO PDF](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11478715)。

## 问题四：公司署名的匹配/胜率预测研究论文

### Takeaway
公司论文清楚表明：至少 EA（EOMM, 2017）与网易伏羲（OptMatch KDD 2020、EnMatch AAAI 2024）**公开发表了以"玩家参与度/满意度/流失"而非纯公平为目标的匹配算法，并报告了真实游戏数据或线上部署实验**；Microsoft 的 TrueSkill/TrueSkill 2 与 Ubisoft 的 Ghost Recon Online 论文代表"更准确的实力估计/对局平衡预测"路线；腾讯论文（WWW 2019、CUPID 2024）侧重阵容/位置对胜率的影响与"重匹配"以提升公平和位置满意度。Activision 的公开研究主要是 2024 年白皮书与 GDC 演讲。

### Cited Findings
- 【公司论文｜EA，WWW 2017】Chen, Xue, Kolen, Aghdaie, Zaman, Sun, Seif El-Nasr, "EOMM: An Engagement Optimized Matchmaking Framework"，WWW 2017（珀斯）pp.1143–1150，DOI 10.1145/3038912.3052559；arXiv 1702.06820。核心：以每次匹配后的**流失风险（churn risk）**度量不参与度，把等待玩家建成完全图、边权为配对后的合并流失风险，用最小权完美匹配求解；证明"同水平匹配"只是 EOMM 在很强简化假设下的特例；用 EA 一款热门游戏真实数据做**模拟**，报告参与度优于现有方法。社区评论指出实验仅针对 1v1。— [arXiv 1702.06820](https://arxiv.org/pdf/1702.06820)；[ADS 摘要](https://ui.adsabs.harvard.edu/abs/2017arXiv170206820C/abstract)；[Webis 收录](https://ir.webis.de/anthology/2017.wwwconf_conference-2017.118/)；[VLR.gg 讨论（社区）](https://www.vlr.gg/post/4169544)
- 【公司论文｜Ubisoft，2012】Delalleau, Contal, Thibodeau-Laufer, Ferrari, Bengio, Zhang, "Beyond Skill Rating: Advanced Matchmaking in Ghost Recon Online", IEEE Trans. on Computational Intelligence and AI in Games 4(3):167–177, 2012（检索仅确认书目信息，未见摘要；常被引为用机器学习预测对局平衡/玩家体验、超越单一技能分的匹配）。另：Ghost Recon Phantoms 官方称匹配同时考虑装备与技能；Wildlands 更新称其 MMR 基于 Glicko-2。— [EOMM 论文参考文献中的引用](https://arxiv.org/pdf/1702.06820)；[CAIAC 摘要（未确认为同一论文）](https://www.caiac.ca/en/node/92)；[GhostRecon.net](https://www.ghostrecon.net/?p=185)；[games.ch Wildlands 8.2](https://games.ch/ghost-recon-wildland/news/update-8-2-ghost-recon-wildlands-ggiid/)
- 【公司论文｜Microsoft Research，NIPS 2006】Herbrich, Minka, Graepel, "TrueSkill(TM): A Bayesian Skill Rating System"（MSR-TR-2006-80），称其为 Elo 的推广（支持多人/团队、以均值+不确定度建模）。— [MSR 出版页](https://www.microsoft.com/en-us/research/publication/trueskilltm-a-bayesian-skill-rating-system/)；[NIPS PDF](https://papers.nips.cc/paper_files/paper/2006/file/f44ee263952e65b3610b8ba51229d1f9-Paper.pdf)
- 【公司论文｜Microsoft Research，2018-03】"TrueSkill 2: An improved Bayesian skill rating system"（MSR-TR-2018-8）：在胜负之外引入玩家经验、是否组队、击杀数、退出倾向、其他模式技能；用 Halo 5 数据，历史对局预测准确率 68% vs 原 TrueSkill 52%。— [MSR 出版页](https://www.microsoft.com/en-us/research/publication/trueskill-2-improved-bayesian-skill-rating-system/)
- 【公司论文｜网易（伏羲/雷火关联，经二手来源），KDD 2020】Gong, Feng, Ye, Li, Wu, Tao, Fan, Cui, "OptMatch: Optimized Matchmaking via Modeling the High-Order Interactions on the Arena"，KDD 2020 pp.2300–2310：离线阶段学习玩家高阶交互表示并用神经网络预测含"组队效应"的对局结果，在线阶段规划匹配以最大化玩家总效用（满意度）；四个真实数据集+《Fever Basketball（潮人篮球）》线上实验。网易归属来自 GDC 讲者页面与 Steam 社区帖，非论文本身确认。— [PapersWithCode](https://astro.paperswithcode.com/paper/optmatch-optimized-matchmaking-via-modeling)；[DBLP](https://dblp.org/pid/223/3141)；[GDC Vault "Find the Right Match AI"](https://gdcvault.com/play/1027278/Find-the-Right-Match-AI)
- 【公司论文｜网易伏羲 AI Lab，AAAI 2024】"EnMatch: Matchmaking for Better Player Engagement via Neural Combinatorial Optimization"，AAAI-38(8):9098–9106，作者全部署名网易伏羲（杭州）：明确批评"按段位分层、只在同层匹配"的公平匹配"not always good for player engagement"；建立参与度模型并以强化学习求解 NP-hard 组合优化；"online deployments on two games"（未披露游戏名）。— [AAAI OJS](https://ojs.aaai.org/index.php/AAAI/article/view/28760)；[MLAnthology](https://mlanthology.org/aaai/2024/wang2024aaai-enmatch)
- 【第三方分析】独立分析者 Ramin Shokrizade 批评 EnMatch 沿用 2017 EOMM 的"流失"定义（实为"疲劳"），并称其以 18 局内疲劳降低 0.3% 得出结论"bizarre"。— [Substack](https://raminshokrizade.substack.com/p/129-analysing-neteases-enmatch-research)
- 【第三方分析】Marvel Rivals 玩家社区将网易 2020 年 OptMatch 作为怀疑 EOMM 的依据之一；网易已官方否认 Rivals 使用 EOMM（见问题一）。— [Gfinity](https://www.gfinityesports.com/article/netease-reveals-the-secret-to-fixing-your-marvel-rivals-losing-streak)；[Steam 社区](https://steamcommunity.com/app/2767030/discussions/0/612032374411151276)
- 【公司论文｜腾讯合作，WWW 2019】"What Makes a Good Team? A Large-scale Study on the Effect of Team Composition in Honor of Kings"（arXiv 1902.06432）：使用《王者荣耀》9600 万场、1 亿玩家数据，研究角色构成对团队胜负的影响，阵容特征具有胜负预测力；含腾讯员工合著。— [arXiv 1902.06432](https://arxiv.org/abs/1902.06432)
- 【公司论文｜腾讯作者参与，2024】Ge Fan（腾讯）等，"CUPID: Improving Battle Fairness and Position Satisfaction in Online MOBA Games with a Re-matchmaking System"（arXiv 2406.19720，2024-06；ACM PACM HCI，DOI 10.1145/3686978）：在初次匹配后增加"重匹配"阶段重新分配队伍与位置，含预过滤与赛前胜率预测模型以评估公平；胜率预测准确率平均相对提升 7.18%；"已部署于一款热门在线 MOBA"，A/B 测试显示公平性与满意度提升（未点名游戏）。— [arXiv 2406.19720](https://arxiv.org/abs/2406.19720v1)；[Crossref](https://api.crossref.org/works/10.1145%2F3686978)
- 【公司论文（部分腾讯作者）】MOBA 实时胜负预测论文（arXiv 2012.09424 含腾讯作者；2008.06313 两阶段时空网络）。— [arXiv 2012.09424](https://arxiv.org/pdf/2012.09424v4)；[arXiv 2008.06313](https://arxiv.org/abs/2008.06313v3)
- 【公司演讲｜Activision，GDC 2016】Josh Menke（时任 Activision 高级系统设计师）"Skill, Matchmaking, and Ranking Systems Design"，涵盖技能判定、匹配、排名的关系，经验来自 WoW、星际争霸 2、CoD。另有 GDC "Significantly Improving Your Skill System"（GDC Vault 1025241，讲者未确认）。— [GDC Vault 1023014](https://gdcvault.com/play/1023014/Skill-Matchmaking-and-Ranking-Systems)；[Game Developer](https://gamedeveloper.com/design/video-skill-matchmaking-and-ranking-systems-design)；[80.lv](https://80.lv/articles/gdc-skill-matchmaking-and-ranking-systems-design)；[GDC Vault 1025241](https://gdcvault.com/play/1025241/Significantly-Improving-Your-Skill-System)
- 【公司白皮书｜Activision Research，2024】见问题一（Ping、Skill、Ranked Play 三篇）。— [Activision Research](https://research.activision.com/publications/2024/07/Call-of-Duty-Matchmaking-Intel-02)
- 【第三方学术】INFORMS《Management Science》论文 "Matchmaking Strategies for Maximizing Player Engagement in Video Games"（作者未在检索中显示）；arXiv 2512.22038 "Mean-Field Analysis and Optimal Control of a Dynamic Rating and Matchmaking System"——均非游戏公司论文，可作理论参照。— [Management Science](https://pubsonline.informs.org/doi/fpi/10.1287/mnsc.2023.02957)；[arXiv 2512.22038](https://arxiv.org/pdf/2512.22038)

### Inferences
- "参与度优化匹配"（EOMM 路线）在学术层面已由两家大厂（EA、网易）公开署名并报告实验/部署，这是"玩家怀疑 EOMM"最硬的事实基础；但这些论文均未声明在具体某款热门竞技游戏的排位模式中长期使用，且公司对具体产品（Marvel Rivals、FIFA）给出了否认。
- 学术上的"参与度匹配"与"操纵胜率"并不等价：EOMM 的目标函数是流失风险，在其模拟中最优解可能包含"连败后给一把易赢局"之类的策略——这与玩家描述的"ELO机制"在现象上相似，因此社区把二者混同并不完全是无中生有，但缺少具体产品层证据。

### Gaps
- 未能读取 EOMM、OptMatch、EnMatch、CUPID 全文，具体提升幅度（如 EOMM 的参与度提升百分比、EnMatch 部署游戏名称）未核实。
- Ubisoft 论文仅确认书目信息，摘要内容未能直接读取。
- 未找到 Riot、Valve、Blizzard、Epic 署名的匹配学术论文；未找到 Activision 在白皮书之外的同行评审匹配论文。
- OptMatch 的网易归属依赖二手来源。

## 问题五：总体判断——哪些"参与度优化/操纵匹配"说法有证据，哪些被否认或缺乏支持

### Takeaway
证据分层：（1）**有直接证据**：公司确实研究并申请了以留存/付费为目标的匹配与动态难度专利（Activision、EA），并发表了参与度优化匹配论文与线上实验（EA EOMM、网易 OptMatch/EnMatch、腾讯 CUPID 的满意度目标）；Activision 公开了以留存为评价指标的 SBMM A/B 实验；休闲模式中按实力调节机器人数量（Fortnite、PUBG）是官方承认的。（2）**被明确否认**：在具体产品中"强制 50% 胜率/输家队列/连胜塞坑队友/按消费匹配"（Riot、Valve、Blizzard、Activision、Tencent、NetEase Rivals 均否认；EA 否认 DDA 并经诉讼技术披露检验）。（3）**无可靠证据**：任何主流竞技游戏排位模式被证实在使用 EOMM 或胜率操控；社区"周期性胜率""60%/50% 调控"说法多为个人样本。

### Cited Findings
- 【专利+官方否认】Activision 9,789,406 存在且内容属实，但官方称未实施；Bungie 称 Destiny/Destiny 2 无此功能。— [GameSpot](https://www.gamespot.com/articles/activision-clarifies-its-patent-for-encouraging-mi/1100-6454147)；[MP1st](https://mp1st.com/news/call-of-duty-matchmaking-used-by-activision-to-encourage-players-to-buy-microtransactions)
- 【专利+诉讼检验】EA DDA 专利存在；诉讼中经技术披露后原告撤诉，EA 承诺不在在线多人中使用 DDA。— [VGC](https://www.videogameschronicle.com/news/ea-loot-box-lawsuit-dropped-after-company-convinces-lawyers-it-doesnt-adjust-difficulty)；[GamingBolt](https://gamingbolt.com/ea-lawsuit-involving-dynamic-difficulty-adjustment-has-been-dismissed)
- 【公司论文】EOMM（EA）与 EnMatch（网易）明确主张公平匹配不等于参与度最优，且报告真实数据模拟/线上部署。— [arXiv EOMM](https://arxiv.org/pdf/1702.06820)；[AAAI EnMatch](https://ojs.aaai.org/index.php/AAAI/article/view/28760)
- 【官方实验】Activision 白皮书 #2：降低 SBMM 后 90% 技能组回流下降、仅顶部 10% 回流增加（媒体转述）。— [Game Developer](https://www.gamedeveloper.com/design/deprioritizing-skill-based-matchmaking-turned-call-of-duty-into-the-bad-place)
- 【官方否认汇总】Riot（LoL 2018、2025；Valorant 2022）、Valve（Jeff Hill）、Blizzard（OW2 2023 part 2）、Activision（消费不影响匹配，2024）、Tencent（2018、2025–2026 诉讼）、NetEase（Marvel Rivals 2025-08）。— [Riot Nexus](https://nexus.leagueoflegends.com/en-us/2018/02/dev-matchmaking-real-talk/)；[GGScore](https://ggscore.com/en/lol/news/70213)；[ONE Esports](https://www.oneesports.gg/valorant/losers-queue-valorant-ranked-shroud/)；[Steam 社区](https://steamcommunity.com/app/570/discussions/0/2789369598124752294)；[OW2 part 2](https://overwatch.blizzard.com/en-us/news/23910161)；[Windows Central](https://www.windowscentral.com/gaming/ping-is-king-call-of-duty-modern-warfare-3-multiplayer-matchmaking-is-demystified-in-the-latest-intel-drop)；[IT之家](https://www.ithome.com/0/874/942.htm)；[Insider Gaming](https://insider-gaming.com/marvel-rivals-does-not-use-eomm-says-netease-games/)
- 【法院认定】中国法院一审未认定"胜率被控制在 50%"，而是以商业秘密/知情权边界驳回公开算法诉求——即法院**没有**就"是否操控"作出事实认定。— [17173](https://news.17173.com/content/04082026/171630771.shtml)；[Inven Global](https://www.invenglobal.com/articles/20748/the-persistent-50-win-rate-conspiracy-what-did-the-chinese-court-decide)
- 【官方承认的"非纯实力"因素】Fortnite/PUBG 休闲模式机器人数量随实力递减；OW2 新手初始 MMR 下调到 Bronze 5 以提高新手胜率；BG 6500 以下每局保底加分；SC2 MMR decay；CoD ping 优先；王者荣耀 2026-08 加入"负面信誉"维度。— [VGC Fortnite](https://videogameschronicle.com/news/fortnite-is-adding-skill-based-matchmaking)；[Destructoid PUBG](https://www.destructoid.com/pubg-is-testing-ranked-mode-on-pc-and-bots-arent-invited/)；[OW2 part 1](https://overwatch.blizzard.com/en-us/news/23896785)；[Hearthstone BG](https://hearthstone.blizzard.com/en-us/news/23239989)；[SC2 Situation Report](https://starcraft2.com/news/12055065)；[callofduty.com](https://www.callofduty.com/blog/2024/01/call-of-duty-update-an-Inside-look-at-matchmaking)；[17173 2026-08](https://news.17173.com/content/08132026/020132459.shtml)

### Inferences
- 可以在报告中明确的"证据强度表"：专利存在（强）＞公司论文/实验存在（强）＞具体产品部署（无公开证据，且多家公司明确否认；EA 案经诉讼程序检验）＞社区"强制 50%"体感（弱，样本小、选择性记忆、与 Elo 收敛的数学性质混淆）。
- 值得强调的细节：官方确实在做"影响胜率/体验"的设计，但多集中在**新手保护、回流校准、休闲模式机器人、行为/信誉过滤**等透明度较低的边缘环节；这些环节恰是玩家体感"被安排"的来源之一，也是官方否认"操控胜率"时往往不展开说明的部分。
- 对 DeepBattler 类项目（酒馆战棋）而言：Blizzard 官方明确 BG 使用自研 8 人评分（非 Elo/Glicko），有方差项与 6500 以下保底加分，匹配只用内部评分——这意味着 BG 中"长期分数"会因保底加分而缓慢上漂，但官方未提及任何基于胜负历史的匹配干预。

### Gaps
- 没有任何公司公开过排位模式匹配质量的长期独立审计数据；所有"未部署"结论都依赖公司自述（EA 案稍强）。
- 未找到第三方对 LoL/OW2/王者荣耀大样本数据检验"连胜后队友质量下降"的严谨研究（应由本研究其他部分补充）。
