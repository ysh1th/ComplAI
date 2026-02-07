"""FastAPI application — Deriv AI Compliance Manager backend."""

import json
import asyncio
import logging
from pathlib import Path
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
    JurisdictionCompliance,
    AgentLogEntry,
    FullAnalysisResponse,
    CompliancePushResponse,
)
from agents import (
    run_profile_agent,
    run_preprocessor_agent,
    run_baseline_agent,
    run_anomaly_agent,
    run_summarizer_agent,
    run_comparison_agent,
    run_analyzer_agent,
    run_rulebook_editor_agent,
)
from scripts.faker_generator import generate_transactions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data directory
DATA_DIR = Path(__file__).parent / "data"

# FastAPI app
app = FastAPI(
    title="Deriv AI Compliance Manager",
    description="AI-powered compliance monitoring for crypto trading",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory state for current risk scores
user_risk_state: dict[str, dict] = {}
# In-memory state for latest analysis results
user_analysis_state: dict[str, dict] = {}
# In-memory compliance state — loaded from seed files on startup, never written back to disk
compliance_state: dict[str, dict] = {}


# --- Load initial state from seed data (read-only from disk) ---

def _load_initial_risk_state() -> dict[str, dict]:
    """Load pre-computed initial risk scores from historical data."""
    path = DATA_DIR / "initial_risk_state.json"
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _load_initial_compliance_state() -> dict[str, dict]:
    """Load compliance seed data from JSON files into memory.
    This runs once on startup — the original files are never modified."""
    code_to_file = {"MT": "malta.json", "AE": "uae.json", "KY": "cayman.json"}
    state: dict[str, dict] = {}
    for code, filename in code_to_file.items():
        filepath = DATA_DIR / "compliance" / filename
        try:
            with open(filepath, "r") as f:
                state[code] = json.load(f)
        except FileNotFoundError:
            logger.warning(f"Compliance seed file not found: {filepath}")
    return state


# Populate risk state on module load so users don't all start at 0
_initial_risk = _load_initial_risk_state()
for uid, risk in _initial_risk.items():
    user_risk_state[uid] = risk

# Populate compliance state from seed files (deep copy so originals are untouched)
compliance_state = _load_initial_compliance_state()


def load_historical_transactions(user_id: str | None = None) -> dict | list:
    """Load historical transactions. If user_id given, return that user's list."""
    path = DATA_DIR / "historical_transactions.json"
    try:
        with open(path, "r") as f:
            data = json.load(f)
        if user_id:
            return data.get(user_id, [])
        return data
    except FileNotFoundError:
        return [] if user_id else {}


# --- Helper Functions ---

def load_users() -> list[dict]:
    with open(DATA_DIR / "users.json", "r") as f:
        return json.load(f)


def load_baselines() -> list[dict]:
    with open(DATA_DIR / "baselines.json", "r") as f:
        return json.load(f)


def load_compliance(jurisdiction_code: str) -> dict:
    """Return the current in-memory compliance state for a jurisdiction.
    On first startup this is the seed data from JSON files.
    After a push, this reflects the in-memory updated state."""
    code = jurisdiction_code.upper()
    if code not in compliance_state:
        raise HTTPException(status_code=404, detail=f"Unknown jurisdiction: {jurisdiction_code}")
    return compliance_state[code]


def load_new_regulations(jurisdiction_code: str) -> list[dict]:
    code_to_file = {"MT": "malta_v2.json", "AE": "uae_v2.json", "KY": "cayman_v2.json"}
    filename = code_to_file.get(jurisdiction_code.upper())
    if not filename:
        return []
    filepath = DATA_DIR / "compliance" / "new_regulations" / filename
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


# --- Request/Response Models ---

class IngestBatchRequest(BaseModel):
    user_id: str
    num_transactions: int = 5
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    variance: Optional[float] = None
    countries: Optional[list[str]] = None  # Multi-select countries for random assignment
    overrides: Optional[dict] = None


class CompliancePushRequest(BaseModel):
    regulation_update_id: str


# --- API Endpoints ---

@app.get("/api/init")
async def get_init():
    """Returns all users with profiles, baselines, historical data, and current risk state."""
    users = load_users()
    baselines = load_baselines()
    baseline_map = {b["user_id"]: b for b in baselines}
    all_history = load_historical_transactions()

    result = []
    for u in users:
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

        risk_state = user_risk_state.get(user_id, {})
        history = all_history.get(user_id, []) if isinstance(all_history, dict) else []

        # Merge dynamic risk_profile into profile if available
        profile_data = {**u}
        if "risk_profile" in risk_state:
            profile_data["risk_profile"] = risk_state["risk_profile"]

        result.append({
            "profile": profile_data,
            "baseline": baseline,
            "current_risk_score": risk_state.get("risk_score", 0),
            "current_risk_band": risk_state.get("risk_band", "CLEAN"),
            "latest_analysis": user_analysis_state.get(user_id),
            "historical_transactions": history,
        })

    return {"users": result}


@app.get("/api/compliance/{jurisdiction_code}")
async def get_compliance_endpoint(jurisdiction_code: str):
    """Returns current compliance state for a jurisdiction (reads from in-memory state)."""
    compliance = load_compliance(jurisdiction_code.upper())
    new_regs = load_new_regulations(jurisdiction_code.upper())

    # Filter out already-pushed regulations
    pushed_ids = {r["regulation_update_id"] for r in compliance.get("new_regulations", [])}
    available = [r for r in new_regs if r["regulation_update_id"] not in pushed_ids]

    return {
        **compliance,
        "available_new_regulations": available,
    }


@app.get("/api/rules/{jurisdiction_code}")
async def get_rules_endpoint(jurisdiction_code: str):
    """Returns the current rulebook for a jurisdiction (reads from in-memory state)."""
    compliance = load_compliance(jurisdiction_code.upper())
    return {
        "jurisdiction": compliance["jurisdiction"],
        "current_version": compliance["current_version"],
        "rulebook": compliance["rulebook"],
    }


@app.post("/api/ingest-batch")
async def ingest_batch(request: IngestBatchRequest):
    """
    Injects a transaction batch through the full analysis workflow.
    Workflow: Profile → (Preprocessor || Baseline) → Anomaly Detector
    """
    agent_chain: list[AgentLogEntry] = []

    # 1. Profile Agent (local)
    try:
        profile, profile_log = run_profile_agent(request.user_id)
        agent_chain.append(profile_log)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User not found: {request.user_id}")

    # Determine jurisdiction
    jurisdiction_map = {"MT": "Malta", "AE": "UAE", "KY": "Cayman Islands"}
    jurisdiction = jurisdiction_map.get(profile.country, profile.country)

    # Generate transactions via Faker (single day)
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

    # 2 & 3. Run Preprocessor and Baseline agents in parallel
    preprocessor_task = asyncio.to_thread(
        run_preprocessor_agent, raw_transactions, profile
    )
    baseline_task = run_baseline_agent(request.user_id, raw_transactions, profile)

    (preprocessed, preprocessor_log), (baseline, baseline_log) = await asyncio.gather(
        preprocessor_task, baseline_task
    )
    agent_chain.append(preprocessor_log)
    agent_chain.append(baseline_log)

    # 4. Load current rulebook for jurisdiction
    compliance = load_compliance(profile.country)
    rulebook = Rulebook(**compliance["rulebook"])

    # Run Anomaly Detector Agent
    anomaly_result, anomaly_log = await run_anomaly_agent(
        preprocessed=preprocessed,
        baseline=baseline,
        profile=profile,
        rulebook=rulebook,
        jurisdiction_version=compliance["current_version"],
    )
    agent_chain.append(anomaly_log)

    # Derive risk_profile from the new score
    if anomaly_result.risk_score >= 50:
        derived_risk_profile = "high"
    elif anomaly_result.risk_score >= 25:
        derived_risk_profile = "medium"
    else:
        derived_risk_profile = "low"

    # Update in-memory risk state (includes derived profile)
    user_risk_state[request.user_id] = {
        "risk_score": anomaly_result.risk_score,
        "risk_band": anomaly_result.risk_band,
        "risk_profile": derived_risk_profile,
    }

    # Build response using the last preprocessed transaction for summary
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
    )

    # Store latest analysis
    user_analysis_state[request.user_id] = response.model_dump()

    return response


