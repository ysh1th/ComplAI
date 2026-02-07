"""Profile Agent — Local agent that loads user profile from JSON."""

import json
import time
from pathlib import Path

from models.user import UserProfile
from models.agent_log import AgentLogEntry

DATA_DIR = Path(__file__).parent.parent / "data"


def run_profile_agent(user_id: str) -> tuple[UserProfile, AgentLogEntry]:
    """
    Agent 1: Profile Agent (Local)
    Loads user profile from data/users.json.
    """
    start = time.time()

    users_path = DATA_DIR / "users.json"
    with open(users_path, "r") as f:
        users = json.load(f)

    user_data = None
    for u in users:
        if u["user_id"] == user_id:
            user_data = u
            break

    if user_data is None:
        duration_ms = int((time.time() - start) * 1000)
        raise ValueError(f"User {user_id} not found")

    profile = UserProfile(**user_data)
    duration_ms = int((time.time() - start) * 1000)

    jurisdiction_map = {"MT": "Malta", "AE": "UAE", "KY": "Cayman Islands"}
    jurisdiction = jurisdiction_map.get(profile.country, profile.country)

    log = AgentLogEntry(
        agent="Profile Agent",
        icon="🔍",
        status="success",
        message=f"Loaded {profile.user_id} ({profile.full_name}, {jurisdiction}, {profile.income_level} income, {profile.kyc_status} KYC)",
        duration_ms=max(duration_ms, 10),
    )

    return profile, log
