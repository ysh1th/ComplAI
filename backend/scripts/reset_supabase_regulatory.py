"""
Reset Supabase to initial seed state (users, baselines, risk, transactions, regulatory).
Run from backend/ with: python scripts/reset_supabase_regulatory.py

Requires SUPABASE_URL and SUPABASE_KEY in .env (or environment).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from utils.supabase_client import get_supabase
from scripts.seed_supabase import (
    seed_profiles,
    seed_baselines,
    seed_risk_state,
    seed_historical_transactions,
    seed_compliance_state,
    DATA_DIR,
)

JURISDICTIONS = ["MT", "AE", "KY"]


def _ensure_active_rulebooks():
    sb = get_supabase()
    for code in JURISDICTIONS:
        res = sb.table("compliance_state").select("current_version").eq(
            "jurisdiction_code", code
        ).execute()
        if not res.data:
            continue
        current_version = res.data[0]["current_version"]
        sb.table("rulebooks").update({"is_active": False}).eq(
            "jurisdiction_code", code
        ).execute()
        sb.table("rulebooks").update({"is_active": True}).eq(
            "jurisdiction_code", code
        ).eq("version", current_version).execute()
    print("Set active rulebook to current_version per jurisdiction")


def _reset_risk_state_for_all_users():
    sb = get_supabase()
    with open(DATA_DIR / "users.json", "r") as f:
        users = json.load(f)
    rows = [
        {
            "user_id": u["user_id"],
            "risk_score": 0,
            "risk_band": "CLEAN",
            "risk_profile": "low",
        }
        for u in users
    ]
    sb.table("risk_state").upsert(rows, on_conflict="user_id").execute()
    print(f"Reset risk_state to CLEAN for {len(rows)} users")


def reset_all():
    sb = get_supabase()

    sb.table("agent_steps").delete().gte("id", 0).execute()
    print("Cleared agent_steps")

    sb.table("agent_traces").delete().in_(
        "trace_type", ["transaction_analysis", "compliance_push"]
    ).execute()
    print("Cleared agent_traces")

    sb.table("transactions").delete().gte("id", 0).execute()
    print("Cleared transactions")

    sb.table("compliance_drafts").delete().in_(
        "jurisdiction_code", JURISDICTIONS
    ).execute()
    print("Cleared compliance_drafts")

    sb.table("rulebooks").delete().in_(
        "jurisdiction_code", JURISDICTIONS
    ).execute()
    print("Cleared rulebooks")

    seed_profiles()
    seed_baselines()
    seed_risk_state()
    _reset_risk_state_for_all_users()
    seed_historical_transactions()
    seed_compliance_state()
    _ensure_active_rulebooks()

    for code in JURISDICTIONS:
        sb.table("new_regulations").update({"is_pushed": False}).eq(
            "jurisdiction_code", code
        ).execute()
    print("Set all new_regulations.is_pushed = false")

    print("=== Full reset complete ===")


if __name__ == "__main__":
    reset_all()
