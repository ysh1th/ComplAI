from pydantic import BaseModel
from typing import Optional


class RawTransaction(BaseModel):
    user_id: str
    timestamp: str
    transaction_amount_usd: float
    transaction_currency: str
    transaction_type: str
    transaction_country: str
    transaction_city: str


class PreprocessedTransaction(BaseModel):
    # Carried from raw
    user_id: str
    timestamp: str
    transaction_amount_usd: float
    transaction_currency: str
    transaction_type: str
    transaction_country: str
    transaction_city: str
    # Computed fields (deterministic, local)
    hour_of_day: int = 0
    time_since_last_sec: int = 0
    previous_country: str = ""
    previous_timestamp: str = ""
    distance_km: float = 0.0
    actual_travel_hours: float = 0.0
    daily_total_usd: float = 0.0
    tx_count_per_day: int = 0
    is_new_country: bool = False
