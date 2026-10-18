# 游戏中的 Elo 与匹配机制

一项分四部分的研究，成果为中文论文（`paper/main.pdf`）和幻灯片（`slides/slides.pdf`）：

1. **文献与披露**：通用评分/匹配模型的研究、各游戏的专门研究、厂商披露、专利与公司论文。
2. **胜率能否计算**：只有胜负、不干涉匹配时，胜率与每局人数、匹配分数、实力、实力波动的关系（公式推导 + 模拟）。
3. **“Elo 感”从何而来**：纯随机、诚实 Elo 的均值回归、上头等实力波动模型、操纵会留下的指纹。
4. **训练视角**：目标是胜率还是实力，模型收敛后的胜负数据说明了什么。

## 在本地继续

把仓库克隆到本地文件夹（路径含空格，需加引号）：

```powershell
git clone -b claude/modest-ptolemy-l2gvma https://github.com/1e32e3e/DeepBattlerPlugin.git "D:\DRQ\Claude code file\elo learning"
cd "D:\DRQ\Claude code file\elo learning"
```

然后二选一：

- 接着云端会话的上下文继续：在该目录运行 `claude --teleport`，从列表中选这次会话（需要用同一 claude.ai 账号 `claude auth login` 登录，且工作区没有未提交的修改）。
- 开一个新的本地会话：直接运行 `claude`。项目约定在 `CLAUDE.md`，后续计划在 `docs/ROADMAP.md`。

编译与出图见 `CLAUDE.md`。
