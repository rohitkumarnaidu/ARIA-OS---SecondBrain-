#!/usr/bin/env python3
"""Validate Document ID frontmatter in all docs/*.md files.

Checks every Document Control table for a valid Document ID.
Valid format: {PREFIX}-{TOPIC}-{NUM} where NUM is 3 digits.
"""

import re
import sys
from pathlib import Path

DOCS_DIR = Path("docs")
DOC_ID_PATTERN = re.compile(r"^[A-Z]+-[A-Z]+-\d{3}$")
TABLE_ROW_PATTERN = re.compile(r"^\|\s*Document ID\s*\|\s*(?P<doc_id>\S+)\s*\|")


def find_doc_id(content: str) -> str | None:
    for line in content.splitlines():
        m = TABLE_ROW_PATTERN.search(line)
        if m:
            return m.group("doc_id")
    return None


def main() -> int:
    md_files = sorted(DOCS_DIR.rglob("*.md"))
    errors = []

    for fp in md_files:
        content = fp.read_text(encoding="utf-8")
        doc_id = find_doc_id(content)
        if doc_id is None:
            errors.append(
                f"{fp.relative_to(DOCS_DIR.parent)}: Missing Document ID in Document Control table"
            )
            continue
        if not DOC_ID_PATTERN.match(doc_id):
            errors.append(
                f"{fp.relative_to(DOCS_DIR.parent)}: Invalid Document ID format "
                f"(expected PREFIX-TOPIC-NNN, got {doc_id!r})"
            )

    if errors:
        print(f"Found {len(errors)} document ID violation(s):\n")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"All {len(md_files)} documents have valid Document IDs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
