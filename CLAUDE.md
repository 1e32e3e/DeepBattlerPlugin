# 项目说明（给本地或云端的 Claude Code）

这是一个研究项目：游戏中的 Elo / 匹配机制。成果是一篇中文 LaTeX 论文和一套 Beamer 幻灯片，四章对应四项研究：

1. 研究一（`paper/chapters/ch1a.tex` 学术研究，`ch1b.tex` 厂商披露、专利、诉讼）
2. 研究二（`ch2.tex`）：不干涉匹配时胜率能否计算，和人数、分数、实力、实力波动的关系
3. 研究三（`ch3.tex`）：诚实系统会不会制造“Elo 感”（连败、连胜后连败），上头等实力波动模型
4. 研究四（`ch4.tex`）：训练视角——目标是胜率还是实力，收敛后的胜负数据

## 目录

- `paper/`：论文。`main.tex` 入口，`preamble.tex` 公共宏，`chapters/` 各章，`refs/` 参考文献。
- `slides/`：幻灯片，复用 `figures/` 里的图。
- `code/`：推导验证、模拟与出图脚本；`code/figstyle.py` 是统一绘图风格；`code/run_all.py` 重新生成全部图。
- `figures/chN/`：生成的图（PDF 给论文，PNG 给幻灯片和预览）。
- `research_notes/游戏Elo匹配与胜率研究/`：第一版研究笔记、模拟脚本与对抗性核查记录（`verify_*.md`）。
- `reports/`：第一版 Markdown 报告（已被论文取代，仅存档）。
- `docs/STYLE.md`：写作、记号、证据标签、出图规范。**改任何章节前先读。**
- `docs/ROADMAP.md`：后续计划（社交平台阴谋论收集与检验；用户本人对局数据分析）。
- `docs/TO_VERIFY.md`：没读到全文、需要在校园网下核对的来源清单。
- `data/`：个人对局数据模板；原始数据放 `data/private/`（不入库）。

## 常用命令

```bash
pip install -r code/requirements.txt
python code/run_all.py            # 全部重新出图；python code/run_all.py ch3 只跑第三章
cd paper && latexmk -xelatex main.tex
cd slides && latexmk -xelatex slides.tex
```

出图耗时（4 核 Linux 实测）：没有缓存时全部约 21 分钟（第一章约 10 秒、第二章约 3.5 分钟、第三章约 16.5 分钟、第四章约 1 分钟；最慢的 `ch3/fig_power.py` 约 8.5 分钟）；模拟结果缓存在 `code/chN/cache/`（不入库），有缓存时几分钟。第三章正文数字由 `python code/ch3/ch3_numbers.py` 打印，它还需要另外约 20 组模拟，首次运行约 12 分钟。论文编译约 1 分钟。图都已入库，只改正文时不必重新出图。

Windows 本地：安装 TeX Live（含 latexmk、biber、ctex、biblatex-gb7714-2015）和 Python 3.11+。ctex 会自动使用 Windows 自带中文字体；`figstyle.py` 会依次尝试思源黑体、微软雅黑、黑体（找不到前几个字体时打印的 `findfont: Font family ... not found` 可忽略；换字体后文字宽度略有变化，出图后看一遍 PNG，若负号“−”显示成方框，说明所选字体缺这个字符）。Windows PowerShell 5.1 不支持 `&&`，改用 `cd paper; latexmk -xelatex main.tex`。单独运行脚本、输出重定向到文件时若报 `UnicodeEncodeError`，先设环境变量 `PYTHONUTF8=1`（`run_all.py` 已为子进程设好 UTF-8）。

## 约定

- 改正文时同步检查：图注里的参数与脚本一致；数字与 `research_notes/.../verify_*.md` 的核查结论一致。
- 新的事实性说法必须有真实出处并加证据标签；只读到摘要的加 `\needcheck` 并登记到 `docs/TO_VERIFY.md`。
- 改完至少编译一次论文，确认没有未定义引用（`main.log` 中无 `undefined`）。
- 论文和幻灯片的 PDF（`paper/main.pdf`、`slides/slides.pdf`）入库，方便直接阅读；中间文件不入库。
