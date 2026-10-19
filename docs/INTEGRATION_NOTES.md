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
