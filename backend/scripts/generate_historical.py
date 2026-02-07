"""
Generate 5 days of historical transaction data for all users.
Run once to create backend/data/historical_transactions.json.

Usage:
    cd backend
    uv run python scripts/generate_historical.py
"""

import json
import random
import statistics
from pathlib import Path
from datetime import datetime, timedelta, timezone

DATA_DIR = Path(__file__).parent.parent / "data"

AMOUNT_RANGES = {
    "low": (20, 200),
    "medium": (50, 500),
    "high": (100, 2000),
}

CURRENCIES = ["ETH", "BTC", "USDT", "SOL", "ADA", "DOT", "AVAX"]
TX_TYPES = ["deposit", "withdrawal", "transfer"]

COUNTRY_CITIES = {
    "MT": ["Valletta", "Sliema", "St. Julian's", "Mdina"],
    "IT": ["Rome", "Milan", "Florence", "Naples"],
    "DE": ["Berlin", "Munich", "Frankfurt", "Hamburg"],
    "GB": ["London", "Manchester", "Edinburgh", "Birmingham"],
    "AE": ["Dubai", "Abu Dhabi", "Sharjah", "Ajman"],
    "SA": ["Riyadh", "Jeddah", "Dammam", "Mecca"],
    "BH": ["Manama", "Riffa", "Muharraq"],
    "PK": ["Islamabad", "Karachi", "Lahore"],
    "KY": ["George Town", "West Bay", "Bodden Town"],
    "US": ["New York", "Miami", "Los Angeles", "Chicago"],
}


def get_city(country_code: str) -> str:
    cities = COUNTRY_CITIES.get(country_code, ["Unknown City"])
    return random.choice(cities)


def generate_user_history(user: dict, num_days: int = 5) -> list[dict]:
    """Generate num_days of normal transaction history for a user."""
    income = user["income_level"]
    lo, hi = AMOUNT_RANGES.get(income, (50, 500))
    countries = user["historical_countries"]

    txs = []
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    for day_offset in range(num_days, 0, -1):
        day = today - timedelta(days=day_offset)
        # 2-5 transactions per day (normal behavior)
        num_tx = random.randint(2, 5)

        for i in range(num_tx):
            hour = random.randint(8, 21)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            ts = day.replace(hour=hour, minute=minute, second=second)

            country = random.choice(countries)
            amount = round(random.uniform(lo, hi), 2)

            txs.append({
                "user_id": user["user_id"],
                "timestamp": ts.isoformat(),
                "transaction_amount_usd": amount,
                "transaction_currency": random.choice(CURRENCIES),
                "transaction_type": random.choice(TX_TYPES),
                "transaction_country": country,
                "transaction_city": get_city(country),
            })

    # Sort by timestamp
    txs.sort(key=lambda t: t["timestamp"])
    return txs


def compute_baseline_from_history(user_id: str, txs: list[dict]) -> dict:
    """Compute a baseline from historical transactions, including min/max."""
    amounts = [t["transaction_amount_usd"] for t in txs]
    hours = []
    daily_totals: dict[str, float] = {}
    daily_counts: dict[str, int] = {}

    for t in txs:
        try:
            ts = datetime.fromisoformat(t["timestamp"].replace("Z", "+00:00"))
            hours.append(ts.hour)
            day_key = ts.strftime("%Y-%m-%d")
        except Exception:
            day_key = "unknown"
        daily_totals[day_key] = daily_totals.get(day_key, 0) + t["transaction_amount_usd"]
        daily_counts[day_key] = daily_counts.get(day_key, 0) + 1

    avg_amount = statistics.mean(amounts) if amounts else 100
    std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 30
    avg_daily = statistics.mean(daily_totals.values()) if daily_totals else 300
    avg_tx_per_day = int(statistics.mean(daily_counts.values())) if daily_counts else 3
    min_hour = min(hours) if hours else 9
    max_hour = max(hours) if hours else 18

    return {
        "user_id": user_id,
        "avg_tx_amount_usd": round(avg_amount, 2),
        "avg_daily_total_usd": round(avg_daily, 2),
        "avg_tx_per_day": avg_tx_per_day,
        "std_dev_amount": round(std_dev, 2),
        "normal_hour_range": [min_hour, max_hour],
        "excluded_anomalies_count": 0,
        "min_tx_amount_usd": round(min(amounts), 2),
        "max_tx_amount_usd": round(max(amounts), 2),
    }


