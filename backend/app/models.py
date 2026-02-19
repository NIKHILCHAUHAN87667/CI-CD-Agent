from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class ErrorType(str, Enum):
    LINTING = "LINTING"
    SYNTAX = "SYNTAX"
    LOGIC = "LOGIC"
    TYPE_ERROR = "TYPE_ERROR"
    IMPORT = "IMPORT"
    INDENTATION = "INDENTATION"
    UNKNOWN = "UNKNOWN"


class ErrorInfo(BaseModel):
    file: str
    line: int
    type: ErrorType
    message: str


class FixResult(BaseModel):
    file: str
    line: int
    type: str
    commit_message: str
    status: str


class AgentRequest(BaseModel):
    repo_url: str
    team: str
    leader: str
    max_retries: int = 5


class AgentResponse(BaseModel):
    repo: str
    branch: str
    total_failures: int
    total_fixes: int
    iterations: int
    status: str
    fixes: List[FixResult]
    id: Optional[int] = None
    created_at: Optional[str] = None
    duration: Optional[str] = None
    repo_name: Optional[str] = None
