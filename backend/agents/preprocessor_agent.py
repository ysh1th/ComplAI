"""Preprocessor Agent — Local/deterministic enrichment of raw transactions."""

import time
from datetime import datetime

from models.user import UserProfile
from models.transaction import RawTransaction, PreprocessedTransaction
from models.agent_log import AgentLogEntry
from utils.geo import get_distance_between_countries, calculate_min_travel_hours


def run_preprocessor_agent(
    transactions: list[RawTransaction],
    profile: UserProfile,
) -> tuple[list[PreprocessedTransaction], AgentLogEntry]:
    """
    Agent 2: Preprocessor Agent (Local)
    Enriches raw transactions with computed fields.
    """
    start = time.time()

    preprocessed = []
    daily_totals: dict[str, float] = {}
    daily_counts: dict[str, int] = {}
    prev_country = profile.country
    prev_timestamp = ""
    max_distance = 0.0
    max_time_delta = 0
    total_daily = 0.0
    any_new_country = False

    for i, tx in enumerate(transactions):
        # Parse timestamp
        try:
            ts = datetime.fromisoformat(tx.timestamp.replace("Z", "+00:00"))
        except Exception:
            ts = datetime.now()

        hour_of_day = ts.hour
        date_key = ts.strftime("%Y-%m-%d")

        # Track daily totals
        daily_totals[date_key] = daily_totals.get(date_key, 0) + tx.transaction_amount_usd
        daily_counts[date_key] = daily_counts.get(date_key, 0) + 1

        # Time since last transaction
        time_since_last_sec = 0
        if prev_timestamp:
            try:
                prev_ts = datetime.fromisoformat(prev_timestamp.replace("Z", "+00:00"))
                time_since_last_sec = max(0, int((ts - prev_ts).total_seconds()))
            except Exception:
                time_since_last_sec = 0

        if time_since_last_sec > 0:
            max_time_delta = max(max_time_delta, time_since_last_sec)

        # Distance calculation — only meaningful when we have a real previous transaction
        # (i.e. prev_timestamp exists). Without it, the "prev_country" is just the user's
        # home country and the distance is misleading for speed/geo-hop analysis.
        if prev_timestamp and prev_country != tx.transaction_country:
            distance_km = get_distance_between_countries(prev_country, tx.transaction_country)
        else:
            distance_km = 0.0
        max_distance = max(max_distance, distance_km)

        # Travel time check
        actual_travel_hours = time_since_last_sec / 3600.0 if time_since_last_sec > 0 else 0
        
        # New country check
        is_new_country = tx.transaction_country not in profile.historical_countries
        if is_new_country:
            any_new_country = True

        ptx = PreprocessedTransaction(
            user_id=tx.user_id,
            timestamp=tx.timestamp,
            transaction_amount_usd=tx.transaction_amount_usd,
            transaction_currency=tx.transaction_currency,
            transaction_type=tx.transaction_type,
            transaction_country=tx.transaction_country,
            transaction_city=tx.transaction_city,
            hour_of_day=hour_of_day,
            time_since_last_sec=time_since_last_sec,
            previous_country=prev_country,
            previous_timestamp=prev_timestamp,
            distance_km=distance_km,
            actual_travel_hours=round(actual_travel_hours, 2),
            daily_total_usd=round(daily_totals[date_key], 2),
            tx_count_per_day=daily_counts[date_key],
            is_new_country=is_new_country,
        )
        preprocessed.append(ptx)

        prev_country = tx.transaction_country
        prev_timestamp = tx.timestamp

    duration_ms = int((time.time() - start) * 1000)

    # Summary for the last transaction (most relevant for display)
    last_ptx = preprocessed[-1] if preprocessed else None
    total_daily = last_ptx.daily_total_usd if last_ptx else 0
    tx_count = last_ptx.tx_count_per_day if last_ptx else 0

    log = AgentLogEntry(
        agent="Preprocessor Agent",
        icon="📊",
        status="success",
        message=(
            f"Preprocessed {len(transactions)} transactions | "
            f"Distance: {max_distance:,.0f}km | "
            f"Time delta: {max_time_delta:,}s | "
            f"Daily total: ${total_daily:,.2f} | "
            f"New country: {'YES' if any_new_country else 'NO'}"
        ),
        duration_ms=max(duration_ms, 20),
    )

    return preprocessed, log
