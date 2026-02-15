import json
import time
import logging

from models.compliance import Rulebook
from models.agent_log import AgentLogEntry
from utils.llm import call_llm_json
from utils.rulebook_guardrails import apply_guardrails

logger = logging.getLogger(__name__)

RULEBOOK_OUTPUT_TEMPLATE = """{
  "updated_rulebook": {
    "amount_based": ["rule string 1", "rule string 2"],
    "frequency_based": ["rule string 1"],
    "location_based": ["rule string 1"],
    "behavioural_pattern": ["rule string 1"],
    "risk_score": {
      "range": "0-100",
      "rules": [
        {"category": "Amount", "rule": "description", "points": 0-50},
        {"category": "Geo", "rule": "description", "points": 0-50}
      ],
      "capping": "min(risk_score, 100)"
    },
    "risk_bands": {
      "HIGH": ">=75 description",
      "MEDIUM": "50-74 description",
      "LOW": "25-49 description",
      "CLEAN": "<25"
    }
  },
  "changes_description": "Brief description of changes made"
}"""


async def run_rulebook_editor_agent(
    impact_analysis: str,
    current_rulebook: Rulebook,
    jurisdiction: str,
    jurisdiction_code: str,
    new_version: str,
) -> tuple[Rulebook, str, AgentLogEntry]:
    start = time.time()

    current_rulebook_json = json.dumps(current_rulebook.model_dump(), indent=2)

    system_prompt = (
        "You are a compliance rulebook engineer. Based on impact analysis and the current "
        "rulebook, make necessary changes to the monitoring rulebook.\n"
        "IMPORTANT CONSTRAINTS:\n"
        "- Do NOT delete or rename any top-level keys (amount_based, frequency_based, etc.)\n"
        "- All point values for rules must be between 0 and 50 inclusive\n"
        f"- Only output rules relevant to jurisdiction {jurisdiction_code} ({jurisdiction})\n"
        "- risk_bands must always include HIGH, MEDIUM, LOW, and CLEAN\n"
        "- Return ONLY valid JSON matching the exact template structure."
    )

    user_prompt = f"""Impact Analysis:
{impact_analysis}

Current Rulebook for {jurisdiction} ({jurisdiction_code}):
{current_rulebook_json}

REQUIRED OUTPUT TEMPLATE (follow this structure exactly):
{RULEBOOK_OUTPUT_TEMPLATE}

Your task:
1. Review each category and determine if rules need updating
2. Review the risk_score rules — point values MUST be between 0 and 50
3. Add new rules if the regulation introduces new requirements
4. Keep all existing top-level keys intact
5. Adjust risk_bands descriptions if thresholds changed

Return the COMPLETE updated rulebook as valid JSON with the same structure."""

    guardrail_issues = []

    try:
        result = await call_llm_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
        )

        rulebook_data = result.get("updated_rulebook", {})
        changes_description = result.get("changes_description", "Rulebook updated based on new regulation.")

        rulebook_data, issues = apply_guardrails(
            rulebook_data, jurisdiction_code, current_rulebook
        )
        guardrail_issues.extend(issues)

        updated_rulebook = Rulebook(**rulebook_data)

    except Exception as e:
        logger.warning(f"Rulebook Editor LLM failed: {e}")
        updated_rulebook = current_rulebook.model_copy(deep=True)
        updated_rulebook.behavioural_pattern.append(
            "Enhanced monitoring required under new regulatory framework"
        )
        changes_description = "Added enhanced monitoring rule (LLM fallback)."
        guardrail_issues.append("[FALLBACK] LLM failed, using deterministic fallback")

    duration_ms = int((time.time() - start) * 1000)

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

    guardrail_note = ""
    if guardrail_issues:
        guardrail_note = f" | {len(guardrail_issues)} guardrail corrections applied"

    log = AgentLogEntry(
        agent="Rulebook Editor Agent",
        icon="✏️",
        status="complete",
        message=f"Rulebook updated — {rules_added} rules added/modified. {changes_description[:80]}{guardrail_note}",
        duration_ms=max(duration_ms, 100),
    )

    return updated_rulebook, changes_description, log
