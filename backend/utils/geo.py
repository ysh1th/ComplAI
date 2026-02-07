"""Geo utility functions for distance/speed calculations."""

import math
from typing import Optional

# Approximate coordinates for countries (capital cities)
COUNTRY_COORDS: dict[str, tuple[float, float]] = {
    # Europe
    "MT": (35.9375, 14.3754),    # Malta - Valletta
    "IT": (41.9028, 12.4964),    # Italy - Rome
    "DE": (52.5200, 13.4050),    # Germany - Berlin
    "GB": (51.5074, -0.1278),    # UK - London
    "FR": (48.8566, 2.3522),     # France - Paris
    "ES": (40.4168, -3.7038),    # Spain - Madrid
    # Middle East
    "AE": (25.2048, 55.2708),    # UAE - Dubai
    "SA": (24.7136, 46.6753),    # Saudi Arabia - Riyadh
    "BH": (26.2285, 50.5860),    # Bahrain - Manama
    "QA": (25.2854, 51.5310),    # Qatar - Doha
    "PK": (33.6844, 73.0479),    # Pakistan - Islamabad
    # Caribbean
    "KY": (19.2869, -81.3674),   # Cayman Islands - George Town
    "US": (38.9072, -77.0369),   # USA - Washington DC
    "JM": (18.1096, -77.2975),   # Jamaica - Kingston
    # Asia
    "CN": (39.9042, 116.4074),   # China - Beijing
    "JP": (35.6762, 139.6503),   # Japan - Tokyo
    "IN": (28.6139, 77.2090),    # India - New Delhi
    "SG": (1.3521, 103.8198),    # Singapore
    # Risky jurisdictions
    "KP": (39.0392, 125.7625),   # North Korea - Pyongyang
    "IR": (35.6892, 51.3890),    # Iran - Tehran
    "SY": (33.5138, 36.2765),    # Syria - Damascus
    "CU": (23.1136, -82.3666),   # Cuba - Havana
    "RU": (55.7558, 37.6173),    # Russia - Moscow
    # Africa
    "NG": (9.0579, 7.4951),      # Nigeria - Abuja
    "ZA": (-33.9249, 18.4241),   # South Africa - Cape Town
}

# Maximum commercial aircraft speed (km/h)
MAX_TRAVEL_SPEED_KMH = 800.0


def get_country_coords(country_code: str) -> Optional[tuple[float, float]]:
    """Get approximate coordinates for a country code."""
    return COUNTRY_COORDS.get(country_code.upper())


def calculate_distance_km(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Calculate distance between two points using Haversine formula."""
    R = 6371.0  # Earth radius in km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(R * c, 1)


def calculate_min_travel_hours(distance_km: float) -> float:
    """Calculate minimum travel time at max commercial speed."""
    if distance_km <= 0:
        return 0.0
    return round(distance_km / MAX_TRAVEL_SPEED_KMH, 2)


def get_distance_between_countries(country1: str, country2: str) -> float:
    """Calculate distance between two countries using their capital coordinates."""
    if country1 == country2:
        return 0.0

    coords1 = get_country_coords(country1)
    coords2 = get_country_coords(country2)

    if not coords1 or not coords2:
        return 0.0

    return calculate_distance_km(coords1[0], coords1[1], coords2[0], coords2[1])
