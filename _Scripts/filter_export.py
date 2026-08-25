#!/usr/bin/env python3
"""Filter git fast-export stream to remove dotnet6/ and dotnet10/ entries."""
import sys
import re

# Patterns for file/directory removal
REMOVE_PREFIXES = ('dotnet6/', 'dotnet10/', 'dotnet6\\', 'dotnet10\\')

def should_remove(path):
    return any(path.startswith(p) for p in REMOVE_PREFIXES)

in_data_section = False
data_remaining = 0
skip_this_entry = False
is_delete = False
current_path = ""

for line in iter(sys.stdin.readline, ''):
    if in_data_section:
        # Raw data section - just pass through (it was already checked)
        sys.stdout.write(line)
        data_remaining -= len(line)
        if data_remaining <= 0:
            in_data_section = False
            if skip_this_entry and not is_delete:
                # Skip the trailing newline after data
                pass
        continue

    if line.startswith('data '):
        # Data section follows
        data_remaining = int(line.split()[1])
        if not skip_this_entry:
            sys.stdout.write(line)
        in_data_section = True
        if data_remaining == 0:
            in_data_section = False
        continue

    if line.startswith('blob'):
        # New blob entry
        skip_this_entry = False
        is_delete = False
        sys.stdout.write(line)
        continue

    if line.startswith('commit '):
        # New commit
        skip_this_entry = False
        is_delete = False
        sys.stdout.write(line)
        continue

    if line.startswith('reset '):
        skip_this_entry = False
        is_delete = False
        sys.stdout.write(line)
        continue

    if line.startswith('tag '):
        skip_this_entry = False
        is_delete = False
        sys.stdout.write(line)
        continue

    if line.startswith('progress '):
        sys.stdout.write(line)
        continue

    if line.startswith('feature '):
        sys.stdout.write(line)
        continue

    if line.startswith('done'):
        sys.stdout.write(line)
        continue

    # File modification commands
    if line.startswith('D '):
        # Delete operation
        path = line[2:].strip()
        if should_remove(path):
            skip_this_entry = True
        else:
            sys.stdout.write(line)
        continue

    if line.startswith('M '):
        # Modify operation - mark and path
        parts = line.split('\t', 1)
        if len(parts) == 2:
            rest = parts[0]  # "M 100644 :mark" or "M 040000 :mark"
            path = parts[1].strip()
            if should_remove(path):
                skip_this_entry = True
            else:
                sys.stdout.write(line)
        else:
            sys.stdout.write(line)
        continue

    if line.startswith('C '):
        path = line[2:].strip()
        if should_remove(path):
            skip_this_entry = True
        else:
            sys.stdout.write(line)
        continue

    if line.startswith('R '):
        parts = line[2:].split('\t', 1)
        if len(parts) == 2:
            old_path, new_path = parts
            if should_remove(old_path) or should_remove(new_path):
                skip_this_entry = True
            else:
                sys.stdout.write(line)
        else:
            sys.stdout.write(line)
        continue

    if line.startswith('tag '):
        sys.stdout.write(line)
        continue

    if line.startswith('from '):
        if not skip_this_entry:
            sys.stdout.write(line)
        continue

    if line.startswith('merge '):
        if not skip_this_entry:
            sys.stdout.write(line)
        continue

    if line.startswith('commit '):
        skip_this_entry = False
        sys.stdout.write(line)
        continue

    if line.startswith('author ') or line.startswith('committer '):
        if not skip_this_entry:
            sys.stdout.write(line)
        continue

    if line.startswith('mark '):
        if not skip_this_entry:
            sys.stdout.write(line)
        continue

    if line.startswith('original-oid '):
        if not skip_this_entry:
            sys.stdout.write(line)
        continue

    if line.startswith('deleteall'):
        sys.stdout.write(line)
        # don't skip anything in deleteall context
        continue

    # For any other line, pass through if not skipping
    if not skip_this_entry:
        sys.stdout.write(line)
