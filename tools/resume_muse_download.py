"""Resume the Muse-Glimmer-30B download using huggingface_hub (memory-efficient streaming).

The Rust `hf` CLI hit a memory-allocation error on the large shards. This uses the
Python huggingface_hub snapshot_download which streams in chunks and resumes partial
files, avoiding the OOM.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from huggingface_hub import snapshot_download

REPO = "meta-models/Muse-Glimmer-30B"
REVISION = "a4e59da52a7bc87ae7251dd5545c0dd437c44b68"
LOCAL_DIR = Path(r"G:\AI\Models\weights\Muse-Glimmer-30B-direct")


def main() -> None:
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Resuming download of {REPO} @ {REVISION[:8]} into {LOCAL_DIR}", flush=True)
    path = snapshot_download(
        repo_id=REPO,
        revision=REVISION,
        local_dir=str(LOCAL_DIR),
        local_dir_use_symlinks=False,
        resume_download=True,
        max_workers=1,  # single worker to keep memory low
    )
    print(f"Download complete: {path}", flush=True)


if __name__ == "__main__":
    main()