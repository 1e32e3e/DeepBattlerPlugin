# 整合记录（2026-10-19）

五位作者并行起草各章后，整合阶段做的跨章决定。

## 参考文献

- 五个章节 bib 合并为 `paper/refs/refs.bib`（194 条；`riot2021valorant202`、`riot2024tldw` 未被引用，保留）。各章 bib 改写为 refs.bib 的子集（含本章原有条目和本章引用的条目），供 `single_*.tex` 试编译；条目内容与 refs.bib 逐字一致，以 refs.bib 为准。
- 同一作品不同键名，统一为按 STYLE.md 规则的键名，并改了所有 `\cite`：

| 统一后 | 被替换 |
|---|---|
| `blizzard2019developer` | `blizzard2019bgrating`、`blizzard2019personal` |
| `blizzard2020developer` | `blizzard2020bgrating`、`blizzard2020rating` |
| `blizzard2022overwatch` | `blizzard2022ow2part1` |
| `blizzard2023overwatch` | `blizzard2023ow2part2` |
| `cortez2024convergence` | `cortez2026convergence` |
| `yang2017realtime` | `yang2016real` |
| `koh2022valorant` | `oneesports2022valorant` |
| `microsoft2005trueskill` | `microsoft2026trueskill` |

- 同键不同著录的取舍：`elo1978rating` 按第二章实际读到的 1986 年第 2 版著录（origdate 1978）；`herbrich2006trueskill` 取 NIPS 19、MIT Press 2007、569–576 页；`deng2024streaks` 作者名按 Crossref（Dion Deng、Mingrui Li）；`oleskertaylor2024analysis` 补 DOI 与页码；`cortez2024convergence` 取首次公开年 2024（正文依据 2026 年 v2），图 `1a_timeline` 相应把 Cortez 移到 2024 年并重新出图；`yang2017realtime` 按 arXiv 1701 取 2017。

## 宏与导言区

- ch1b 的 `\en`、`\patno` 移入 `preamble.tex`（`\newcommand`），章节文件里不再定义宏。
- 修正 cleveref 的章引用：原格式用 `\chinese{chapter}`，会打印“当前章”而不是被引用的章（第一章里 `\cref{ch:winrate}` 显示“第一章”）；改为 `第#1章`（ctexrep 的章标签本身就是中文数字）。
- 多目标 `\cref` 的连接词改为中文（原为英文 and）；节号两侧统一加空格（“第 2.5.1 节”）。
- 加 `\emergencystretch`，消除中西文混排时个别找不到断行点的溢出行。

## 重复内容：一处为准，其余指过去

- **“五五开”**：厂商原话与三种读法以 ch1b `sec:ch1b-fifty` 为准，数学以 ch2 `sec:ch2-fair` 为准。ch1b 原来的推导框（取 σ_e=50）删去，改为一段引用 ch2 的数字（K=16 时 90% 的“五五开”对局真实胜率在 38%–62%）；ch2 加了指向 ch1b 原话表的句子。
- **酒馆战棋**：暴雪披露以 ch1b `sec:ch1b-blizzard` 为准（补入经原文核对的“外显评分单局最多加 300 分”）；对 AI 的含义以 ch4 `sec:ch4-bg` 为准。ch1b 的“对 AI 的两点含义”压缩为一句并指向 ch4；ch2 `sec:ch2-rank`、`sec:ch2-ffa`，ch3 `sec:ch3-bg`，ch4 的“暴雪公开了什么”均压缩为要点加引用。
- **EOMM**：论文内容以 ch1a `sec:1a-mm-engage` 为准，专利以 ch1b `sec:ch1b-patents` 为准。ch4 `sec:ch4-retention` 压缩为训练视角需要的部分并引用前两者；ch3 原先“仅依据摘要”的脚注删去（ch1a 已读全文），改为引用 ch1a。

## 跨章数字与说法

