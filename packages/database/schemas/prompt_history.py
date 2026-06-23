from pydantic import BaseModel


class PromptCommit(BaseModel):
    hash: str
    date: str
    author: str
    message: str
    additions: int
    deletions: int


class PromptHistoryResponse(BaseModel):
    name: str
    commits: list[PromptCommit]
