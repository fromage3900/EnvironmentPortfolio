#!/usr/bin/env python3
"""Read filtered fast-export and pipe to git fast-import."""
import subprocess
import sys

with open(r'C:\EnvironmentPortfolio\.temp_export_clean.fi', 'rb') as f:
    data = f.read()

# Check first bytes
print(f"First 20 bytes: {data[:20].hex()}", file=sys.stderr)
print(f"First line: {data[:data.index(b'\\n')] if b'\\n' in data[:100] else data[:100]}", file=sys.stderr)

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