- ch1a 的 EOMM 段落开头在起草中丢失（段落从半句话开始），按 arXiv 1702.06820 第 3 节补回，含边权式 `eq:1a-eomm`（10 局状态特征、作者单位均已核对）。
- ch1a 的 Yang 等数字改为原文表 2 的口径（只用英雄 60.07%，全部特征 71.49%），与 ch4 表 4.2 一致；摘要中的 58.69% 是另一组特征的结果。
- 评分误差衰减时间：ch4 的 `4/(Kc)`（K=32 约 22 局）注明是理想值，并引用 ch2 的实际值（K=16 约 55–65 局，K=32 约 30–34 局）。
- 分辨 50 Elo 所需局数：ch4 统一写约 196 局（精确的 F(50)−1/2），5 Elo 约 19,300 局。
- ch4 留存一节的“输后比赢后高约 1.1 个百分点”改为引用同章模拟的 50.6% 对 49.4%。
- ch4 的“上头”明确为 ch3 式 `eq:ch3-tilt` 取 m=1、θ=δ 的特例，两章的检出局数因此不可直接比较。
- 腾讯“没有任何动机去干预……胜率”：2026-10-19 核对，《每日经济新闻》报道（虎嗅转载，`zhang2025hok`）确含这些摘录；光环助手页面（`ghzs2022wangzhe`）不含，只作【社区】引用。官网原文仍未找到，保留待核对脚注。
- ch3 中“第一轮人群模拟”“经核查”等过程性说法改为直接引用表格或写明模拟设定；`【本项目】` 字面量改为 `\tagOwn`，`\parencite` 改为 `\cite`（与其他章一致的上标编号）。
- 含糊的“见本章厂商部分”“见第二章”等改为指向具体节、式、表的 `\cref`。

## 版式

- ch2 浮动体由 `[t]` 改为 `[htbp]`（与其他章一致）；ch3 四张被缩到原尺寸 55%–77% 的图放大到接近原尺寸（刻度字号约 8pt）。
- 附录在目录中只列到节。

## 新写与合并

- 新写：摘要、引言（研究问题、章节对应、问题速答表、记号表、证据标签、方法与局限）、第一章章首直接回答与本章小结（三层对照表）、结论与展望；标题页小改。
- `docs/to_verify_ch*.md` 并入 `docs/TO_VERIFY.md`（42 行待核对、14 行已核对），原文件删除。

## 未解决

- 记号：AR(1) 系数第二章记 φ、第三章记 ρ（第三章 φ 是疲劳斜率）；图中标签已含这些记号，未改名，只在引言记号表后说明。
- ch2 章末的图 2.12 与表 2.6 各占一个浮动页。
- 待核对来源见 `docs/TO_VERIFY.md`。

## 第二轮修订（2026-10-19，按数学、来源、读者三组审稿意见）

### 模拟与代码
- `code/ch2/model.py`：5v5 按分匹配原先对“带噪排队键”的顺序做蛇形分队（等于随机分队）；改为房间内按评分排序后再蛇形。重跑 `t_s100_sum_k16`、`t_s200_sum_k16`、`t_s100_mean_k16`：十分位胜率变为 48.7–51.3%（加和，σ_q=100）、48.1–52.0%（加和，σ_q=200）、48.9–51.1%（均值），λ 一直拉伸（1.22→2.04）。`absorbed_share` 改用赛前评分（多一个 φ 因子）。
- `code/ch3/population.py`：新增团队加和模型、`balanced`/`assort` 分队（126 种分法）、AR 状态、连胜加分、爬分实验，以及近期战绩与自身评分统计量 `form_stats`；新增场景 `t5_snake`、`t5_sum`、`t5_balanced`、`t5_assort`（M4 输家队列）及其上头版本、`ar09_elo32`、`streakbonus_elo32`、`climb_*`。原有场景重跑后数字逐位不变。
- `code/ch3/experiments.py`：新增 `run_power_elonull`（K=20 备择换成诚实 Elo 零分布）和 `run_detect`（单人可察觉性）；`fig_power.py` 改为 2×2 四面板；`ch3_numbers.py` 打印全部新数字。
- `code/ch4/check_residual_calibration.py`：封闭人群中冻结模型残差检验的误报率（未校准 8.5%，校准 γ̂=0.62 后 4.5%）。
- 出图：第二章图例与标注字号统一 ≥7.5 pt，`ci`、`fair_game`、`stretch`、`rating_error` 去掉重叠；第三章 `FONT_SCALE` 改为 1.0 并全部按 `\linewidth` 排版，`manip` 加深阈值线并区分被遮住的诚实 Elo 曲线，`fatigue_session` 的 φ 改 ψ；`1a_timeline` 字号 7 pt、换刻度说明移到横轴下；`fig_k_tradeoff` 图例移到右下；`fig_selfplay_inflation` 打印期望值与抽样标准差。

