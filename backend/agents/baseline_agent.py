"""Baseline Calculator Agent — LLM agent that computes/updates user baselines."""

import json
import time
import logging
import statistics
from pathlib import Path
from datetime import datetime

from models.user import UserProfile, UserBaseline
from models.transaction import RawTransaction
from models.agent_log import AgentLogEntry
from utils.llm import call_llm_json

logger = logging.getLogger(__name__)
DATA_DIR = Path(__file__).parent.parent / "data"


def _compute_fallback_baseline(
    user_id: str,
    transactions: list[RawTransaction],
    existing_baseline: UserBaseline | None = None,
) -> UserBaseline:
    """Deterministic fallback if LLM fails."""
    if not transactions:
        if existing_baseline:
            return existing_baseline
        return UserBaseline(
            user_id=user_id,
            avg_tx_amount_usd=100.0,
            avg_daily_total_usd=300.0,
            avg_tx_per_day=3,
            std_dev_amount=30.0,
            normal_hour_range=[9, 18],
            excluded_anomalies_count=0,
        )

    amounts = [tx.transaction_amount_usd for tx in transactions]
    avg_amount = statistics.mean(amounts) if amounts else 100.0
    std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 30.0

    # Group by day
    daily_totals: dict[str, float] = {}
    daily_counts: dict[str, int] = {}
    hours = []

    for tx in transactions:
        try:
            ts = datetime.fromisoformat(tx.timestamp.replace("Z", "+00:00"))
            date_key = ts.strftime("%Y-%m-%d")
            hours.append(ts.hour)
        except Exception:
            date_key = "unknown"

        daily_totals[date_key] = daily_totals.get(date_key, 0) + tx.transaction_amount_usd
        daily_counts[date_key] = daily_counts.get(date_key, 0) + 1

    avg_daily = statistics.mean(daily_totals.values()) if daily_totals else 300.0
    avg_tx_per_day = int(statistics.mean(daily_counts.values())) if daily_counts else 3

    min_hour = min(hours) if hours else 9
    max_hour = max(hours) if hours else 18

    return UserBaseline(
        user_id=user_id,
        avg_tx_amount_usd=round(avg_amount, 2),
        avg_daily_total_usd=round(avg_daily, 2),
        avg_tx_per_day=avg_tx_per_day,
        std_dev_amount=round(std_dev, 2),
        normal_hour_range=[min_hour, max_hour],
        excluded_anomalies_count=0,
    )


def _load_existing_baseline(user_id: str) -> UserBaseline | None:
    """Load existing baseline from baselines.json."""
    baselines_path = DATA_DIR / "baselines.json"
    try:
        with open(baselines_path, "r") as f:
            baselines = json.load(f)
        for b in baselines:
            if b["user_id"] == user_id:
                return UserBaseline(**b)
    except Exception:
        pass
    return None


def _save_baseline(baseline: UserBaseline) -> None:
    """Save updated baseline back to baselines.json."""
    baselines_path = DATA_DIR / "baselines.json"
    try:
        with open(baselines_path, "r") as f:
            baselines = json.load(f)
    except Exception:
        baselines = []

    # Update or append
    found = False
    for i, b in enumerate(baselines):
        if b["user_id"] == baseline.user_id:
            baselines[i] = baseline.model_dump()
            found = True
            break
    if not found:
        baselines.append(baseline.model_dump())

    with open(baselines_path, "w") as f:
        json.dump(baselines, f, indent=2)


async def run_baseline_agent(
    user_id: str,
    transactions: list[RawTransaction],
    profile: UserProfile,
) -> tuple[UserBaseline, AgentLogEntry]:
    """
    Agent 3: Baseline Calculator Agent (LLM)
    Computes/updates user baselines from transaction history.
    """
    start = time.time()
    existing_baseline = _load_existing_baseline(user_id)

    # Format transactions for LLM
    tx_list = "\n".join([
        f"- ${tx.transaction_amount_usd:.2f} {tx.transaction_currency} ({tx.transaction_type}) "
        f"at {tx.timestamp} from {tx.transaction_city}, {tx.transaction_country}"
        for tx in transactions
    ])

    existing_info = ""
    if existing_baseline:
        existing_info = f"""
Previous baseline:
- Avg tx amount: ${existing_baseline.avg_tx_amount_usd}
- Avg daily total: ${existing_baseline.avg_daily_total_usd}
- Avg tx per day: {existing_baseline.avg_tx_per_day}
- Std deviation: ${existing_baseline.std_dev_amount}
- Normal hours: {existing_baseline.normal_hour_range}
"""

    system_prompt = "You are a financial data analyst. Given transaction data for a user, compute their behavioral baseline. Return ONLY valid JSON."

    user_prompt = f"""User: {user_id} ({profile.full_name}), {profile.country}, {profile.income_level} income, {profile.occupation}
{existing_info}
Current batch transactions:
{tx_list}

Compute and return as JSON:
{{
  "avg_tx_amount_usd": <average transaction amount as float>,
  "avg_daily_total_usd": <average total spent per day as float>,
  "avg_tx_per_day": <average number of transactions per day as integer>,
  "std_dev_amount": <standard deviation of transaction amounts as float>,
  "normal_hour_range": [<earliest_typical_hour>, <latest_typical_hour>],
  "excluded_anomalies_count": <how many transactions you'd exclude as outliers as integer>
}}

If there's a previous baseline, weight it 70% and the new data 30% to create a blended baseline.
Return ONLY valid JSON, no explanation."""

    try:
        result = await call_llm_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1,
        )

        baseline = UserBaseline(
            user_id=user_id,
            avg_tx_amount_usd=round(float(result.get("avg_tx_amount_usd", 100)), 2),
            avg_daily_total_usd=round(float(result.get("avg_daily_total_usd", 300)), 2),
            avg_tx_per_day=int(result.get("avg_tx_per_day", 3)),
            std_dev_amount=round(float(result.get("std_dev_amount", 30)), 2),
            normal_hour_range=result.get("normal_hour_range", [9, 18]),
            excluded_anomalies_count=int(result.get("excluded_anomalies_count", 0)),
        )
        source = "LLM"

    except Exception as e:
        logger.warning(f"Baseline LLM failed, using fallback: {e}")
        baseline = _compute_fallback_baseline(user_id, transactions, existing_baseline)
        source = "fallback"

    # Save updated baseline
    _save_baseline(baseline)

    duration_ms = int((time.time() - start) * 1000)

    log = AgentLogEntry(
        agent="Baseline Calculator Agent",
        icon="📈",
        status="success",
        message=(
            f"Baseline computed via {source} — "
            f"avg ${baseline.avg_tx_amount_usd:.0f}/tx, "
            f"${baseline.avg_daily_total_usd:.0f}/day, "
            f"{baseline.avg_tx_per_day} tx/day, "
            f"σ=${baseline.std_dev_amount:.0f}"
        ),
        duration_ms=max(duration_ms, 50),
    )

    return baseline, log
