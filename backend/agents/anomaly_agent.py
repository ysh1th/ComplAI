"""Anomaly Detector Agent — LLM agent that reasons about anomalies."""

import json
import time
import logging

from models.user import UserProfile, UserBaseline
from models.transaction import PreprocessedTransaction
from models.compliance import Rulebook
from models.risk import AnomalyResult
from models.agent_log import AgentLogEntry
from utils.llm import call_llm_json
from utils.geo import calculate_min_travel_hours

logger = logging.getLogger(__name__)

JURISDICTION_MAP = {"MT": "Malta", "AE": "UAE", "KY": "Cayman Islands"}


def _deterministic_fallback(
    preprocessed: list[PreprocessedTransaction],
    baseline: UserBaseline,
    profile: UserProfile,
    rulebook: Rulebook,
) -> AnomalyResult:
    """Deterministic point-based fallback if LLM fails."""
    total_points = 0
    flags = []
    regulations = []

    for ptx in preprocessed:
        # Amount checks
        if baseline.avg_tx_amount_usd > 0:
            ratio = ptx.transaction_amount_usd / baseline.avg_tx_amount_usd
            if ratio > 5:
                total_points += 55
                flags.append(f"Single tx ${ptx.transaction_amount_usd:,.0f} > 5× avg ${baseline.avg_tx_amount_usd:,.0f} [+55pts]")
            elif ratio > 3:
                total_points += 35
                flags.append(f"Single tx ${ptx.transaction_amount_usd:,.0f} > 3× avg ${baseline.avg_tx_amount_usd:,.0f} [+35pts]")

        # Daily total check
        if baseline.avg_daily_total_usd > 0 and ptx.daily_total_usd > 2 * baseline.avg_daily_total_usd:
            total_points += 30
            flags.append(f"Daily total ${ptx.daily_total_usd:,.0f} > 2× avg daily ${baseline.avg_daily_total_usd:,.0f} [+30pts]")

        # Geo checks
        if ptx.is_new_country:
            total_points += 45
            flags.append(f"New country {ptx.transaction_country} never seen in history [+45pts]")

        if ptx.distance_km > 500 and ptx.time_since_last_sec > 0:
            min_hours = calculate_min_travel_hours(ptx.distance_km)
            if ptx.actual_travel_hours < min_hours:
                speed = ptx.distance_km / max(ptx.actual_travel_hours, 0.01)
                total_points += 60
                flags.append(f"Impossible geo hop: {speed:,.0f} km/h exceeds 800 km/h threshold [+60pts]")

        # Frequency check
        if baseline.avg_tx_per_day > 0 and ptx.tx_count_per_day > 2 * baseline.avg_tx_per_day:
            total_points += 35
            flags.append(f"Frequency spike: {ptx.tx_count_per_day} tx/day > 2× avg {baseline.avg_tx_per_day} [+35pts]")

    # Remove duplicate flags
    flags = list(dict.fromkeys(flags))
    risk_score = min(total_points, 100)

    if risk_score >= 75:
        risk_band = "HIGH"
    elif risk_score >= 50:
        risk_band = "MEDIUM"
    elif risk_score >= 25:
        risk_band = "LOW"
    else:
        risk_band = "CLEAN"

    return AnomalyResult(
        is_anomaly=risk_score >= 25,
        risk_score=risk_score,
        risk_band=risk_band,
        flags=flags,
        reasoning=f"Deterministic analysis: {len(flags)} flags detected with total score {risk_score}/100.",
        regulations_violated=regulations,
    )


