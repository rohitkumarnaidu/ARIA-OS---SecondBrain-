import re
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class PromptEntry:
    def __init__(self, frontmatter: Dict[str, Any], body: str, file_path: Path):
        self.frontmatter = frontmatter
        self.body = body
        self.file_path = file_path
        self.name = file_path.stem
        self.category = "root"
        self._loaded_at = datetime.now()

    @property
    def system_prompt(self) -> str:
        return self.body

    @property
    def agent_prompt(self) -> str:
        return self.body

    def render(self, **kwargs) -> str:
        if not kwargs:
            return self.body
        try:
            return self.body.format(**kwargs)
        except KeyError:
            return self.body

    def validate(self) -> List[str]:
        errors = []
        fm = self.frontmatter
        required = ["version", "status", "model", "max_tokens", "temperature"]
        for field in required:
            if field not in fm:
                errors.append(f"Missing required field: {field}")
        if fm.get("status") not in ("active", "draft", "deprecated"):
            errors.append(f"Invalid status: {fm.get('status')}")
        if not isinstance(fm.get("max_tokens"), (int, float)):
            errors.append("max_tokens must be a number")
        if not isinstance(fm.get("temperature"), (int, float)):
            errors.append("temperature must be a number")
        return errors


class PromptLoaderError(Exception):
    pass


class PromptLoader:
    def __init__(self, prompts_dir: Optional[Path] = None):
        self.root = prompts_dir or (Path(__file__).resolve().parent.parent.parent / "prompts")
        self._entries: Dict[str, PromptEntry] = {}
        self._load_all()

    def _parse_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        match = re.match(r"^---\s*\n(.*?\n)---\s*\n(.*)", content, re.DOTALL)
        if match:
            frontmatter = yaml.safe_load(match.group(1)) or {}
            body = match.group(2).strip()
            return frontmatter, body
        return {}, content.strip()

    def _load_all(self):
        self._entries.clear()
        for md_file in sorted(self.root.rglob("*.md")):
            if md_file.name == "README.md":
                continue
            relative = md_file.relative_to(self.root)
            category = relative.parts[0] if len(relative.parts) > 1 else "root"
            content = md_file.read_text(encoding="utf-8-sig")
            frontmatter, body = self._parse_frontmatter(content)
            entry = PromptEntry(frontmatter, body, md_file)
            entry.category = category
            key = f"{category}/{md_file.stem}"
            self._entries[key] = entry
            self._entries[md_file.stem] = entry

    def reload(self):
        self._load_all()

    def get(self, name: str, category: Optional[str] = None) -> Optional[PromptEntry]:
        if category:
            return self._entries.get(f"{category}/{name}")
        return self._entries.get(name)

    def get_required(self, name: str, category: Optional[str] = None) -> PromptEntry:
        entry = self.get(name, category)
        if not entry:
            raise PromptLoaderError(f"Prompt '{name}' not found in category '{category}'")
        return entry

    def get_system(self, name: str) -> Optional[PromptEntry]:
        return self.get(name, category="system")

    def get_agent(self, name: str) -> Optional[PromptEntry]:
        return self.get(name, category="agents")

    def get_template(self, name: str) -> Optional[PromptEntry]:
        return self.get(name, category="templates")

    def list_prompts(self, category: Optional[str] = None) -> List[str]:
        if category:
            return sorted(k.split("/", 1)[1] for k in self._entries if k.startswith(f"{category}/"))
        return sorted(self._entries.keys())

    def list_categories(self) -> List[str]:
        cats = set()
        for key in self._entries:
            if "/" in key:
                cats.add(key.split("/", 1)[0])
        return sorted(cats)

    def validate_frontmatter(self, name: str) -> List[str]:
        entry = self.get(name)
        if not entry:
            return ["Prompt not found"]
        return entry.validate()

    def validate_all(self) -> Dict[str, List[str]]:
        results = {}
        for key in self._entries:
            errors = self.validate_frontmatter(key)
            if errors:
                results[key] = errors
        return results

    def count_prompts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for key in self._entries:
            if "/" in key:
                cat = key.split("/", 1)[0]
                counts[cat] = counts.get(cat, 0) + 1
            else:
                counts["root"] = counts.get("root", 0) + 1
        return counts


prompts = PromptLoader()
