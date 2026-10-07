#!/usr/bin/env python3
"""Count selected kernel-message patterns without treating lines as incidents."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_PATTERNS = {
    "page_fault_messages": r"page\s+fault",
    "gpu_fault_messages": r"gpu\s+fault",
}


def summarize_text(text: str, patterns: dict[str, str] | None = None) -> dict[str, object]:
    selected = DEFAULT_PATTERNS if patterns is None else patterns
    counts = {
        name: len(re.findall(pattern, text, flags=re.IGNORECASE | re.MULTILINE))
        for name, pattern in selected.items()
    }
    return {
        "counts": counts,
        "interpretation": "Counts are matching log messages, not independent fault incidents.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Count selected messages in a kernel-log extract")
    parser.add_argument("log", type=Path)
    args = parser.parse_args()
    result = summarize_text(args.log.read_text(encoding="utf-8", errors="replace"))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
