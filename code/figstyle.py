"""全文统一的绘图风格。所有出图脚本都应 `from figstyle import use, save, SERIES, INK`。

配色取自一套经色觉缺陷校验的分类色板（按固定顺序取用，不循环）；
文字一律用墨色，系列颜色只用于线和点。
"""
from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figures"

# 分类色：按序号取用；>=4 个系列时同时加直接标注或线型区分
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
# 单色顺序色（蓝，浅→深），用于热图/连续量
SEQ_BLUE = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5",
            "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
# 发散色：蓝 ↔ 灰 ↔ 红
DIV = ("#2a78d6", "#f0efec", "#e34948")
INK = {"primary": "#0b0b0b", "secondary": "#52514e", "muted": "#898781",
       "grid": "#e1e0d9", "axis": "#c3c2b7"}
LINESTYLES = ["-", "--", "-.", ":"]

CJK_FONTS = ["Noto Sans CJK SC", "Source Han Sans SC", "Microsoft YaHei", "SimHei",
             "PingFang SC", "WenQuanYi Zen Hei", "DejaVu Sans"]

# 版心宽约 15.8 cm
WIDTH_FULL = 6.2   # 英寸，整栏
WIDTH_HALF = 3.0   # 英寸，并排子图


def use() -> None:
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": CJK_FONTS,
        "axes.unicode_minus": False,
        "mathtext.fontset": "dejavusans",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "legend.fontsize": 8,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "text.color": INK["primary"],
        "axes.labelcolor": INK["secondary"],
        "xtick.color": INK["muted"],
        "ytick.color": INK["muted"],
        "axes.edgecolor": INK["axis"],
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": INK["grid"],
        "grid.linewidth": 0.5,
        "axes.axisbelow": True,
        "axes.prop_cycle": mpl.cycler(color=SERIES),
        "lines.linewidth": 1.6,
        "lines.markersize": 4,
        "legend.frameon": False,
        "figure.figsize": (WIDTH_FULL, 3.4),
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def save(fig: plt.Figure, chapter: str, name: str) -> Path:
    """保存为 figures/<chapter>/<name>.pdf（论文用）和 .png（预览/幻灯片用）。"""
    out = FIG_DIR / chapter
    out.mkdir(parents=True, exist_ok=True)
    pdf = out / f"{name}.pdf"
    fig.savefig(pdf)
    fig.savefig(out / f"{name}.png")
    plt.close(fig)
    return pdf
