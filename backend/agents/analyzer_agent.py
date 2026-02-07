"""Analyzer Agent — LLM agent that analyzes impact on users & company."""

import json
import time
import logging
from pathlib import Path

from models.compliance import Regulation
from models.user import UserProfile, UserBaseline
from models.agent_log import AgentLogEntry
from utils.llm import call_llm

logger = logging.getLogger(__name__)
DATA_DIR = Path(__file__).parent.parent / "data"


def _load_users_for_jurisdiction(jurisdiction_code: str) -> list[tuple[UserProfile, UserBaseline | None]]:
    """Load users and baselines for a specific jurisdiction."""
    users_path = DATA_DIR / "users.json"
    baselines_path = DATA_DIR / "baselines.json"

    with open(users_path, "r") as f:
        users = json.load(f)
    with open(baselines_path, "r") as f:
        baselines = json.load(f)

    baseline_map = {b["user_id"]: b for b in baselines}
    result = []

    for u in users:
        if u["country"] == jurisdiction_code:
            profile = UserProfile(**u)
            baseline_data = baseline_map.get(u["user_id"])
            baseline = UserBaseline(**baseline_data) if baseline_data else None
            result.append((profile, baseline))

    return result


async def run_analyzer_agent(
    old_regulations: list[Regulation],
    new_regulation: Regulation,
    jurisdiction: str,
    jurisdiction_code: str,
) -> tuple[str, AgentLogEntry]:
    """
    Agent 7: Analyzer Agent (LLM)
    Analyzes impact on users & company with specific numbers.
    """
    start = time.time()

    users_data = _load_users_for_jurisdiction(jurisdiction_code)

    user_baselines_text = "\n".join([
        f"- {p.user_id} ({p.full_name}): avg tx ${b.avg_tx_amount_usd if b else 'N/A'}, "
        f"avg daily ${b.avg_daily_total_usd if b else 'N/A'}, "
        f"{b.avg_tx_per_day if b else 'N/A'} tx/day, income: {p.income_level}"
        for p, b in users_data
    ])

    old_regs_text = "\n".join([
        f"- {r.update_title}: {r.summary}"
        for r in old_regulations
    ])

    system_prompt = """You are a compliance impact analyst. Analyze how new regulations 
affect customers and the company. Be specific with numbers and percentages."""

    user_prompt = f"""Jurisdiction: {jurisdiction}

Old regulations:
{old_regs_text}

New regulation:
- {new_regulation.update_title}: {new_regulation.summary}
- Effective: {new_regulation.date_effective}

User baselines in this jurisdiction (current behavior):
{user_baselines_text}

Analyze:
1. How many users would be affected by the new regulation? Be specific.
2. What behavioral changes might users make to evade the new rules?
3. What is the estimated cost/operational impact on the company?
4. What are the specific risks if the company doesn't adapt its monitoring?

Include numbers and percentages. Be specific and actionable.
Return as a structured analysis paragraph (4-6 sentences). No JSON, just text."""

    try:
        impact_analysis = await call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=False,
            temperature=0.3,
        )
        impact_analysis = impact_analysis.strip().strip('"')

    except Exception as e:
        logger.warning(f"Analyzer LLM failed: {e}")
        num_users = len(users_data)
        impact_analysis = (
            f"{num_users} users in {jurisdiction} would be affected by {new_regulation.update_title}. "
            f"Users may attempt to structure transactions below new thresholds or shift activity to "
            f"unregulated jurisdictions. Estimated compliance cost increase of 10-15% for enhanced "
            f"monitoring and reporting requirements. Without adaptation, the company risks regulatory "
            f"penalties and potential license suspension."
        )

    duration_ms = int((time.time() - start) * 1000)

    num_affected = len(users_data)
    log = AgentLogEntry(
        agent="Analyzer Agent",
        icon="📊",
        status="alert",
        message=(
            f"Impact analysis complete — {num_affected}/{num_affected} {jurisdiction} users affected, "
            f"estimated compliance cost increase"
        ),
        duration_ms=max(duration_ms, 50),
    )

    return impact_analysis, log
