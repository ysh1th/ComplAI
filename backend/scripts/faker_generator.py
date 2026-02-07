"""Faker-based transaction data generator."""

import random
from datetime import datetime, timedelta, timezone
from typing import Optional
from faker import Faker

from models.user import UserProfile
from models.transaction import RawTransaction

fake = Faker()

# Amount ranges by income level
AMOUNT_RANGES = {
    "low": (20, 200),
    "medium": (50, 500),
    "high": (100, 2000),
}

# Common crypto currencies
CURRENCIES = ["ETH", "BTC", "USDT", "SOL", "ADA", "DOT", "AVAX"]

# Transaction types
TX_TYPES = ["deposit", "withdrawal", "transfer"]

# City lookup by country
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
    "KP": ["Pyongyang", "Hamhung", "Chongjin"],
    "IR": ["Tehran", "Isfahan", "Mashhad"],
    "SY": ["Damascus", "Aleppo", "Homs"],
    "CU": ["Havana", "Santiago de Cuba", "Camagüey"],
    "RU": ["Moscow", "Saint Petersburg", "Novosibirsk"],
    "CN": ["Beijing", "Shanghai", "Shenzhen"],
    "JP": ["Tokyo", "Osaka", "Kyoto"],
    "IN": ["New Delhi", "Mumbai", "Bangalore"],
    "SG": ["Singapore"],
    "NG": ["Abuja", "Lagos", "Kano"],
    "ZA": ["Cape Town", "Johannesburg", "Pretoria"],
    "JM": ["Kingston", "Montego Bay"],
    "QA": ["Doha"],
    "FR": ["Paris", "Lyon", "Marseille"],
    "ES": ["Madrid", "Barcelona", "Seville"],
}


def _get_city_for_country(country_code: str) -> str:
    """Get a random city for a country code."""
    cities = COUNTRY_CITIES.get(country_code)
    if cities:
        return random.choice(cities)
    return fake.city()


def _generate_amount(
    min_amount: Optional[float],
    max_amount: Optional[float],
    variance: Optional[float],
    default_range: tuple[float, float],
) -> float:
    """
    Generate a random transaction amount.
    
    - If min/max provided: generate randomly within [min, max]
    - If variance provided: add gaussian noise with that std dev around the midpoint
    - If nothing provided: use the user's income-based default range
    """
    if min_amount is not None and max_amount is not None:
        midpoint = (min_amount + max_amount) / 2.0
        half_range = (max_amount - min_amount) / 2.0

        if variance is not None and variance > 0:
            # Gaussian around midpoint, clamped to [min, max]
            amount = random.gauss(midpoint, variance)
            amount = max(min_amount, min(max_amount, amount))
        else:
            amount = random.uniform(min_amount, max_amount)
        return round(amount, 2)

    elif min_amount is not None:
        # Only min: use min as floor with default ceiling
        hi = max(min_amount * 2, default_range[1])
        return round(random.uniform(min_amount, hi), 2)

    elif max_amount is not None:
        # Only max: use default floor with max as ceiling
        lo = min(default_range[0], max_amount * 0.1)
        return round(random.uniform(lo, max_amount), 2)

    else:
        # Default: use income-based range
        return round(random.uniform(*default_range), 2)


def _generate_timestamps_for_today(num_transactions: int) -> list[str]:
    """Generate timestamps for a single day (today), spread across business hours."""
    now = datetime.now(timezone.utc)
    base = now.replace(hour=8, minute=0, second=0, microsecond=0)
    hours_spread = min(12, max(1, num_transactions))
    total_minutes = hours_spread * 60

    timestamps = []
    for i in range(num_transactions):
        offset_minutes = (i * total_minutes) // max(num_transactions, 1)
        offset_minutes += random.randint(0, max(1, total_minutes // (num_transactions + 1)))
        ts = base + timedelta(minutes=offset_minutes, seconds=random.randint(0, 59))
        timestamps.append(ts.isoformat())

    timestamps.sort()
    return timestamps


def generate_transactions(
    user_id: str,
    user_profile: UserProfile,
    num_transactions: int = 5,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    variance: Optional[float] = None,
    countries: Optional[list[str]] = None,
    overrides: Optional[dict] = None,
) -> list[RawTransaction]:
    """
    Generate a batch of transactions for a user — all for a single day (today).

    Amount generation:
      - If min_amount/max_amount provided: random within that range
      - If variance provided: gaussian noise around the midpoint
      - Otherwise: use the user's income-based default range

    Countries:
      - If countries list provided: randomly assign each tx to one of those countries
      - Otherwise: use user's historical_countries

    Overrides: currency, city overrides still work for geo injection.
    """
    transactions = []

    # Use explicit countries list if provided, otherwise fall back to historical
    country_pool = countries if countries and len(countries) > 0 else user_profile.historical_countries
    default_range = AMOUNT_RANGES.get(user_profile.income_level, (50, 500))
    timestamps = _generate_timestamps_for_today(num_transactions)

    for i in range(num_transactions):
        country = random.choice(country_pool)

        amount = _generate_amount(min_amount, max_amount, variance, default_range)

        tx = {
            "user_id": user_id,
            "timestamp": timestamps[i],
            "transaction_amount_usd": amount,
            "transaction_currency": random.choice(CURRENCIES),
            "transaction_type": random.choice(TX_TYPES),
            "transaction_country": country,
            "transaction_city": _get_city_for_country(country),
        }

        # Apply overrides (currency, city — but NOT amount or country which have dedicated params)
        if overrides:
            for key, value in overrides.items():
                if value is not None and value != "" and key != "transaction_country":
                    tx[key] = value

            # If city was overridden, use it; otherwise city already matches the country
            if "transaction_city" not in (overrides or {}):
                tx["transaction_city"] = _get_city_for_country(tx["transaction_country"])

        transactions.append(RawTransaction(**tx))

    return transactions
