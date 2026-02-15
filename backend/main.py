import os
import asyncio
import logging
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from models import (
    UserProfile,
    UserBaseline,
    RawTransaction,
    Regulation,
    Rulebook,
    AgentLogEntry,
    FullAnalysisResponse,
    CompliancePushResponse,
)
from agents import (
    run_profile_agent,
    run_preprocessor_agent,
    run_baseline_agent,
    run_anomaly_agent,
    run_validator_agent,
    run_summarizer_agent,
    run_comparison_agent,
    run_analyzer_agent,
    run_rulebook_editor_agent,
)
from scripts.faker_generator import generate_transactions
from utils import database as db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ComplAI — AI Compliance Manager",
    description="AI-powered compliance monitoring for crypto trading (production)",
    version="2.0.0",
)

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
railway_url = os.getenv("RAILWAY_PUBLIC_DOMAIN")
if railway_url:
    ALLOWED_ORIGINS.append(f"https://{railway_url}")
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    ALLOWED_ORIGINS.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Models ──

class IngestBatchRequest(BaseModel):
    user_id: str
    num_transactions: int = 5
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    variance: Optional[float] = None
    countries: Optional[list[str]] = None
    overrides: Optional[dict] = None


class CompliancePushRequest(BaseModel):
    regulation_update_id: str


class DraftApproveRequest(BaseModel):
    edited_rulebook: Optional[dict] = None


# ── API Endpoints ──

@app.get("/api/init")
async def get_init():
    profiles = db.get_all_profiles()
    baselines = db.get_all_baselines()
    risk_states = db.get_all_risk_states()
    all_history = db.get_historical_transactions()

    baseline_map = {b["user_id"]: b for b in baselines}

    result = []
    for u in profiles:
        user_id = u["user_id"]
        baseline = baseline_map.get(user_id, {
            "user_id": user_id,
            "avg_tx_amount_usd": 100.0,
            "avg_daily_total_usd": 300.0,
            "avg_tx_per_day": 3,
            "std_dev_amount": 30.0,
            "normal_hour_range": [9, 18],
            "excluded_anomalies_count": 0,
            "min_tx_amount_usd": 0.0,
            "max_tx_amount_usd": 0.0,
        })

        risk_state = risk_states.get(user_id, {})
        history = all_history.get(user_id, []) if isinstance(all_history, dict) else []

        profile_data = {**u}
        if "risk_profile" in risk_state:
            profile_data["risk_profile"] = risk_state["risk_profile"]

        latest_analysis = db.get_latest_analysis(user_id)

        result.append({
            "profile": profile_data,
            "baseline": baseline,
            "current_risk_score": risk_state.get("risk_score", 0),
            "current_risk_band": risk_state.get("risk_band", "CLEAN"),
            "latest_analysis": latest_analysis,
            "historical_transactions": history,
        })

    return {"users": result}


@app.get("/api/compliance/{jurisdiction_code}")
async def get_compliance_endpoint(jurisdiction_code: str):
    code = jurisdiction_code.upper()
    compliance = db.get_compliance_state(code)
    if not compliance:
        raise HTTPException(status_code=404, detail=f"Unknown jurisdiction: {code}")

    available = db.get_available_regulations(code)

    return {
        **compliance,
        "available_new_regulations": [
            {
                "regulation_update_id": r["regulation_update_id"],
                "update_title": r["update_title"],
                "summary": r["summary"],
                "date_effective": r["date_effective"],
            }
            for r in available
        ],
    }


@app.get("/api/rules/{jurisdiction_code}")
async def get_rules_endpoint(jurisdiction_code: str):
    code = jurisdiction_code.upper()
    compliance = db.get_compliance_state(code)
    if not compliance:
        raise HTTPException(status_code=404, detail=f"Unknown jurisdiction: {code}")
    return {
        "jurisdiction": compliance["jurisdiction"],
        "current_version": compliance["current_version"],
        "rulebook": compliance["rulebook"],
    }