async def run_anomaly_agent(
    preprocessed: list[PreprocessedTransaction],
    baseline: UserBaseline,
    profile: UserProfile,
    rulebook: Rulebook,
    jurisdiction_version: str = "v1",
) -> tuple[AnomalyResult, AgentLogEntry]:
    """
    Agent 4: Anomaly Detector Agent (LLM)
    Reasons about anomalies using all context.
    """
    start = time.time()
    jurisdiction = JURISDICTION_MAP.get(profile.country, profile.country)

    # Format transactions for prompt
    tx_details = []
    for ptx in preprocessed:
        speed = 0
        if ptx.actual_travel_hours > 0:
            speed = ptx.distance_km / ptx.actual_travel_hours
        tx_details.append(
            f"- Amount: ${ptx.transaction_amount_usd:,.2f} {ptx.transaction_currency} ({ptx.transaction_type})\n"
            f"  From: {ptx.transaction_city}, {ptx.transaction_country}\n"
            f"  Time: {ptx.timestamp} (hour: {ptx.hour_of_day})\n"
            f"  Distance from previous: {ptx.distance_km:,.0f}km in {ptx.time_since_last_sec}s "
            f"(speed: {speed:,.0f} km/h)\n"
            f"  Daily total so far: ${ptx.daily_total_usd:,.2f}\n"
            f"  Transaction count today: {ptx.tx_count_per_day}\n"
            f"  New country: {ptx.is_new_country}"
        )

    # Format rulebook
    risk_rules = "\n".join([
        f"  - {r['category']}: {r['rule']} [{r['points']} pts]"
        for r in rulebook.risk_score.get("rules", [])
    ])

    system_prompt = """You are a senior compliance analyst at a crypto trading platform.
You are evaluating a user's transactions for anomalies.
You must return ONLY valid JSON with the specified format."""

    user_prompt = f"""## User Profile
- ID: {profile.user_id}
- Name: {profile.full_name}
- Country: {profile.country} ({jurisdiction})
- Income: {profile.income_level}, Occupation: {profile.occupation}
- KYC: {profile.kyc_status}, Risk Profile: {profile.risk_profile}
- Historical countries: {profile.historical_countries}

## User Baseline
- Avg tx amount: ${baseline.avg_tx_amount_usd}
- Avg daily total: ${baseline.avg_daily_total_usd}
- Avg tx per day: {baseline.avg_tx_per_day}
- Std deviation: ${baseline.std_dev_amount}
- Normal hours: {baseline.normal_hour_range}

## Today's Preprocessed Transactions
{chr(10).join(tx_details)}

## Jurisdiction Rulebook ({jurisdiction} — version {jurisdiction_version})
### Amount-based rules:
{chr(10).join(f'- {r}' for r in rulebook.amount_based)}
### Frequency-based rules:
{chr(10).join(f'- {r}' for r in rulebook.frequency_based)}
### Location-based rules:
{chr(10).join(f'- {r}' for r in rulebook.location_based)}
### Behavioural pattern rules:
{chr(10).join(f'- {r}' for r in rulebook.behavioural_pattern)}
### Risk scoring rules:
{risk_rules}
### Risk bands:
{json.dumps(rulebook.risk_bands, indent=2)}

## Your Task
Analyze the transactions against the user's baseline and the jurisdiction rulebook.
For each anomaly found:
1. Identify the specific rule violated
2. Cite the specific regulation/Act
3. Assign points based on the rulebook's scoring table

Then compute the total risk score (capped at 100) and assign a risk band.

Return as JSON:
{{
  "is_anomaly": true/false,
  "risk_score": 0-100,
  "risk_band": "HIGH"/"MEDIUM"/"LOW"/"CLEAN",
  "flags": ["list of specific flags with points"],
  "regulations_violated": ["specific Act names"],
  "reasoning": "2-4 sentence explanation of your analysis, citing specific regulations. Be direct and professional."
}}"""

    try:
        result = await call_llm_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3,
        )

        anomaly_result = AnomalyResult(
            is_anomaly=bool(result.get("is_anomaly", False)),
            risk_score=min(int(result.get("risk_score", 0)), 100),
            risk_band=result.get("risk_band", "CLEAN"),
            flags=result.get("flags", []),
            reasoning=result.get("reasoning", "Analysis completed."),
            regulations_violated=result.get("regulations_violated", []),
        )

    except Exception as e:
        logger.warning(f"Anomaly LLM failed, using fallback: {e}")
        anomaly_result = _deterministic_fallback(preprocessed, baseline, profile, rulebook)

    duration_ms = int((time.time() - start) * 1000)

    # Determine log status based on risk
    if anomaly_result.risk_band == "HIGH":
        status = "high"
    elif anomaly_result.risk_band in ("MEDIUM", "LOW"):
        status = "alert"
    else:
        status = "success"

    log = AgentLogEntry(
        agent="Anomaly Detector Agent",
        icon="🚨",
        status=status,
        message=(
            f"{'ANOMALY DETECTED' if anomaly_result.is_anomaly else 'No anomaly'} — "
            f"Risk: {anomaly_result.risk_score}/100 {anomaly_result.risk_band} | "
            f"{len(anomaly_result.flags)} flags | "
            f"{len(anomaly_result.regulations_violated)} regulations violated"
        ),
        duration_ms=max(duration_ms, 100),
    )

    return anomaly_result, log
