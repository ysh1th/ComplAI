"""Seed Supabase tables from existing JSON data files."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from utils.supabase_client import get_supabase

DATA_DIR = Path(__file__).parent.parent / "data"


def seed_profiles():
    sb = get_supabase()
    with open(DATA_DIR / "users.json", "r") as f:
        users = json.load(f)
    for u in users:
        u["historical_countries"] = u.get("historical_countries", [])
    sb.table("profiles").upsert(users, on_conflict="user_id").execute()
    print(f"Seeded {len(users)} profiles")


def seed_baselines():
    sb = get_supabase()
    with open(DATA_DIR / "baselines.json", "r") as f:
        baselines = json.load(f)
    for b in baselines:
        b.setdefault("min_tx_amount_usd", 0.0)
        b.setdefault("max_tx_amount_usd", 0.0)
    sb.table("baselines").upsert(baselines, on_conflict="user_id").execute()
    print(f"Seeded {len(baselines)} baselines")


def seed_risk_state():
    sb = get_supabase()
    risk_path = DATA_DIR / "initial_risk_state.json"
    try:
        with open(risk_path, "r") as f:
            risk_data = json.load(f)
    except FileNotFoundError:
        print("No initial_risk_state.json found, skipping")
        return

    rows = []
    for user_id, state in risk_data.items():
        rows.append({
            "user_id": user_id,
            "risk_score": state.get("risk_score", 0),
            "risk_band": state.get("risk_band", "CLEAN"),
            "risk_profile": state.get("risk_profile", "low"),
        })
    sb.table("risk_state").upsert(rows, on_conflict="user_id").execute()
    print(f"Seeded {len(rows)} risk states")


def seed_historical_transactions():
    sb = get_supabase()
    tx_path = DATA_DIR / "historical_transactions.json"
    try:
        with open(tx_path, "r") as f:
            all_tx = json.load(f)
    except FileNotFoundError:
        print("No historical_transactions.json found, skipping")
        return

    rows = []
    for user_id, txs in all_tx.items():
        for tx in txs:
            rows.append({
                "user_id": tx.get("user_id", user_id),
                "timestamp": tx["timestamp"],
                "transaction_amount_usd": tx["transaction_amount_usd"],
                "transaction_currency": tx["transaction_currency"],
                "transaction_type": tx["transaction_type"],
                "transaction_country": tx["transaction_country"],
                "transaction_city": tx["transaction_city"],
                "batch_id": "historical",
                "is_preprocessed": False,
            })

    batch_size = 100
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        sb.table("transactions").insert(batch).execute()
    print(f"Seeded {len(rows)} historical transactions")


def seed_compliance_state():
    sb = get_supabase()
    code_to_file = {"MT": "malta.json", "AE": "uae.json", "KY": "cayman.json"}

    for code, filename in code_to_file.items():
        filepath = DATA_DIR / "compliance" / filename
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Missing {filepath}, skipping")
            continue

        sb.table("compliance_state").upsert(
            {
                "jurisdiction_code": code,
                "jurisdiction": data["jurisdiction"],
                "current_version": data["current_version"],
                "old_regulations": data.get("old_regulations", []),
                "new_regulations": data.get("new_regulations", []),
            },
            on_conflict="jurisdiction_code",
        ).execute()

        rulebook = data.get("rulebook", {})
        existing = (
            sb.table("rulebooks")
            .select("id")
            .eq("jurisdiction_code", code)
            .eq("version", data["current_version"])
            .execute()
        )
        if not existing.data:
            sb.table("rulebooks").insert(
                {
                    "jurisdiction_code": code,
                    "version": data["current_version"],
                    "rulebook": rulebook,
                    "is_active": True,
                }
            ).execute()

    print(f"Seeded compliance state for {list(code_to_file.keys())}")


def seed_new_regulations():
    sb = get_supabase()
    code_to_file = {"MT": "malta_v2.json", "AE": "uae_v2.json", "KY": "cayman_v2.json"}

    total = 0
    for code, filename in code_to_file.items():
        filepath = DATA_DIR / "compliance" / "new_regulations" / filename
        try:
            with open(filepath, "r") as f:
                regs = json.load(f)
        except FileNotFoundError:
            continue

        for reg in regs:
            existing = (
                sb.table("new_regulations")
                .select("id")
                .eq("regulation_update_id", reg["regulation_update_id"])
                .execute()
            )
            if not existing.data:
                sb.table("new_regulations").insert(
                    {
                        "jurisdiction_code": code,
                        "regulation_update_id": reg["regulation_update_id"],
                        "update_title": reg["update_title"],
                        "summary": reg["summary"],
                        "date_effective": reg["date_effective"],
                        "is_pushed": False,
                    }
                ).execute()
                total += 1

    print(f"Seeded {total} new regulations")


def main():
    print("=== Seeding Supabase ===")
    seed_profiles()
    seed_baselines()
    seed_risk_state()
    seed_historical_transactions()
    seed_compliance_state()
    seed_new_regulations()
    print("=== Seeding complete ===")


if __name__ == "__main__":
    main()
