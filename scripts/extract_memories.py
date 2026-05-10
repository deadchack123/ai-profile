#!/usr/bin/env python3
"""
Extract user+feedback memories from all Claude Code projects.
Outputs grouped markdown to stdout (or to --out path).

Usage:
    python3 extract_memories.py                  # dump to stdout
    python3 extract_memories.py --out raw.md     # dump to file
    python3 extract_memories.py --types user     # only user memories
    python3 extract_memories.py --types user,feedback,project,reference  # all types

Default types: user, feedback (the cross-project applicable ones).
"""
from __future__ import annotations
import argparse
import glob
import sys
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude" / "projects"


def extract(types: set[str]) -> list[tuple[str, str, str, str]]:
    """Return list of (project, filename, type, content) tuples."""
    result = []
    pattern = str(PROJECTS_DIR / "*" / "memory" / "*.md")
    for memory_file in sorted(glob.glob(pattern)):
        path = Path(memory_file)
        try:
            content = path.read_text()
        except Exception as e:
            print(f"# skipped {path}: {e}", file=sys.stderr)
            continue
        head = content[:300]
        memory_type = None
        for t in ("user", "feedback", "project", "reference"):
            if f"type: {t}" in head:
                memory_type = t
                break
        if memory_type is None or memory_type not in types:
            continue
        project = path.parent.parent.name
        result.append((project, path.name, memory_type, content))
    return result


def render(memories: list[tuple[str, str, str, str]]) -> str:
    projects = sorted(set(m[0] for m in memories))
    out = []
    out.append(f"# Extracted memories ({len(memories)} entries from {len(projects)} projects)")
    out.append("")
    out.append("## Projects scanned")
    for p in projects:
        count = sum(1 for m in memories if m[0] == p)
        out.append(f"- `{p}` ({count})")
    out.append("")
    out.append("## Memories by type")
    by_type: dict[str, list] = {}
    for m in memories:
        by_type.setdefault(m[2], []).append(m)
    for t, items in sorted(by_type.items()):
        out.append(f"### {t} ({len(items)})")
        for proj, fname, _, content in items:
            out.append("")
            out.append(f"#### {proj} / {fname}")
            out.append("")
            out.append(content.strip())
            out.append("")
            out.append("---")
        out.append("")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, help="Output file (default: stdout)")
    parser.add_argument(
        "--types",
        default="user,feedback",
        help="Comma-separated memory types to extract (default: user,feedback)",
    )
    args = parser.parse_args()
    types = set(t.strip() for t in args.types.split(","))
    memories = extract(types)
    rendered = render(memories)
    if args.out:
        args.out.write_text(rendered)
        print(f"Wrote {len(memories)} memories to {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(rendered)


if __name__ == "__main__":
    main()