@app.post("/api/ingest-batch")
async def ingest_batch(request: IngestBatchRequest):
    agent_chain: list[AgentLogEntry] = []
    batch_id = str(uuid.uuid4())
    step_order = 0

    trace_id = db.create_agent_trace(
        trace_type="transaction_analysis",
        user_id=request.user_id,
    )

    # 1. Profile Agent
    try:
        profile, profile_log = run_profile_agent(request.user_id)
        agent_chain.append(profile_log)
        step_order += 1
        db.save_agent_step(
            trace_id=trace_id,
            step_order=step_order,
            agent=profile_log.agent,
            icon=profile_log.icon,
            status=profile_log.status,
            message=profile_log.message,
            duration_ms=profile_log.duration_ms,
        )
    except Exception:
        db.complete_agent_trace(trace_id, failed=True)
        raise HTTPException(status_code=404, detail=f"User not found: {request.user_id}")

    jurisdiction_map = {"MT": "Malta", "AE": "UAE", "KY": "Cayman Islands"}
    jurisdiction = jurisdiction_map.get(profile.country, profile.country)

    raw_transactions = generate_transactions(
        user_id=request.user_id,
        user_profile=profile,
        num_transactions=request.num_transactions,
        min_amount=request.min_amount,
        max_amount=request.max_amount,
        variance=request.variance,
        countries=request.countries,
        overrides=request.overrides,
    )

    # 2 & 3. Preprocessor + Baseline in parallel
    preprocessor_task = asyncio.to_thread(
        run_preprocessor_agent, raw_transactions, profile
    )
    baseline_task = run_baseline_agent(request.user_id, raw_transactions, profile)

    (preprocessed, preprocessor_log), (baseline, baseline_log) = await asyncio.gather(
        preprocessor_task, baseline_task
    )

    agent_chain.append(preprocessor_log)
    step_order += 1
    db.save_agent_step(
        trace_id=trace_id,
        step_order=step_order,
        agent=preprocessor_log.agent,
        icon=preprocessor_log.icon,
        status=preprocessor_log.status,
        message=preprocessor_log.message,
        duration_ms=preprocessor_log.duration_ms,
    )

    agent_chain.append(baseline_log)
    step_order += 1
    db.save_agent_step(
        trace_id=trace_id,
        step_order=step_order,
        agent=baseline_log.agent,
        icon=baseline_log.icon,
        status=baseline_log.status,
        message=baseline_log.message,
        duration_ms=baseline_log.duration_ms,
    )

    # 4. Anomaly Detector
    compliance = db.get_compliance_state(profile.country)
    if not compliance:
        db.complete_agent_trace(trace_id, failed=True)
        raise HTTPException(status_code=500, detail="Compliance state not found")

    rulebook = Rulebook(**compliance["rulebook"])

    anomaly_result, anomaly_log = await run_anomaly_agent(
        preprocessed=preprocessed,
        baseline=baseline,
        profile=profile,
        rulebook=rulebook,
        jurisdiction_version=compliance["current_version"],
    )

    agent_chain.append(anomaly_log)
    step_order += 1
    db.save_agent_step(
        trace_id=trace_id,
        step_order=step_order,
        agent=anomaly_log.agent,
        icon=anomaly_log.icon,
        status=anomaly_log.status,
        message=anomaly_log.message,
        duration_ms=anomaly_log.duration_ms,
    )

    # 5. Validator Agent (quality control)
    validated_result, validator_log, validator_loops = await run_validator_agent(
        anomaly_result=anomaly_result,
        preprocessed=preprocessed,
        baseline=baseline,
        profile=profile,
        rulebook=rulebook,
    )
    anomaly_result = validated_result

    validator_log_entry = AgentLogEntry(
        agent=validator_log.agent,
        icon=validator_log.icon,
        status=validator_log.status,
        message=validator_log.message,
        duration_ms=validator_log.duration_ms,
        retry_count=validator_loops,
        retry_type="logical" if validator_loops > 0 else None,
    )
    agent_chain.append(validator_log_entry)
    step_order += 1
    db.save_agent_step(
        trace_id=trace_id,
        step_order=step_order,
        agent=validator_log.agent,
        icon=validator_log.icon,
        status=validator_log.status,
        message=validator_log.message,
        duration_ms=validator_log.duration_ms,
        retry_count=validator_loops,
        retry_type="logical" if validator_loops > 0 else None,
    )

    # Derive risk profile
    if anomaly_result.risk_score >= 50:
        derived_risk_profile = "high"
    elif anomaly_result.risk_score >= 25:
        derived_risk_profile = "medium"
    else:
        derived_risk_profile = "low"

    # Persist risk state to Supabase
    db.upsert_risk_state(
        user_id=request.user_id,
        risk_score=anomaly_result.risk_score,
        risk_band=anomaly_result.risk_band,
        risk_profile=derived_risk_profile,
    )

    # Save preprocessed transactions
    try:
        db.save_preprocessed_transactions(preprocessed, batch_id)
    except Exception as e:
        logger.warning(f"Failed to save preprocessed transactions: {e}")

    last_preprocessed = preprocessed[-1] if preprocessed else preprocessed[0]

    response = FullAnalysisResponse(
        user_id=request.user_id,
        user_name=profile.full_name,
        jurisdiction=jurisdiction,
        risk_score=anomaly_result.risk_score,
        risk_band=anomaly_result.risk_band,
        risk_profile=derived_risk_profile,
        reasoning=anomaly_result.reasoning,
        flags=anomaly_result.flags,
        regulations_violated=anomaly_result.regulations_violated,
        agent_chain=agent_chain,
        preprocessed=last_preprocessed,
        baseline=baseline,
        generated_transactions=raw_transactions,
        timestamp=datetime.now(timezone.utc).isoformat(),
        trace_id=trace_id,
        validator_loops=validator_loops,
    )

    db.complete_agent_trace(trace_id, result=response.model_dump())

    return response


