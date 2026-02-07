from pydantic import BaseModel
from typing import Literal


class UserProfile(BaseModel):
    user_id: str
    age: int
    country: str
    full_name: str
    income_level: Literal["low", "medium", "high"]
    occupation: str
    kyc_status: Literal["verified", "pending"]
    risk_profile: Literal["low", "medium", "high"]
    historical_countries: list[str]


class UserBaseline(BaseModel):
    user_id: str
    avg_tx_amount_usd: float
    avg_daily_total_usd: float
    avg_tx_per_day: int
    std_dev_amount: float
    normal_hour_range: list[int]
    excluded_anomalies_count: int = 0
    min_tx_amount_usd: float = 0.0
    max_tx_amount_usd: float = 0.0
