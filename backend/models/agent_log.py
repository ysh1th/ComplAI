from pydantic import BaseModel
from typing import Literal, Any, Optional

from .user import UserBaseline
from .transaction import PreprocessedTransaction, RawTransaction
from .compliance import Rulebook, Regulation


class AgentLogEntry(BaseModel):
    agent: str
    icon: str
    status: Literal["success", "alert", "high", "complete", "error"]
    message: str
    duration_ms: int


class FullAnalysisResponse(BaseModel):
    user_id: str
    user_name: str
    jurisdiction: str
    risk_score: int
    risk_band: Literal["HIGH", "MEDIUM", "LOW", "CLEAN"]
    risk_profile: Literal["low", "medium", "high"] = "low"
    reasoning: str
    flags: list[str]
    regulations_violated: list[str]
    agent_chain: list[AgentLogEntry]
    preprocessed: PreprocessedTransaction
    baseline: UserBaseline
    generated_transactions: list[RawTransaction]
    timestamp: str


class CompliancePushResponse(BaseModel):
    jurisdiction_code: str
    new_version: str
    summary: str
    comparison_points: list[str]
    impact_analysis: str
    rulebook_changes: str
    updated_rulebook: Rulebook
    agent_chain: list[AgentLogEntry]
