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
