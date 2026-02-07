"""Rulebook Editor Agent — LLM agent that modifies the rulebook based on analysis."""

import json
import time
import logging

from models.compliance import Rulebook
from models.agent_log import AgentLogEntry
from utils.llm import call_llm_json

logger = logging.getLogger(__name__)


async def run_rulebook_editor_agent(
    impact_analysis: str,
    current_rulebook: Rulebook,
    jurisdiction: str,
    jurisdiction_code: str,
    new_version: str,
) -> tuple[Rulebook, str, AgentLogEntry]:
    """
    Agent 8: Rulebook Editor Agent (LLM)
    Modifies the rulebook based on impact analysis.
    Returns: (updated_rulebook, changes_description, log_entry)
    """
    start = time.time()

    current_rulebook_json = json.dumps(current_rulebook.model_dump(), indent=2)

    system_prompt = """You are a compliance rulebook engineer. Based on impact analysis and the current 
rulebook, make necessary changes to the monitoring rulebook. Return ONLY valid JSON."""

    user_prompt = f"""Impact Analysis:
{impact_analysis}

Current Rulebook for {jurisdiction}:
{current_rulebook_json}

Your task:
1. Review each category (amount_based, frequency_based, location_based, behavioural_pattern) 
   and determine if rules need updating
2. Review the risk_score rules and determine if point values or conditions need adjusting
3. Add new rules if the new regulation introduces requirements not currently covered
4. Adjust risk_bands descriptions if thresholds have changed

Return the COMPLETE updated rulebook as valid JSON with the same structure.
Also provide a brief description of what you changed and why.

Return format:
{{
  "updated_rulebook": {{
    "amount_based": [...],
    "frequency_based": [...],
    "location_based": [...],
    "behavioural_pattern": [...],
    "risk_score": {{
      "range": "0-100",
      "rules": [...],
      "capping": "min(risk_score, 100)"
    }},
    "risk_bands": {{...}}
  }},
  "changes_description": "Brief description of changes made"
}}"""

    try:
        result = await call_llm_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
        )

        rulebook_data = result.get("updated_rulebook", {})
        changes_description = result.get("changes_description", "Rulebook updated based on new regulation.")

        updated_rulebook = Rulebook(**rulebook_data)

    except Exception as e:
        logger.warning(f"Rulebook Editor LLM failed: {e}")
        # Fallback: add a generic rule
        updated_rulebook = current_rulebook.model_copy(deep=True)
        updated_rulebook.behavioural_pattern.append(
            "Enhanced monitoring required under new regulatory framework"
        )
        changes_description = "Added enhanced monitoring rule (LLM fallback)."

    duration_ms = int((time.time() - start) * 1000)

    # Count changes
    old_rule_count = (
        len(current_rulebook.amount_based)
        + len(current_rulebook.frequency_based)
        + len(current_rulebook.location_based)
        + len(current_rulebook.behavioural_pattern)
    )
    new_rule_count = (
        len(updated_rulebook.amount_based)
        + len(updated_rulebook.frequency_based)
        + len(updated_rulebook.location_based)
        + len(updated_rulebook.behavioural_pattern)
    )
    rules_added = max(0, new_rule_count - old_rule_count)

    log = AgentLogEntry(
        agent="Rulebook Editor Agent",
        icon="✏️",
        status="complete",
        message=f"Rulebook updated — {rules_added} rules added/modified. {changes_description[:80]}",
        duration_ms=max(duration_ms, 100),
    )

    return updated_rulebook, changes_description, log