@app.post("/api/compliance/{jurisdiction_code}/push")
async def push_compliance(jurisdiction_code: str, request: CompliancePushRequest):
    jurisdiction_code = jurisdiction_code.upper()
    agent_chain: list[AgentLogEntry] = []
    step_order = 0

    compliance = db.get_compliance_state(jurisdiction_code)
    if not compliance:
        raise HTTPException(status_code=404, detail=f"Unknown jurisdiction: {jurisdiction_code}")

    jurisdiction = compliance["jurisdiction"]

    trace_id = db.create_agent_trace(
        trace_type="compliance_push",
        jurisdiction_code=jurisdiction_code,
    )

    reg_data = db.get_regulation_by_id(request.regulation_update_id)
    if not reg_data:
        db.complete_agent_trace(trace_id, failed=True)
        raise HTTPException(
            status_code=404,
            detail=f"Regulation {request.regulation_update_id} not found",
        )

    regulation = Regulation(
        regulation_update_id=reg_data["regulation_update_id"],
        update_title=reg_data["update_title"],
        summary=reg_data["summary"],
        date_effective=reg_data["date_effective"],
    )
    old_regulations = [Regulation(**r) for r in compliance.get("old_regulations", [])]
    current_rulebook = Rulebook(**compliance["rulebook"])

    current_ver = compliance["current_version"]
    ver_num = int(current_ver.replace("v", "")) + 1
    new_version = f"v{ver_num}"

    # 1. Summarizer
    summary, summarizer_log = await run_summarizer_agent(regulation)
    agent_chain.append(summarizer_log)
    step_order += 1
    db.save_agent_step(
        trace_id=trace_id, step_order=step_order,
        agent=summarizer_log.agent, icon=summarizer_log.icon,
        status=summarizer_log.status, message=summarizer_log.message,
        duration_ms=summarizer_log.duration_ms,
    )

    # 2. Comparison
    comparison_points, comparison_log = await run_comparison_agent(
        old_regulations=old_regulations,
        new_regulation=regulation,
        jurisdiction=jurisdiction,
    )
    agent_chain.append(comparison_log)
    step_order += 1
    db.save_agent_step(
        trace_id=trace_id, step_order=step_order,
        agent=comparison_log.agent, icon=comparison_log.icon,
        status=comparison_log.status, message=comparison_log.message,
        duration_ms=comparison_log.duration_ms,
    )

    # 3. Analyzer
    impact_analysis, analyzer_log = await run_analyzer_agent(
        old_regulations=old_regulations,
        new_regulation=regulation,
        jurisdiction=jurisdiction,
        jurisdiction_code=jurisdiction_code,
    )
    agent_chain.append(analyzer_log)
    step_order += 1
    db.save_agent_step(
        trace_id=trace_id, step_order=step_order,
        agent=analyzer_log.agent, icon=analyzer_log.icon,
        status=analyzer_log.status, message=analyzer_log.message,
        duration_ms=analyzer_log.duration_ms,
    )

    # 4. Rulebook Editor (with integrity guardrails)
    updated_rulebook, rulebook_changes, editor_log = await run_rulebook_editor_agent(
        impact_analysis=impact_analysis,
        current_rulebook=current_rulebook,
        jurisdiction=jurisdiction,
        jurisdiction_code=jurisdiction_code,
        new_version=new_version,
    )
    agent_chain.append(editor_log)
    step_order += 1
    db.save_agent_step(
        trace_id=trace_id, step_order=step_order,
        agent=editor_log.agent, icon=editor_log.icon,
        status=editor_log.status, message=editor_log.message,
        duration_ms=editor_log.duration_ms,
    )

    # HITL: Write to compliance_drafts instead of directly activating
    draft_id = db.create_compliance_draft(
        jurisdiction_code=jurisdiction_code,
        proposed_version=new_version,
        rulebook=updated_rulebook.model_dump(),
        previous_rulebook=current_rulebook.model_dump(),
        changes_description=rulebook_changes,
        summary=summary,
        comparison_points=comparison_points,
        impact_analysis=impact_analysis,
        agent_chain=[log.model_dump() for log in agent_chain],
        regulation_id=request.regulation_update_id,
    )

    db.complete_agent_trace(trace_id, result={"draft_id": draft_id})

    response = CompliancePushResponse(
        jurisdiction_code=jurisdiction_code,
        new_version=new_version,
        summary=summary,
        comparison_points=comparison_points,
        impact_analysis=impact_analysis,
        rulebook_changes=rulebook_changes,
        updated_rulebook=updated_rulebook,
        agent_chain=agent_chain,
        draft_id=draft_id,
        status="pending_review",
    )

    return response


