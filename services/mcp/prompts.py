"""MCP prompt templates — bridges ARIA OS PromptLoader with MCP prompt format."""

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "packages"))

import mcp.types as types
from mcp.types import Prompt, PromptArgument, GetPromptResult, PromptMessage, TextContent

from ai.prompt_loader import prompts
from shared.utils.logger import logger


class MCPPromptRegistry:
    """Registry of MCP prompts backed by ARIA OS PromptLoader.

    Discovers all prompts from the PromptLoader singleton and exposes them
    through the MCP prompt interface with argument substitution.
    """

    def __init__(self):
        self._prompts: list[Prompt] = []
        self._discovered = False

    def discover(self):
        """Discover all prompts from PromptLoader and convert to MCP format."""
        self._prompts = []
        all_prompt_names = prompts.list_prompts()

        for name in all_prompt_names:
            entry = prompts.get(name)
            if entry is None:
                continue

            frontmatter = entry.frontmatter or {}
            description = frontmatter.get("description", f"Prompt template for {name}")

            mcp_prompt = Prompt(
                name=name,
                description=description,
                arguments=[
                    PromptArgument(
                        name="user_id",
                        description="Authenticated user ID",
                        required=True,
                    ),
                ],
            )
            self._prompts.append(mcp_prompt)

        logger.info("MCP prompts discovered", count=len(self._prompts))
        self._discovered = True

    def list_prompts(self) -> list[Prompt]:
        if not self._discovered:
            self.discover()
        return self._prompts

    def get_prompt(self, name: str, arguments: dict[str, str]) -> GetPromptResult:
        """Resolve a prompt by name with argument substitution."""
        entry = prompts.get_agent(name) or prompts.get_template(name) or prompts.get_system(name)
        if entry is None:
            return GetPromptResult(
                description=f"Unknown prompt: {name}",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Prompt '{name}' not found. Available prompts: {', '.join(p.name for p in self._prompts)}",
                        ),
                    )
                ],
            )

        frontmatter = entry.frontmatter or {}
        body = entry.body
        description = frontmatter.get("description", f"Prompt template for {name}")

        if arguments and body:
            try:
                body = entry.render(**arguments)
            except KeyError:
                body = entry.body

        version = frontmatter.get("version", "unknown")
        model = frontmatter.get("model", "default")

        return GetPromptResult(
            description=description,
            messages=[
                PromptMessage(
                    role="system",
                    content=TextContent(
                        type="text",
                        text=f"Version: {version} | Model: {model}\n\n{body}",
                    ),
                ),
            ],
        )
