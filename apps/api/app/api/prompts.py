from fastapi import APIRouter, Depends, HTTPException
from config.core.auth import get_current_user
from shared.utils.logger import logger
from database.schemas.prompt_schema import (
    PromptMeta,
    PromptDetail,
    PromptRenderRequest,
    PromptRenderResponse,
    PromptListResponse,
)
from database.schemas.prompt_history import PromptHistoryResponse, PromptCommit
from ai.prompt_loader import prompts
import subprocess
from pathlib import Path

router = APIRouter()


@router.get("/", summary="List all prompts", response_model=PromptListResponse)
async def list_prompts(current_user=Depends(get_current_user)):
    try:
        entries = []
        for name in prompts.list_prompts():
            entry = prompts.get(name)
            if not entry:
                continue
            entries.append(
                PromptMeta(
                    name=entry.name,
                    category=entry.category,
                    file_path=str(entry.file_path),
                    frontmatter=entry.frontmatter,
                    body_length=len(entry.body),
                    word_count=len(entry.body.split()),
                )
            )
        return PromptListResponse(total=len(entries), prompts=entries)
    except Exception as e:
        logger.error("Failed to list prompts", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to load prompts")


@router.get("/{name}", summary="Get prompt details by name", response_model=PromptDetail)
async def get_prompt(name: str, current_user=Depends(get_current_user)):
    entry = prompts.get(name)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Prompt '{name}' not found")
    return PromptDetail(
        name=entry.name,
        category=entry.category,
        file_path=str(entry.file_path),
        frontmatter=entry.frontmatter,
        body=entry.body,
        body_length=len(entry.body),
        word_count=len(entry.body.split()),
    )


@router.post("/{name}/render", summary="Render a prompt with variables", response_model=PromptRenderResponse)
async def render_prompt(name: str, req: PromptRenderRequest, current_user=Depends(get_current_user)):
    entry = prompts.get(name)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Prompt '{name}' not found")
    try:
        rendered = entry.render(**req.variables) if req.variables else entry.body
        return PromptRenderResponse(name=entry.name, rendered=rendered, frontmatter=entry.frontmatter)
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Missing variable: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Render failed: {e}")


@router.get("/{name}/history", summary="Get prompt revision history", response_model=PromptHistoryResponse)
async def get_prompt_history(name: str, current_user=Depends(get_current_user)):
    entry = prompts.get(name)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Prompt '{name}' not found")

    repo_root = Path(__file__).resolve().parents[4]
    rel_path = entry.file_path.relative_to(repo_root) if hasattr(entry.file_path, "relative_to") else entry.file_path

    try:
        result = subprocess.run(
            ["git", "log", "--numstat", "--pretty=format:COMMIT%n%H%n%aI%n%an%n%s", "--", str(rel_path)],
            capture_output=True,
            text=True,
            cwd=repo_root,
            timeout=10,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        raise HTTPException(status_code=500, detail="Git history unavailable")

    commits = []
    blocks = result.stdout.strip().split("COMMIT\n")[1:] if "COMMIT" in result.stdout else []

    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 4:
            continue
        h, date, author, msg = lines[:4]
        additions = 0
        deletions = 0
        for stat_line in lines[4:]:
            parts = stat_line.strip().split("\t")
            if len(parts) >= 3:
                try:
                    additions += int(parts[0]) if parts[0] != "-" else 0
                    deletions += int(parts[1]) if parts[1] != "-" else 0
                except ValueError as e:
                    logger.warn("Failed to parse git stat line in prompt history", error=str(e))

        commits.append(
            PromptCommit(
                hash=h[:8],
                date=date,
                author=author,
                message=msg,
                additions=additions,
                deletions=deletions,
            )
        )

    if not commits:
        from datetime import datetime, timezone

        commits.append(
            PromptCommit(
                hash="initial",
                date=datetime.now(timezone.utc).isoformat(),
                author="system",
                message="Initial version",
                additions=0,
                deletions=0,
            )
        )

    return PromptHistoryResponse(name=name, commits=commits)
