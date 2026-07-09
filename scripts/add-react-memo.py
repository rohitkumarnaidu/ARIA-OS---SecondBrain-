#!/usr/bin/env python3
"""Batch-add React.memo to all UI component files."""

import re
from pathlib import Path

UI_DIR = Path("apps/web/components/ui")
SKIP_PATTERNS = (".stories.", ".test.", ".bench.")
SYS_ENCODING = "utf-8"

ALREADY_MEMO = re.compile(r"import\s*\{[^}]*\bmemo\b[^}]*\}\s*from\s*['\"]react['\"]")
REACT_IMPORT = re.compile(r"(import\s*\{)([^}]*)(\}\s*from\s*['\"]react['\"])")


def add_memo_import(content: str) -> str:
    def replacer(m: re.Match) -> str:
        body = m.group(2).strip()
        items = [x.strip() for x in body.split(",") if x.strip()]
        if "memo" in items:
            return m.group(0)
        if not items:
            return f"{m.group(1)} memo {m.group(3)}"
        return f"{m.group(1)} memo, {m.group(2)} {m.group(3)}"

    return REACT_IMPORT.sub(replacer, content)


def wrap_forward_ref_components(content: str) -> str:
    """Wrap `const X = forwardRef<...>(...)` with memo()."""
    lines = content.split("\n")
    result = []

    for i, line in enumerate(lines):
        m = re.match(r"(const\s+\w+\s*=\s*)forwardRef<", line)
        if m:
            m.group(1)
            comp_name_match = re.search(r"const\s+(\w+)\s*=", line)
            comp_name = comp_name_match.group(1) if comp_name_match else None

            # Replace `= forwardRef<` with `= memo(forwardRef<`
            line = line.replace("= forwardRef<", "= memo(forwardRef<", 1)

            if comp_name:
                # Scan forward for displayName line
                for j in range(i + 1, len(lines)):
                    stripped = lines[j].strip()
                    if f"{comp_name}.displayName" in stripped:
                        # Add ')' at the end of the previous line
                        prev_idx = j - 1
                        prev_stripped = lines[prev_idx].rstrip()
                        lines[prev_idx] = prev_stripped + ")"
                        break

        result.append(line)

    return "\n".join(result)


def wrap_plain_functions(content: str) -> str:
    """Replace `function X(...)` with `const X = memo(function X(...)` for pascal-cased functions."""

    def replacer(m: re.Match) -> str:
        m.group(1) or ""
        name = m.group(2)
        return f"const {name} = memo(function {name}("

    return re.sub(
        r"^(export\s+)?function\s+([A-Z]\w*)\s*\(",
        replacer,
        content,
        flags=re.MULTILINE,
    )


def process_file(fp: Path) -> bool:
    content = fp.read_text(encoding=SYS_ENCODING)
    original = content

    if ALREADY_MEMO.search(content):
        return False

    content = add_memo_import(content)
    content = wrap_forward_ref_components(content)
    content = wrap_plain_functions(content)

    if content != original:
        fp.write_text(content, encoding=SYS_ENCODING)
        return True
    return False


def main():
    count = 0
    for fp in sorted(UI_DIR.iterdir()):
        if fp.suffix != ".tsx":
            continue
        if any(p in fp.name for p in SKIP_PATTERNS):
            continue
        if fp.name in ("index.ts", "utils.ts"):
            continue

        if process_file(fp):
            print(f"  OK {fp.name}")
            count += 1
        else:
            print(f"  -- {fp.name}")

    print(f"\nDone - {count} files transformed")


if __name__ == "__main__":
    main()
