from enum import Enum
from pydantic import BaseModel
from typing import Literal


class RiskBand(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    CLEAN = "CLEAN"


class AnomalyResult(BaseModel):
    is_anomaly: bool
    risk_score: int
    risk_band: Literal["HIGH", "MEDIUM", "LOW", "CLEAN"]
    flags: list[str]
    reasoning: str
    regulations_violated: list[str]
