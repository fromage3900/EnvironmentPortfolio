#!/usr/bin/env python3
"""Import LF-converted fast-export stream."""
import subprocess
import sys

with open(r'C:\EnvironmentPortfolio\.temp_export_lf.fi', 'rb') as f:
    data = f.read()

proc = subprocess.Popen(
    ['git', '-C', r'C:\EnvironmentPortfolio\.clean_repo', 'fast-import', '--force'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

stdout, stderr = proc.communicate(input=data)
if stdout:
    print(stdout.decode(errors='replace'), file=sys.stderr)
if stderr:
    print(stderr.decode(errors='replace'), file=sys.stderr)
print(f"Return code: {proc.returncode}", file=sys.stderr)
