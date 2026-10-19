"""重新生成全部图：python code/run_all.py（可加章节名只跑一章，如 python code/run_all.py ch2）。

约定：code/chN/ 下每个 fig_*.py 都能独立运行，并通过 figstyle.save() 写入 figures/chN/。
每个脚本在独立子进程里运行，避免各章同名模块（如 model.py）互相覆盖。
"""
import subprocess
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parent
ROOT = CODE.parent
chapters = sys.argv[1:] or ["ch1", "ch2", "ch3", "ch4"]
failed = []
for ch in chapters:
    for script in sorted((CODE / ch).glob("fig_*.py")):
        print(f"[{ch}] {script.name}", flush=True)
        if subprocess.run([sys.executable, str(script)], cwd=ROOT).returncode != 0:
            failed.append(f"{ch}/{script.name}")
if failed:
    sys.exit("失败的脚本：" + ", ".join(failed))
