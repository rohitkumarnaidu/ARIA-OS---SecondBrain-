from pydantic import BaseModel
from typing import Optional


class PromptMeta(BaseModel):
    name: str
    category: str
    file_path: str
    frontmatter: dict
    body_length: int
    word_count: int


class PromptDetail(BaseModel):
    name: str
    category: str
    file_path: str
    frontmatter: dict
    body: str
    body_length: int
    word_count: int


class PromptRenderRequest(BaseModel):
    variables: dict = {}


class PromptRenderResponse(BaseModel):
    name: str
    rendered: str
    frontmatter: dict


class PromptListResponse(BaseModel):
    total: int
    prompts: list[PromptMeta]