### 正文的主要改动
- 第三章：“单人要 5 万局以上才能察觉”限定为滞后 1 自相关与连胜条件胜率；新增表 `tab:ch3-detect`（近期战绩约 1,500–3,300 局、自身评分约 500–700 局可检出，14–6 之后约 −4~−5 个百分点）；检验力改为两种零分布（i.i.d. 与诚实 Elo），“Elo 下慢状态检不出”改写为零分布选择的结果；M3 改名“分队控五成”并配蛇形分队对照，新增 M4 输家队列（不加上头时不增加长连败，叠加上头后 P(≥10) 46%→56%）；新增 `sec:ch3-hell`（150 分差距追回一半：1v1 25 局，5v5 58–110 局）；标明均值/加和团队模型（5v5 回归 0.5 对 0.9 个百分点）；AR 与连胜加分的数字改由 `code/ch3` 场景给出；答复框分段并加“在本章的诚实模型中”限定。
- 第二章：sd(W_n) 改为 Var(E)/n + 2σ_e²/(K²n²)；“百局 ≥60%”改报中位数玩家；5.9/8.2、43–57%、0.81 与 0.86、r² 的含义、离散半衰期；ρ→r、AR 系数 φ→ρ、增益 α→b、κ→κ_R；答复框分段。
- 第四章：冻结模型零假设改为校准刻度后的模型，并给出未校准时的误报率；指纹表注明需校准；AlphaGo Zero 的 c_elo 底数脚注；自博弈图注改报期望值；EOMM 段与酒馆战棋段压缩为指针；p→E、σ(·)→Λ(·)、λ→γ_s；答复框分段；小结改为 keybox。
- 第一章：Jabin–Junca 的结论按作者预印本重写（只与相近评分者对局时可能卡在依赖初值的亚稳平衡）；CS:GO 改引 2014-09-11 的 Valve 员工原评论（【官方】）；王者荣耀 2018 说明按摘录原句；“近 1000 页证据”改引 `zhang2026hokfeb`；原告指控改标【社区】；Respawn 以长期留存作为上线标准；Szczecinski 改为“模型解耦原则”，arXiv 预印本首次出现处注明；Cheng 28.7%、Yuksel、AlphaStar、Riot 衰减原因、EA 专利表、法院“四个焦点”只披露两点等措辞修正；长段落拆分；删去 ch1a 末段重复的“从另一端入手”。
- 全文：`\evtag` 放进盒子并禁止其后断行；`\ind` 示性函数；页眉不再大写；式号格式“式（2.5）”，第三章 `式\eqref` 改 `\cref`；`\emph` 改为加粗；标题页 Alph、前置部分罗马页码；问题速答与两个“下一步”进目录并加标签；第一章目录加“上篇/下篇”；引言新增“局部记号”与“术语对照”表；“功效→检验力”“车队→组排”“Monte Carlo→蒙特卡洛”“logistic→逻辑斯蒂”“用户→提问者”；多处标题缩短避免孤字。
- 参考文献：新增 `vitaliy2014comment`；修正 `zajonc2020complaint`、`yashkov2016applications`、`oneesports2024valorant` 著录；`iTero`、`u/renecotyfanboy` 用 `\NoCaseChange` 防止首字母大写；两条 AAAI 改为 `@article`；学位论文加地点、导师移到 `addendum`。各章 bib 与 `refs.bib` 一致（`ch3.bib` 补入 `jabin2015continuous`）。
- 文档：`docs/STYLE.md` 增加诉讼材料与预印本的标签规则、术语与 Λ/ρ/b/\ind 记号；`docs/TO_VERIFY.md` 移出 Jabin–Junca、CS:GO 原评论、AlphaStar MMR 三条，补记 Respawn、iTero、ONE Esports、AlphaGo Zero 的核对，Véron 条更新原因。

### 未解决
- Véron 等全文 PDF 仍下载失败；SIAM 版 Jabin–Junca 未与预印本逐字比对。
- 第三章蛇形/最平衡分队场景的评分刻度在统计期内持续拉伸（λ 2.7–4.6），相应数字只是快照。
- 幻灯片（`slides/`）复用的 `ch3/power`、`ch3/manip` 等图已改版，幻灯片尚未同步检查。
