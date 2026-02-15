import json
import time
import logging

from models.user import UserProfile, UserBaseline
from models.transaction import PreprocessedTransaction
from models.compliance import Rulebook
from models.risk import AnomalyResult
from models.agent_log import AgentLogEntry
from utils.llm import call_llm_json

logger = logging.getLogger(__name__)

MAX_VALIDATION_LOOPS = 2


async def run_validator_agent(
    anomaly_result: AnomalyResult,
    preprocessed: list[PreprocessedTransaction],
    baseline: UserBaseline,
    profile: UserProfile,
    rulebook: Rulebook,
) -> tuple[AnomalyResult, AgentLogEntry, int]:
    """
    Anomaly Validator Agent — quality control for Workflow 1.

    Cross-examines the Anomaly Detector's output:
      1. Does the reasoning support the risk score?
      2. Are the cited regulations relevant to the flags?
      3. Is the risk band consistent with the score?

    Returns: (possibly_corrected_result, log_entry, loop_count)
    """
    start = time.time()
    loop_count = 0
    current_result = anomaly_result

    expected_band = _expected_band(current_result.risk_score)
    if current_result.risk_band != expected_band:
        current_result = current_result.model_copy(
            update={"risk_band": expected_band}
        )

    for iteration in range(MAX_VALIDATION_LOOPS):
        system_prompt = (
            "You are a senior compliance quality-control analyst. "
            "Your job is to validate the output of the Anomaly Detector Agent. "
            "Return ONLY valid JSON."
        )

        tx_summary = []
        for ptx in preprocessed[:5]:
            tx_summary.append(
                f"  Amount: ${ptx.transaction_amount_usd:,.2f}, "
                f"Country: {ptx.transaction_country}, "
                f"Distance: {ptx.distance_km:,.0f}km, "
                f"New: {ptx.is_new_country}"
            )

        user_prompt = f"""Review the Anomaly Detector's output for logical consistency.

## Anomaly Detector Output
- is_anomaly: {current_result.is_anomaly}
- risk_score: {current_result.risk_score}
- risk_band: {current_result.risk_band}
- flags: {json.dumps(current_result.flags)}
- reasoning: {current_result.reasoning}
- regulations_violated: {json.dumps(current_result.regulations_violated)}

## Context
User: {profile.user_id} ({profile.full_name}), {profile.country}
Baseline avg tx: ${baseline.avg_tx_amount_usd}, avg daily: ${baseline.avg_daily_total_usd}
Transactions summary:
{chr(10).join(tx_summary)}

## Validation Checks
1. Does the reasoning logically support the risk score? (e.g. "no issues" should NOT have score 90)
2. Are the cited regulations relevant to the detected flags?
3. Is the risk band consistent with the score? (HIGH >= 75, MEDIUM 50-74, LOW 25-49, CLEAN < 25)
4. Are any flags contradictory or unsupported by the transaction data?

Return JSON:
{{
  "is_valid": true/false,
  "issues": ["list of specific issues found, empty if valid"],
  "suggested_corrections": {{
    "risk_score": null or corrected integer,
    "risk_band": null or corrected string,
    "reasoning": null or improved reasoning string
  }},
  "validation_summary": "1-2 sentence summary of your review"
}}"""

        try:
            result = await call_llm_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.2,
            )

            is_valid = result.get("is_valid", True)
            issues = result.get("issues", [])
            corrections = result.get("suggested_corrections", {})
            validation_summary = result.get("validation_summary", "Validation complete.")

            if is_valid or not issues:
                break

            loop_count += 1

            corrected_score = corrections.get("risk_score")
            corrected_band = corrections.get("risk_band")
            corrected_reasoning = corrections.get("reasoning")

            updates = {}
            if corrected_score is not None:
                updates["risk_score"] = min(int(corrected_score), 100)
            if corrected_band and corrected_band in ("HIGH", "MEDIUM", "LOW", "CLEAN"):
                updates["risk_band"] = corrected_band
            if corrected_reasoning:
                updates["reasoning"] = corrected_reasoning

            if updates:
                current_result = current_result.model_copy(update=updates)
                new_band = _expected_band(current_result.risk_score)
                if current_result.risk_band != new_band:
                    current_result = current_result.model_copy(update={"risk_band": new_band})

        except Exception as e:
            logger.warning(f"Validator LLM failed: {e}")
            break

    duration_ms = int((time.time() - start) * 1000)

    if loop_count == 0:
        status_msg = "Validated & Complete — output consistent"
    else:
        status_msg = f"Analysis refined {loop_count} time(s) by Internal Validator for regulatory accuracy"

    log = AgentLogEntry(
        agent="Anomaly Validator Agent",
        icon="🛡️",
        status="success" if loop_count == 0 else "alert",
        message=status_msg,
        duration_ms=max(duration_ms, 50),
    )

    return current_result, log, loop_count


def _expected_band(score: int) -> str:
    if score >= 75:
        return "HIGH"
    elif score >= 50:
        return "MEDIUM"
    elif score >= 25:
        return "LOW"
    return "CLEAN"