@app.post("/api/compliance/{jurisdiction_code}/push")
async def push_compliance(jurisdiction_code: str, request: CompliancePushRequest):
    """
    Pushes a new regulation through the compliance agentic workflow.
    Workflow: Summarizer → Comparison → Analyzer → Rulebook Editor
    """
    jurisdiction_code = jurisdiction_code.upper()
    agent_chain: list[AgentLogEntry] = []

    # Load compliance data
    compliance = load_compliance(jurisdiction_code)
    jurisdiction = compliance["jurisdiction"]

    # Find the regulation to push
    new_regs = load_new_regulations(jurisdiction_code)
    regulation_data = None
    for r in new_regs:
        if r["regulation_update_id"] == request.regulation_update_id:
            regulation_data = r
            break

    if not regulation_data:
        raise HTTPException(
            status_code=404,
            detail=f"Regulation {request.regulation_update_id} not found",
        )

    regulation = Regulation(**regulation_data)
    old_regulations = [Regulation(**r) for r in compliance["old_regulations"]]
    current_rulebook = Rulebook(**compliance["rulebook"])

    # Calculate new version
    current_ver = compliance["current_version"]
    ver_num = int(current_ver.replace("v", "")) + 1
    new_version = f"v{ver_num}"

    # 1. Summarizer Agent
    summary, summarizer_log = await run_summarizer_agent(regulation)
    agent_chain.append(summarizer_log)

    # 2. Comparison Agent
    comparison_points, comparison_log = await run_comparison_agent(
        old_regulations=old_regulations,
        new_regulation=regulation,
        jurisdiction=jurisdiction,
    )
    agent_chain.append(comparison_log)

    # 3. Analyzer Agent
    impact_analysis, analyzer_log = await run_analyzer_agent(
        old_regulations=old_regulations,
        new_regulation=regulation,
        jurisdiction=jurisdiction,
        jurisdiction_code=jurisdiction_code,
    )
    agent_chain.append(analyzer_log)

    # 4. Rulebook Editor Agent
    updated_rulebook, rulebook_changes, editor_log = await run_rulebook_editor_agent(
        impact_analysis=impact_analysis,
        current_rulebook=current_rulebook,
        jurisdiction=jurisdiction,
        jurisdiction_code=jurisdiction_code,
        new_version=new_version,
    )
    agent_chain.append(editor_log)

    # Update in-memory compliance state (no disk writes — resets on restart)
    compliance_state[jurisdiction_code]["new_regulations"].append(regulation_data)
    compliance_state[jurisdiction_code]["current_version"] = new_version
    compliance_state[jurisdiction_code]["rulebook"] = updated_rulebook.model_dump()

    response = CompliancePushResponse(
        jurisdiction_code=jurisdiction_code,
        new_version=new_version,
        summary=summary,
        comparison_points=comparison_points,
        impact_analysis=impact_analysis,
        rulebook_changes=rulebook_changes,
        updated_rulebook=updated_rulebook,
        agent_chain=agent_chain,
    )

    return response


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