# ── HITL Endpoints ──

@app.get("/api/drafts")
async def list_drafts(jurisdiction_code: str | None = None):
    drafts = db.get_pending_drafts(jurisdiction_code)
    return {"drafts": drafts}


@app.get("/api/drafts/{draft_id}")
async def get_draft(draft_id: str):
    draft = db.get_draft_by_id(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft


@app.post("/api/drafts/{draft_id}/approve")
async def approve_draft_endpoint(draft_id: str, request: DraftApproveRequest = DraftApproveRequest()):
    result = db.approve_draft(draft_id, edited_rulebook=request.edited_rulebook)
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Draft not found or not in pending state",
        )
    return {
        "status": "approved",
        "draft": result,
        "message": "Rulebook has been promoted to active. Monitoring now uses the updated rules.",
    }


@app.post("/api/drafts/{draft_id}/reject")
async def reject_draft_endpoint(draft_id: str):
    result = db.reject_draft(draft_id)
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Draft not found or not in pending state",
        )
    return {
        "status": "rejected",
        "draft": result,
        "message": "Draft rejected. The current rulebook remains unchanged.",
    }


# ── Agent Trace Endpoints ──

@app.get("/api/traces/{trace_id}")
async def get_trace(trace_id: str):
    from utils.supabase_client import get_supabase
    sb = get_supabase()
    trace = sb.table("agent_traces").select("*").eq("id", trace_id).execute()
    if not trace.data:
        raise HTTPException(status_code=404, detail="Trace not found")

    steps = (
        sb.table("agent_steps")
        .select("*")
        .eq("trace_id", trace_id)
        .order("step_order")
        .execute()
    )

    return {
        "trace": trace.data[0],
        "steps": steps.data,
    }


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "features": [
            "supabase_persistence",
            "pydantic_retry_loop",
            "anomaly_validator_agent",
            "rulebook_integrity_guardrails",
            "hitl_draft_review",
            "agent_trace_logging",
        ],
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
