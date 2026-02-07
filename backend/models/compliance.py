from pydantic import BaseModel
from typing import Any, Optional


class Regulation(BaseModel):
    regulation_update_id: str
    update_title: str
    summary: str
    date_effective: str


class RuleEntry(BaseModel):
    category: str
    rule: str
    points: int


class Rulebook(BaseModel):
    amount_based: list[str]
    frequency_based: list[str]
    location_based: list[str]
    behavioural_pattern: list[str]
    risk_score: dict[str, Any]
    risk_bands: dict[str, str]


class JurisdictionCompliance(BaseModel):
    jurisdiction: str
    jurisdiction_code: str
    current_version: str
    old_regulations: list[Regulation]
    new_regulations: list[Regulation]
    rulebook: Rulebook
