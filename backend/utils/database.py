import json
import uuid
import logging
from datetime import datetime, timezone

from models.user import UserProfile, UserBaseline
from models.transaction import RawTransaction, PreprocessedTransaction
from models.compliance import Regulation, Rulebook
from utils.supabase_client import get_supabase

logger = logging.getLogger(__name__)

VALID_JURISDICTIONS = {"MT", "AE", "KY"}


# ── Profiles ──

def get_all_profiles() -> list[dict]:
    sb = get_supabase()
    res = sb.table("profiles").select("*").execute()
    return res.data


def get_profile(user_id: str) -> dict | None:
    sb = get_supabase()
    res = sb.table("profiles").select("*").eq("user_id", user_id).execute()
    return res.data[0] if res.data else None


# ── Baselines ──

def get_all_baselines() -> list[dict]:
    sb = get_supabase()
    res = sb.table("baselines").select("*").execute()
    return res.data


def get_baseline(user_id: str) -> dict | None:
    sb = get_supabase()
    res = sb.table("baselines").select("*").eq("user_id", user_id).execute()
    return res.data[0] if res.data else None


def upsert_baseline(baseline: UserBaseline) -> None:
    sb = get_supabase()
    data = baseline.model_dump()
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    sb.table("baselines").upsert(data, on_conflict="user_id").execute()


# ── Risk State ──

def get_all_risk_states() -> dict[str, dict]:
    sb = get_supabase()
    res = sb.table("risk_state").select("*").execute()
    return {r["user_id"]: r for r in res.data}


def get_risk_state(user_id: str) -> dict | None:
    sb = get_supabase()
    res = sb.table("risk_state").select("*").eq("user_id", user_id).execute()
    return res.data[0] if res.data else None


