"""Build a secret-safe raw domain corpus from the UE/Monolith workspace.

The output is JSONL with one source file per record. It is suitable for
continued-pretraining or as retrieval/fine-tuning source material, but it is
not an instruction-tuning set: no assistant answers are fabricated.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


TEXT_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".h",
    ".hpp",
    ".inl",
    ".ini",
    ".jinja",
    ".json",
    ".md",
    ".py",
    ".ps1",
    ".uplugin",
    ".uproject",
    ".ush",
    ".usf",
    ".yaml",
    ".yml",
}

EXCLUDED_DIRECTORIES = {
    ".git",
    ".jcode",
    ".vs",
    "Binaries",
    "DerivedDataCache",
    "Intermediate",
    "node_modules",
    "Saved",
}

EXCLUDED_NAME_PARTS = (
    ".env",
    ".mcp.json",
    ".opencode.json",
    "credentials",
    "secret",
    "token",
)

DEFAULT_ROOTS = (
    "BS_GodFile/Plugins/Monolith",
    "BS_GodFile/Source",
    "BS_GodFile/Content/Python",
    "CompatibilityLabs/TurnBasedJRPGUE58/Plugins/Monolith",
    "Docs/Gameplay",
    "Docs/Reports",
)


def is_excluded(path: Path) -> bool:
    if any(part in EXCLUDED_DIRECTORIES for part in path.parts):
        return True
    lowered = path.name.lower()
    return any(part in lowered for part in EXCLUDED_NAME_PARTS)


def language_for(path: Path) -> str:
    return {
        ".cpp": "cpp",
        ".h": "cpp",
        ".hpp": "cpp",
        ".inl": "cpp",
        ".cs": "csharp",
        ".py": "python",
        ".ps1": "powershell",
        ".md": "markdown",
        ".json": "json",
        ".ini": "ini",
        ".usf": "hlsl",
        ".ush": "hlsl",
    }.get(path.suffix.lower(), path.suffix.lower().lstrip("."))


def iter_source_files(workspace: Path, roots: tuple[str, ...], max_bytes: int):
    seen: set[Path] = set()
    for relative_root in roots:
        root = (workspace / relative_root).resolve()
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            if path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            if is_excluded(path) or path.stat().st_size > max_bytes:
                continue
            yield path


def build_corpus(workspace: Path, output: Path, roots: tuple[str, ...], max_bytes: int) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    skipped = 0
    bytes_written = 0
    language_counts: dict[str, int] = {}
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for path in sorted(iter_source_files(workspace, roots, max_bytes)):
            try:
                raw = path.read_bytes()
                text = raw.decode("utf-8-sig")
            except (OSError, UnicodeDecodeError):
                skipped += 1
                continue
            if "\x00" in text:
                skipped += 1
                continue
            relative = path.relative_to(workspace).as_posix()
            record = {
                "id": hashlib.sha256(raw).hexdigest()[:16],
                "source": relative,
                "language": language_for(path),
                "text": text,
            }
            line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
            handle.write(line + "\n")
            count += 1
            bytes_written += len(line.encode("utf-8")) + 1
            language = record["language"]
            language_counts[language] = language_counts.get(language, 0) + 1
    return {
        "workspace": str(workspace),
        "output": str(output),
        "records": count,
        "skipped": skipped,
        "bytes_written": bytes_written,
        "languages": dict(sorted(language_counts.items())),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-file-bytes", type=int, default=2_000_000)
    parser.add_argument("--root", action="append", dest="roots", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workspace = args.workspace.resolve()
    output = args.output.resolve()
    roots = tuple(args.roots or DEFAULT_ROOTS)
    summary = build_corpus(workspace, output, roots, args.max_file_bytes)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
