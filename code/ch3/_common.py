"""出图脚本的公共设置：把 code/ 与 code/ch3/ 加入 sys.path，导入统一风格。"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for p in (HERE.parent, HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import matplotlib as mpl  # noqa: E402

from figstyle import INK, SERIES, WIDTH_FULL, save  # noqa: E402,F401
from figstyle import use as _use_base  # noqa: E402

CH = "ch3"

# 第三章的多数图在论文中按 0.7–0.84 倍版心宽排版，字号相应放大约 1.2 倍，排版后约 7–8 pt
FONT_SCALE = 1.2


def use():
    """统一风格（figstyle.use）+ 本章的字号放大。"""
    _use_base()
    for key in ("font.size", "axes.titlesize", "axes.labelsize", "legend.fontsize",
                "xtick.labelsize", "ytick.labelsize"):
        mpl.rcParams[key] = mpl.rcParams[key] * FONT_SCALE


def label_end(ax, x, y, text, dy=0.0, dx_pts=4, **kw):
    """在线的右端加直接标注（墨色文字）。"""
    ax.annotate(text, (x, y), xytext=(dx_pts, dy), textcoords="offset points", va="center",
                fontsize=8 * FONT_SCALE, color=INK["secondary"], **kw)


def log_count_axis(ax):
    """对数横轴上用 10、100、1000 这样的普通数字作刻度。"""
    from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter
    ax.xaxis.set_major_locator(LogLocator(base=10, subs=(1.0, 2.0, 5.0)))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.xaxis.set_minor_formatter(NullFormatter())


def label_at_level(ax, x, y, text, level=0.5, dx_pts=-3, dy_pts=3, side="left"):
    """在曲线首次越过 level 的位置旁加标注；越不过就标在右端。"""
    import numpy as np
    x = np.asarray(x)
    y = np.asarray(y)
    idx = np.flatnonzero(y >= level)
    if idx.size:
        i = idx[0]
        if side == "left":
            ax.annotate(text, (x[i], y[i]), xytext=(dx_pts, dy_pts), textcoords="offset points",
                        ha="right", va="bottom", fontsize=8 * FONT_SCALE, color=INK["secondary"])
        else:
            ax.annotate(text, (x[i], y[i]), xytext=(5, -4), textcoords="offset points",
                        ha="left", va="top", fontsize=8 * FONT_SCALE, color=INK["secondary"])
    else:
        ax.annotate(text, (x[-1], y[-1]), xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=8 * FONT_SCALE, color=INK["secondary"])


def bottom_legend(fig, handles, labels, ncol=5, y=-0.02):
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, y), ncol=ncol,
               frameon=False, fontsize=8 * FONT_SCALE, handlelength=2.2, columnspacing=1.4)
