"""重新生成全部图：python code/run_all.py（可加章节名只跑一章，如 python code/run_all.py ch2）。

约定：code/chN/ 下每个 fig_*.py 都能独立运行，并通过 figstyle.save() 写入 figures/chN/。
"""
import runpy
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE))
chapters = sys.argv[1:] or ["ch1", "ch2", "ch3", "ch4"]
for ch in chapters:
    for script in sorted((CODE / ch).glob("fig_*.py")):
        print(f"[{ch}] {script.name}")
        runpy.run_path(str(script), run_name="__main__")
