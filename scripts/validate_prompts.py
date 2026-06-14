import sys
import yaml
import re
import glob
from pathlib import Path


def validate_all():
    errors = []
    prompt_files = sorted(glob.glob("prompts/**/*.md", recursive=True))

    for fp in prompt_files:
        if fp.endswith("README.md"):
            continue
        with open(fp, encoding="utf-8-sig") as f:
            content = f.read()
        match = re.match(r"^---\s*\n(.*?\n)---", content, re.DOTALL)
        if not match:
            errors.append(f"{fp}: missing YAML frontmatter")
            continue
        try:
            fm = yaml.safe_load(match.group(1))
        except yaml.YAMLError as e:
            errors.append(f"{fp}: YAML parse error: {e}")
            continue
        if not isinstance(fm, dict):
            errors.append(f"{fp}: frontmatter is not a dict")
            continue
        for field in ["version", "status", "model", "max_tokens", "temperature"]:
            if field not in fm:
                errors.append(f"{fp}: missing required field '{field}'")
        if fm.get("status") not in ("active", "draft", "deprecated"):
            errors.append(f"{fp}: invalid status '{fm.get('status')}'")
        if not isinstance(fm.get("max_tokens"), (int, float)):
            errors.append(f"{fp}: max_tokens must be a number")
        if not isinstance(fm.get("temperature"), (int, float)):
            errors.append(f"{fp}: temperature must be a number")

    if errors:
        print(f"\nFAIL: {len(errors)} validation error(s):\n")
        for e in errors:
            print(f"  • {e}")
        sys.exit(1)
    else:
        count = len(prompt_files) - 1  # exclude README
        print(f"\nOK: All {count} prompts validated successfully.")
        sys.exit(0)


if __name__ == "__main__":
    validate_all()