def compute_initial_risk(user: dict, txs: list[dict], baseline: dict) -> dict:
    """
    Compute initial risk score from historical data characteristics.
    Uses income level, number of countries, trade volume relative to income.
    """
    score = 0

    # Factor 1: Income vs trade volume mismatch
    income = user.get("income_level", "medium")
    avg_amount = baseline.get("avg_tx_amount_usd", 100)
    income_ceilings = {"low": 150, "medium": 400, "high": 1500}
    ceiling = income_ceilings.get(income, 400)
    if avg_amount > ceiling:
        score += 10

    # Factor 2: Number of countries in history (more = higher baseline risk)
    num_countries = len(user.get("historical_countries", []))
    if num_countries >= 3:
        score += 8
    elif num_countries >= 2:
        score += 3

    # Factor 3: High std deviation = volatile trading
    std_dev = baseline.get("std_dev_amount", 30)
    if std_dev > avg_amount * 0.5:
        score += 5

    # Factor 4: High daily volume
    avg_daily = baseline.get("avg_daily_total_usd", 300)
    daily_ceilings = {"low": 300, "medium": 1000, "high": 4000}
    daily_cap = daily_ceilings.get(income, 1000)
    if avg_daily > daily_cap:
        score += 7

    # Small randomness
    score += random.randint(0, 5)
    score = min(score, 60)

    if score >= 75:
        band = "HIGH"
    elif score >= 50:
        band = "MEDIUM"
    elif score >= 25:
        band = "LOW"
    else:
        band = "CLEAN"

    return {"risk_score": score, "risk_band": band}


def derive_risk_profile(risk_score: int) -> str:
    """Derive the static risk_profile label from the computed risk score."""
    if risk_score >= 50:
        return "high"
    elif risk_score >= 25:
        return "medium"
    else:
        return "low"


def main():
    random.seed(42)  # Reproducible

    with open(DATA_DIR / "users.json", "r") as f:
        users = json.load(f)

    all_history = {}
    all_baselines = []
    all_initial_risk = {}

    for user in users:
        uid = user["user_id"]
        history = generate_user_history(user, num_days=5)
        all_history[uid] = history

        baseline = compute_baseline_from_history(uid, history)
        all_baselines.append(baseline)

        risk = compute_initial_risk(user, history, baseline)
        all_initial_risk[uid] = risk

        # Derive risk_profile from the computed score so they're consistent
        user["risk_profile"] = derive_risk_profile(risk["risk_score"])

    # Save updated users.json (with derived risk_profile)
    with open(DATA_DIR / "users.json", "w") as f:
        json.dump(users, f, indent=2)
    print(f"Saved users.json ({len(users)} users — risk_profile derived from scores)")

    # Save historical transactions
    with open(DATA_DIR / "historical_transactions.json", "w") as f:
        json.dump(all_history, f, indent=2)
    print(f"Saved historical_transactions.json ({sum(len(v) for v in all_history.values())} total transactions)")

    # Save baselines (with min/max)
    with open(DATA_DIR / "baselines.json", "w") as f:
        json.dump(all_baselines, f, indent=2)
    print(f"Saved baselines.json ({len(all_baselines)} baselines)")

    # Save initial risk state
    with open(DATA_DIR / "initial_risk_state.json", "w") as f:
        json.dump(all_initial_risk, f, indent=2)
    print(f"Saved initial_risk_state.json ({len(all_initial_risk)} users)")

    # Print summary
    for b in all_baselines:
        uid = b["user_id"]
        risk = all_initial_risk[uid]
        user = next(u for u in users if u["user_id"] == uid)
        num_tx = len(all_history[uid])
        print(
            f"  {uid}: {num_tx} txs, "
            f"avg ${b['avg_tx_amount_usd']:.0f}, "
            f"range ${b['min_tx_amount_usd']:.0f}-${b['max_tx_amount_usd']:.0f}, "
            f"risk {risk['risk_score']}/{risk['risk_band']}, "
            f"profile={user['risk_profile']}"
        )


if __name__ == "__main__":
    main()
