"""Probe C3: BLACK_NUM_WORKERS env var vs --workers CLI validation."""
import os
import subprocess
import tempfile
from pathlib import Path

VB = Path.cwd() / ".venv/bin/black"
work = Path(tempfile.mkdtemp(prefix="bkworkers"))
for i in range(3):
    (work / f"f{i}.py").write_text("x = 1\n", "utf-8")


for value in ["abc", "1.5", "0", "-1"]:
    env = dict(os.environ, BLACK_NUM_WORKERS=value)
    r = subprocess.run([str(VB), "--no-cache", "--check", str(work)],
                       capture_output=True, text=True, env=env)
    err = r.stderr.strip().splitlines()
    print(f"--- BLACK_NUM_WORKERS={value!r}: rc={r.returncode}, "
          f"last line: {err[-1] if err else ''!r}, traceback lines: {len(err)}")
print("--- --workers=abc (same knob, CLI channel):")
r = subprocess.run([str(VB), "--no-cache", "--workers=abc", "--check", str(work)],
                   capture_output=True, text=True)
print(f"    rc={r.returncode}")
print("    " + "\n    ".join(r.stderr.strip().splitlines()[-2:]))
print("--- --workers=0 (same knob, CLI channel):")
r = subprocess.run([str(VB), "--no-cache", "--workers=0", "--check", str(work)],
                   capture_output=True, text=True)
print(f"    rc={r.returncode}")
print("    " + "\n    ".join(r.stderr.strip().splitlines()[-2:]))

print("--- 配置文件通道（第三个入口）：workers 写坏 / 写 0")
cfg = Path(tempfile.mkdtemp(prefix="bkcfgworkers"))
for i in range(3):
    (cfg / f"f{i}.py").write_text("x = 1\n", "utf-8")
for v in ['workers = "abc"', "workers = 0"]:
    (cfg / "pyproject.toml").write_text(f"[tool.black]\n{v}\n", "utf-8")
    r = subprocess.run([str(VB), "--no-cache", "--check", str(cfg)],
                       capture_output=True, text=True)
    lines = r.stderr.strip().splitlines()
    print(f"    {v}: rc={r.returncode}, last line: {lines[-1] if lines else ''}")

print("--- 库直调通道（第四个入口）：进程内直接走 reformat_many 读这个环境变量")
from black import WriteBack
from black.concurrency import reformat_many
from black.mode import Mode
from black.report import Report

for value in ["abc", "0"]:
    os.environ["BLACK_NUM_WORKERS"] = value
    try:
        reformat_many(set(), False, WriteBack.NO, Mode(), Report(), None)
        print(f"    env={value!r}: 没抛，静默走完")
    except Exception as e:
        print(f"    env={value!r}: {type(e).__name__}: {str(e).splitlines()[0][:80]}")
del os.environ["BLACK_NUM_WORKERS"]
