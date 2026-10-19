"""重新生成全部图：python code/run_all.py（可加章节名只跑一章，如 python code/run_all.py ch2）。

约定：code/chN/ 下每个 fig_*.py 都能独立运行，并通过 figstyle.save() 写入 figures/chN/。
每个脚本在独立子进程里运行，避免各章同名模块（如 model.py）互相覆盖。
没有缓存（code/chN/cache/）时从头模拟，四章合计约 21 分钟（4 核实测）；有缓存时几分钟。
"""
import os
import subprocess
import sys
import time
from pathlib import Path

CODE = Path(__file__).resolve().parent
ROOT = CODE.parent
# 子进程输出含中文：Windows 下管道/重定向默认用本地代码页，统一成 UTF-8 以免 UnicodeEncodeError
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}
chapters = sys.argv[1:] or ["ch1", "ch2", "ch3", "ch4"]
failed = []
for ch in chapters:
    t_ch = time.time()
    for script in sorted((CODE / ch).glob("fig_*.py")):
        print(f"[{ch}] {script.name}", flush=True)
        t0 = time.time()
        if subprocess.run([sys.executable, str(script)], cwd=ROOT, env=ENV).returncode != 0:
            failed.append(f"{ch}/{script.name}")
        print(f"[{ch}] {script.name} done in {time.time() - t0:.0f}s", flush=True)
    print(f"[{ch}] total {time.time() - t_ch:.0f}s", flush=True)
if failed:
    sys.exit("失败的脚本：" + ", ".join(failed))