def upsert_risk_state(user_id: str, risk_score: int, risk_band: str, risk_profile: str) -> None:
    sb = get_supabase()
    sb.table("risk_state").upsert(
        {
            "user_id": user_id,
            "risk_score": risk_score,
            "risk_band": risk_band,
            "risk_profile": risk_profile,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
        on_conflict="user_id",
    ).execute()


# ── Transactions ──

def get_historical_transactions(user_id: str | None = None) -> dict | list:
    sb = get_supabase()
    query = sb.table("transactions").select("*").order("timestamp", desc=False)
    if user_id:
        query = query.eq("user_id", user_id)
    res = query.execute()
    if user_id:
        return res.data
    grouped: dict[str, list] = {}
    for row in res.data:
        uid = row["user_id"]
        grouped.setdefault(uid, []).append(row)
    return grouped


def save_transactions(transactions: list[dict], batch_id: str | None = None) -> None:
    sb = get_supabase()
    for tx in transactions:
        tx["batch_id"] = batch_id
    sb.table("transactions").insert(transactions).execute()


def save_preprocessed_transactions(
    preprocessed: list[PreprocessedTransaction], batch_id: str
) -> None:
    sb = get_supabase()
    rows = []
    for ptx in preprocessed:
        row = ptx.model_dump()
        row["batch_id"] = batch_id
        row["is_preprocessed"] = True
        rows.append(row)
    sb.table("transactions").insert(rows).execute()


# ── Compliance State ──

def get_compliance_state(jurisdiction_code: str) -> dict | None:
    sb = get_supabase()
    res = (
        sb.table("compliance_state")
        .select("*")
        .eq("jurisdiction_code", jurisdiction_code.upper())
        .execute()
    )
    if not res.data:
        return None
    state = res.data[0]
    rulebook_res = (
        sb.table("rulebooks")
        .select("*")
        .eq("jurisdiction_code", jurisdiction_code.upper())
        .eq("is_active", True)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    rulebook = rulebook_res.data[0]["rulebook"] if rulebook_res.data else {}
    state["rulebook"] = rulebook
    return state


def update_compliance_version(jurisdiction_code: str, new_version: str) -> None:
    sb = get_supabase()
    sb.table("compliance_state").update(
        {
            "current_version": new_version,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("jurisdiction_code", jurisdiction_code).execute()


def add_pushed_regulation(jurisdiction_code: str, regulation_data: dict) -> None:
    sb = get_supabase()
    res = (
        sb.table("compliance_state")
        .select("new_regulations")
        .eq("jurisdiction_code", jurisdiction_code)
        .execute()
    )
    existing = []
    if res.data:
        raw = res.data[0].get("new_regulations", [])
        existing = raw if isinstance(raw, list) else json.loads(raw) if raw else []
    existing.append(regulation_data)
    sb.table("compliance_state").update(
        {"new_regulations": existing}
    ).eq("jurisdiction_code", jurisdiction_code).execute()
    sb.table("new_regulations").update(
        {"is_pushed": True}
    ).eq("regulation_update_id", regulation_data["regulation_update_id"]).execute()


# ── Rulebooks ──

def get_active_rulebook(jurisdiction_code: str) -> dict | None:
    sb = get_supabase()
    res = (
        sb.table("rulebooks")
        .select("*")
        .eq("jurisdiction_code", jurisdiction_code.upper())
        .eq("is_active", True)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return res.data[0] if res.data else None


def save_rulebook(jurisdiction_code: str, version: str, rulebook: dict, activate: bool = True) -> None:
    sb = get_supabase()
    if activate:
        sb.table("rulebooks").update({"is_active": False}).eq(
            "jurisdiction_code", jurisdiction_code
        ).eq("is_active", True).execute()
    sb.table("rulebooks").insert(
        {
            "jurisdiction_code": jurisdiction_code,
            "version": version,
            "rulebook": rulebook,
            "is_active": activate,
        }
    ).execute()


# ── New Regulations ──

def get_available_regulations(jurisdiction_code: str) -> list[dict]:
    sb = get_supabase()
    res = (
        sb.table("new_regulations")
        .select("*")
        .eq("jurisdiction_code", jurisdiction_code.upper())
        .eq("is_pushed", False)
        .execute()
    )
    return res.data


def get_regulation_by_id(regulation_update_id: str) -> dict | None:
    sb = get_supabase()
    res = (
        sb.table("new_regulations")
        .select("*")
        .eq("regulation_update_id", regulation_update_id)
        .execute()
    )
    return res.data[0] if res.data else None


# ── Agent Traces ──

def create_agent_trace(
    trace_type: str,
    user_id: str | None = None,
    jurisdiction_code: str | None = None,
) -> str:
    sb = get_supabase()
    trace_id = str(uuid.uuid4())
    sb.table("agent_traces").insert(
        {
            "id": trace_id,
            "trace_type": trace_type,
            "user_id": user_id,
            "jurisdiction_code": jurisdiction_code,
            "status": "running",
        }
    ).execute()
    return trace_id


def complete_agent_trace(trace_id: str, result: dict | None = None, failed: bool = False) -> None:
    sb = get_supabase()
    sb.table("agent_traces").update(
        {
            "status": "failed" if failed else "completed",
            "result": result,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("id", trace_id).execute()


def save_agent_step(
    trace_id: str,
    step_order: int,
    agent: str,
    icon: str,
    status: str,
    message: str,
    duration_ms: int,
    retry_count: int = 0,
    retry_type: str | None = None,
    output: dict | None = None,
) -> None:
    sb = get_supabase()
    sb.table("agent_steps").insert(
        {
            "trace_id": trace_id,
            "step_order": step_order,
            "agent": agent,
            "icon": icon,
            "status": status,
            "message": message,
            "duration_ms": duration_ms,
            "retry_count": retry_count,
            "retry_type": retry_type,
            "output": output,
        }
    ).execute()


# ── Compliance Drafts (HITL) ──

def create_compliance_draft(
    jurisdiction_code: str,
    proposed_version: str,
    rulebook: dict,
    previous_rulebook: dict,
    changes_description: str,
    summary: str,
    comparison_points: list[str],
    impact_analysis: str,
    agent_chain: list[dict],
    regulation_id: str,
) -> str:
    sb = get_supabase()
    draft_id = str(uuid.uuid4())
    sb.table("compliance_drafts").insert(
        {
            "id": draft_id,
            "jurisdiction_code": jurisdiction_code,
            "proposed_version": proposed_version,
            "rulebook": rulebook,
            "previous_rulebook": previous_rulebook,
            "changes_description": changes_description,
            "summary": summary,
            "comparison_points": comparison_points,
            "impact_analysis": impact_analysis,
            "agent_chain": agent_chain,
            "regulation_id": regulation_id,
            "status": "pending",
        }
    ).execute()
    return draft_id


def get_pending_drafts(jurisdiction_code: str | None = None) -> list[dict]:
    sb = get_supabase()
    query = sb.table("compliance_drafts").select("*").eq("status", "pending")
    if jurisdiction_code:
        query = query.eq("jurisdiction_code", jurisdiction_code.upper())
    res = query.order("created_at", desc=True).execute()
    return res.data


def get_draft_by_id(draft_id: str) -> dict | None:
    sb = get_supabase()
    res = sb.table("compliance_drafts").select("*").eq("id", draft_id).execute()
    return res.data[0] if res.data else None


def approve_draft(draft_id: str, edited_rulebook: dict | None = None) -> dict | None:
    sb = get_supabase()
    draft = get_draft_by_id(draft_id)
    if not draft or draft["status"] != "pending":
        return None

    jc = draft["jurisdiction_code"]
    new_ver = draft["proposed_version"]
    rulebook_data = edited_rulebook if edited_rulebook else draft["rulebook"]
    reg_id = draft["regulation_id"]

    if edited_rulebook:
        sb.table("compliance_drafts").update(
            {"rulebook": edited_rulebook}
        ).eq("id", draft_id).execute()

    save_rulebook(jc, new_ver, rulebook_data, activate=True)
    update_compliance_version(jc, new_ver)

    reg = get_regulation_by_id(reg_id)
    if reg:
        add_pushed_regulation(jc, {
            "regulation_update_id": reg["regulation_update_id"],
            "update_title": reg["update_title"],
            "summary": reg["summary"],
            "date_effective": reg["date_effective"],
        })

    sb.table("compliance_drafts").update(
        {
            "status": "approved",
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("id", draft_id).execute()

    return get_draft_by_id(draft_id)


def reject_draft(draft_id: str) -> dict | None:
    sb = get_supabase()
    draft = get_draft_by_id(draft_id)
    if not draft or draft["status"] != "pending":
        return None
    sb.table("compliance_drafts").update(
        {
            "status": "rejected",
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("id", draft_id).execute()
    return get_draft_by_id(draft_id)


# ── Latest Analysis (stored in agent_traces.result) ──

def get_latest_analysis(user_id: str) -> dict | None:
    sb = get_supabase()
    res = (
        sb.table("agent_traces")
        .select("*")
        .eq("user_id", user_id)
        .eq("trace_type", "transaction_analysis")
        .eq("status", "completed")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if res.data and res.data[0].get("result"):
        result = res.data[0]["result"]
        if isinstance(result, str):
            return json.loads(result)
        return result
    return None
