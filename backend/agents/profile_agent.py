import time
from models.user import UserProfile
from models.agent_log import AgentLogEntry
from utils.database import get_profile


def run_profile_agent(user_id: str) -> tuple[UserProfile, AgentLogEntry]:
    start = time.time()

    user_data = get_profile(user_id)

    if user_data is None:
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
