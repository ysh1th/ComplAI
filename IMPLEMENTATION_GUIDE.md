# Deriv AI Compliance Manager — Implementation Guide (Final)

> The complete technical implementation reference. Covers architecture, tech stack, frontend, backend, data models, agentic workflows, API contracts, and file structure.
> Last updated: February 7, 2026

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack & Dependencies](#2-tech-stack--dependencies)
3. [Project File Structure](#3-project-file-structure)
4. [Design System](#4-design-system)
5. [Data Models (Pydantic Schemas)](#5-data-models-pydantic-schemas)
6. [Agentic Workflow Architecture](#6-agentic-workflow-architecture)
7. [API Contract (FastAPI Endpoints)](#7-api-contract-fastapi-endpoints)
8. [Frontend — Screen 1: Live Monitor](#8-frontend--screen-1-live-monitor)
9. [Frontend — Screen 2: Regulatory Hub](#9-frontend--screen-2-regulatory-hub)
10. [Frontend — Shared Components](#10-frontend--shared-components)
11. [Faker Data Generation Script](#11-faker-data-generation-script)
12. [Static Data Files (JSON)](#12-static-data-files-json)
13. [LLM Integration](#13-llm-integration)
14. [Environment Configuration](#14-environment-configuration)
15. [Demo Script](#15-demo-script)

---

## 1. Project Overview

### What
An AI-powered compliance monitoring dashboard for Deriv that combines behavioral anomaly detection with regulatory intelligence across three jurisdictions.

### Who
Built for Compliance Officers who need machine-scale monitoring with human-readable explanations.

### Scope
- **Domain:** Crypto trading compliance (KYC, cross-border payments, AML/CFT, tax reporting)
- **Jurisdictions:** Malta (MT), UAE (AE), Cayman Islands (KY)
- **Users:** 10 demo users, all aged 25, spread across jurisdictions (~3-4 per country)
- **Type:** Hackathon MVP — live demo, no slides

### Core Concept: The Dual Brain
1. **Behavioral Brain** — detects anomalies using LLM-powered reasoning against preprocessed transaction data and user baselines
2. **Regulatory Brain** — uses LLM agents to analyze new compliance, compare against old, assess impact, and autonomously edit the rulebook

### The Two User Controls (World Simulator)
The user acts as a **simulator for the world**. They control the environment in two ways:
1. **Changing user trading behavior** — via the Data Injection Flow (Faker script generates transactions based on user-set parameters)
2. **Pushing new compliance** — via the Regulatory Hub (select a regulation, push it into the compliance agentic workflow)

---

## 2. Tech Stack & Dependencies

### Frontend

| Tool | Version | Purpose |
|------|---------|---------|
| **Next.js** | 14 | React framework, App Router |
| **TypeScript** | 5.x | Type safety |
| **Tailwind CSS** | 3.x | Utility-first styling |
| **shadcn/ui** | latest | Pre-built accessible components |
| **Framer Motion** | latest | Animations (risk gauge, card transitions, flashing) |
| **Lucide React** | latest | Icon library |
| **next-themes** | latest | Dark/light mode toggle |
| **recharts** or **chart.js** | latest | Baseline vs current comparison charts |

### Backend

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.11+ | Runtime |
| **FastAPI** | 0.100+ | API framework |
| **Pydantic** | 2.x | Data validation, schema enforcement |
| **Uvicorn** | latest | ASGI server |
| **Faker** | latest | Synthetic transaction data generation |
| **python-dotenv** | latest | Environment variable loading |
| **openai** (or equivalent) | latest | LLM API client |
| **httpx** | latest | Async HTTP client for LLM calls |

### No Database
All data is served from **static JSON files** via the FastAPI backend. No PostgreSQL, no SQLite, no Redis. JSON files are the source of truth for the MVP. The rulebook JSON is **mutable** — the Rulebook Editor Agent modifies it at runtime.

---

## 3. Project File Structure

```
Deriv_Hackathon/
├── PROJECT_BLUEPRINT.md              # Vision & concept document
├── IMPLEMENTATION_GUIDE.md           # This file — technical implementation reference
│
├── backend/
│   ├── main.py                       # FastAPI app — route definitions, CORS, startup
│   ├── .env                          # LLM_API_KEY, LLM_MODEL
│   ├── requirements.txt              # Python dependencies
│   │
│   ├── models/                       # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py                   # UserProfile, UserBaseline
│   │   ├── transaction.py            # RawTransaction, PreprocessedTransaction
│   │   ├── compliance.py             # Regulation, Rulebook, RuleEntry
│   │   ├── risk.py                   # AnomalyResult, RiskBand enum
│   │   └── agent_log.py              # AgentLogEntry, AgentChain, FullAnalysisResponse
│   │
│   ├── agents/                       # Agentic workflows
│   │   ├── __init__.py
│   │   │
│   │   │── # ── Transaction Analysis Workflow ──
│   │   ├── profile_agent.py          # Loads user profile from JSON
│   │   ├── preprocessor_agent.py     # Local/deterministic enrichment of raw transactions
│   │   ├── baseline_agent.py         # LLM agent — computes/updates user baselines
│   │   ├── anomaly_agent.py          # LLM agent — reasons about anomalies using all data
│   │   │
│   │   │── # ── Compliance Update Workflow ──
│   │   ├── summarizer_agent.py       # LLM agent — summarizes new regulatory act
│   │   ├── comparison_agent.py       # LLM agent — compares old vs new regulations
│   │   ├── analyzer_agent.py         # LLM agent — analyzes impact on users & company
│   │   └── rulebook_editor_agent.py  # LLM agent — modifies the rulebook based on analysis
│   │
│   ├── scripts/
│   │   └── faker_generator.py        # Faker-based transaction data generator
│   │
│   ├── data/                         # Static + mutable JSON data files
│   │   ├── users.json                # 10 user profiles (bio + KYC)
│   │   ├── baselines.json            # 10 user baselines (updated by Baseline Agent)
│   │   └── compliance/
│   │       ├── malta.json            # Compliance data for Malta (old regs + rulebook)
│   │       ├── uae.json              # Compliance data for UAE
│   │       ├── cayman.json           # Compliance data for Cayman Islands
│   │       └── new_regulations/      # New regulations to be pushed (v2, v3, etc.)
│   │           ├── malta_v2.json
│   │           ├── uae_v2.json
│   │           └── cayman_v2.json
│   │
│   └── utils/
│       ├── __init__.py
│       ├── geo.py                    # Distance/speed calculation helpers
│       └── llm.py                    # LLM client wrapper (loads .env, calls API)
│
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.js
│   │
│   ├── app/
│   │   ├── layout.tsx                # Root layout — sidebar, theme provider
│   │   ├── page.tsx                  # Redirect to /monitor
│   │   ├── globals.css               # Tailwind imports, custom CSS variables, fonts
│   │   │
│   │   ├── monitor/
│   │   │   └── page.tsx              # Screen 1: Live Monitor
│   │   │
│   │   └── regulatory/
│   │       └── page.tsx              # Screen 2: Regulatory Hub
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx           # Sidebar navigation (logo, links, theme toggle)
│   │   │   └── ThemeToggle.tsx       # Dark/light mode switch
│   │   │
│   │   ├── monitor/                  # Screen 1 components
│   │   │   ├── UserRoster.tsx        # Left panel — scrollable user card list
│   │   │   ├── UserCard.tsx          # Individual user card (avatar, name, flag, badge)
│   │   │   ├── IntelligenceDetail.tsx # Right panel — full user detail view
│   │   │   ├── RiskGauge.tsx         # Animated semi-circular gauge (0–100)
│   │   │   ├── IdentityCard.tsx      # Bio/KYC data display
│   │   │   ├── BehavioralAnalysis.tsx # Statistical brain + physics brain section
│   │   │   ├── StatisticalBrain.tsx  # Baseline vs current comparisons
│   │   │   ├── PhysicsBrain.tsx      # Distance, time, impossible travel detection
│   │   │   ├── AIGuardian.tsx        # Terminal-style anomaly log + agent chain
│   │   │   ├── AgentChainLog.tsx     # Step-by-step agent workflow visualization
│   │   │   └── DataInjectionFlow.tsx # Bottom drawer — Faker params + trigger
│   │   │
│   │   ├── regulatory/              # Screen 2 components
│   │   │   ├── WorldMapBackground.tsx # Translucent B&W map with country highlight
│   │   │   ├── JurisdictionTabs.tsx  # Malta | UAE | Cayman tab switcher
│   │   │   ├── ComplianceSummary.tsx # Current compliance overview
│   │   │   ├── ActiveRulebook.tsx    # Categorized rules with point values
│   │   │   ├── VersionLabel.tsx      # Simple version label (v1, v2, v3)
│   │   │   ├── RegulationCard.tsx    # Individual regulation display card
│   │   │   ├── PushCompliance.tsx    # Select new regulation + push button
│   │   │   ├── ComplianceAgentOutput.tsx # Shows output from 4 compliance agents
│   │   │   └── RulebookDiff.tsx      # Shows before/after rulebook changes
│   │   │
│   │   └── shared/                  # Reusable components
│   │       ├── RiskBadge.tsx         # Color-coded pill (HIGH/MEDIUM/LOW/CLEAN)
│   │       ├── CountryFlag.tsx       # Flag emoji/icon for MT/AE/KY
│   │       └── LoadingSpinner.tsx    # Loading state
│   │
│   ├── lib/
│   │   ├── api.ts                    # API client — all fetch calls to backend
│   │   ├── types.ts                  # TypeScript interfaces matching Pydantic models
│   │   └── utils.ts                  # Helper functions (formatting, colors, etc.)
│   │
│   └── hooks/
│       ├── useUsers.ts               # Fetch + manage user list state
│       ├── useCompliance.ts          # Fetch + manage compliance data state
│       └── useInjectBatch.ts         # Handle data injection flow
```

---

## 4. Design System

### Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--deriv-red` | `#FF444F` | HIGH risk, alerts, active nav, regulation highlights, primary CTA |
| `--deriv-black` | `#0E0E0E` | Dark mode background |
| `--deriv-dark-card` | `#1A1A1A` | Dark mode card/panel backgrounds |
| `--deriv-dark-border` | `#2A2A2A` | Dark mode borders |
| `--deriv-teal` | `#00A79E` | LOW risk, safe states, success, CLEAN badge |
| `--deriv-amber` | `#F5A623` | MEDIUM risk, warnings |
| `--deriv-grey` | `#6B7280` | CLEAN/neutral, muted text |
| `--light-bg` | `#F5F5F5` | Light mode background |
| `--light-card` | `#FFFFFF` | Light mode card backgrounds |
| `--light-border` | `#E0E0E0` | Light mode borders |

### Risk Band Colors

| Band | Color | Hex | Score Range |
|------|-------|-----|-------------|
| HIGH | Red | `#FF444F` | ≥75 |
| MEDIUM | Amber | `#F5A623` | 50–74 |
| LOW | Green/Teal | `#00A79E` | 25–49 |
| CLEAN | Grey | `#6B7280` | <25 |

### Typography

| Element | Font | Weight | Size |
|---------|------|--------|------|
| Headings | Inter | 700 (Bold) | 24–32px |
| Subheadings | Inter | 600 (SemiBold) | 16–20px |
| Body | Inter | 400 (Regular) | 14px |
| Monospace (AI Guardian) | JetBrains Mono / Fira Code | 400 | 13px |
| Risk Score Number | Inter | 800 (ExtraBold) | 48px |

### Theme Modes

- **Dark mode** (default): `--deriv-black` background, `--deriv-dark-card` panels
- **Light mode**: `--light-bg` background, `--light-card` panels
- Toggle in sidebar footer using `next-themes`

### Spacing & Layout

- Sidebar width: 64px collapsed, 240px expanded
- Main content: fills remaining width
- Cards: 12px border radius, subtle shadow
- Grid gaps: 16–24px

---

## 5. Data Models (Pydantic Schemas)

### A. User Profile

```python
class UserProfile(BaseModel):
    user_id: str                          # "MT-USER-001"
    age: int                              # 25
    country: str                          # "MT" (ISO code)
    full_name: str                        # "John Doe"
    income_level: Literal["low", "medium", "high"]
    occupation: str                       # "Freelancer"
    kyc_status: Literal["verified", "pending"]
    risk_profile: Literal["low", "medium", "high"]
    historical_countries: list[str]       # ["MT", "IT"]
```

### B. User Baseline (computed by Baseline Agent LLM)

```python
class UserBaseline(BaseModel):
    user_id: str
    avg_tx_amount_usd: float              # 150.75
    avg_daily_total_usd: float            # 450.00
    avg_tx_per_day: int                   # 3
    std_dev_amount: float                 # 50.25
    normal_hour_range: list[int]          # [9, 18]
    excluded_anomalies_count: int = 0
```

### C. Raw Transaction (generated by Faker script)

```python
class RawTransaction(BaseModel):
    user_id: str
    timestamp: str                        # ISO 8601
    transaction_amount_usd: float
    transaction_currency: str             # "ETH", "BTC", "USDT"
    transaction_type: str                 # "withdrawal", "deposit", "transfer"
    transaction_country: str              # ISO code
    transaction_city: str
```

### D. Preprocessed Transaction (computed locally by Preprocessor Agent)

```python
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
    hour_of_day: int
    time_since_last_sec: int
    previous_country: str
    previous_timestamp: str
    distance_km: float
    actual_travel_hours: float
    daily_total_usd: float
    tx_count_per_day: int
    is_new_country: bool
```

### E. Regulation

```python
class Regulation(BaseModel):
    regulation_update_id: str             # "MT-REG-001"
    update_title: str
    summary: str
    date_effective: str
```

### F. Rule Entry

```python
class RuleEntry(BaseModel):
    category: str                         # "Amount", "Geo", "Frequency", "Profile"
    rule: str                             # Human-readable rule description
    points: int                           # Points awarded if triggered
```

### G. Rulebook (mutable — edited by Rulebook Editor Agent)

```python
class Rulebook(BaseModel):
    amount_based: list[str]
    frequency_based: list[str]
    location_based: list[str]
    behavioural_pattern: list[str]
    risk_score: dict                      # { "range": "0-100", "rules": [...], "capping": ... }
    risk_bands: dict                      # { "HIGH": "...", "MEDIUM": "...", ... }
```

### H. Jurisdiction Compliance

```python
class JurisdictionCompliance(BaseModel):
    jurisdiction: str                     # "Malta", "UAE", "Cayman Islands"
    jurisdiction_code: str                # "MT", "AE", "KY"
    current_version: str                  # "v1", "v2" — simple label, increments on push
    old_regulations: list[Regulation]     # The original/foundational regulations
    new_regulations: list[Regulation]     # Regulations pushed via compliance workflow
    rulebook: Rulebook                    # The current rulebook (mutated by Rulebook Editor Agent)
```

### I. Anomaly Result (output of Anomaly Detector LLM Agent)

```python
class AnomalyResult(BaseModel):
    is_anomaly: bool
    risk_score: int                       # 0–100 (LLM-assigned)
    risk_band: Literal["HIGH", "MEDIUM", "LOW", "CLEAN"]
    flags: list[str]                      # Specific flags the LLM identified
    reasoning: str                        # LLM's chain-of-thought reasoning
    regulations_violated: list[str]       # Specific Acts cited
```

### J. Agent Log Entry

```python
class AgentLogEntry(BaseModel):
    agent: str                            # "Profile Agent"
    icon: str                             # "🔍"
    status: Literal["success", "alert", "high", "complete", "error"]
    message: str                          # What this agent found
    duration_ms: int                      # Processing time in milliseconds
```

### K. Full Analysis Response (returned from POST /api/ingest-batch)

```python
class FullAnalysisResponse(BaseModel):
    user_id: str
    user_name: str
    jurisdiction: str
    risk_score: int                       # 0–100 (from Anomaly Agent LLM)
    risk_band: Literal["HIGH", "MEDIUM", "LOW", "CLEAN"]
    reasoning: str                        # LLM's full reasoning (displayed in AI Guardian)
    flags: list[str]                      # List of triggered flags
    regulations_violated: list[str]       # Specific Acts cited
    agent_chain: list[AgentLogEntry]      # Full agent workflow log for frontend display
    preprocessed: PreprocessedTransaction # Enriched data for frontend charts
    baseline: UserBaseline                # Baseline used (from Baseline Agent LLM)
    timestamp: str
```

### L. Compliance Push Response (returned from POST /api/compliance/push)

```python
class CompliancePushResponse(BaseModel):
    jurisdiction_code: str
    new_version: str                      # "v2"
    summary: str                          # From Summarizer Agent
    comparison_points: list[str]          # From Comparison Agent
    impact_analysis: str                  # From Analyzer Agent
    rulebook_changes: str                 # Description of what Rulebook Editor changed
    updated_rulebook: Rulebook            # The new rulebook after edits
    agent_chain: list[AgentLogEntry]      # Full compliance workflow log
```

---

## 6. Agentic Workflow Architecture

### Philosophy

There are **two distinct agentic workflows**. Each workflow is a sequence of named agents called from a FastAPI endpoint. There is **no orchestrator** — the endpoint calls agents in order.

Each agent is a Pydantic-validated function that:
1. Takes typed input
2. Does its work (local computation OR LLM call)
3. Returns typed output + an `AgentLogEntry` for the chain

The agent chain is returned to the frontend. The frontend renders it so the judges can see every agent's contribution.

---

### WORKFLOW 1: Transaction Analysis (Behavioral Monitoring)

Triggered when the user injects transaction data via the Data Injection Flow.

#### Agent 1: Profile Agent (`profile_agent.py`) — Local

**Input:** `user_id: str`
**Output:** `UserProfile`, `AgentLogEntry`
**Logic:**
- Loads user profile from `data/users.json`
- Determines jurisdiction from user's country code
- Returns profile data for downstream agents

**Log example:** `"Loaded AE-USER-001 (Jane Smith, UAE, high income, verified KYC)"`

#### Agent 2: Preprocessor Agent (`preprocessor_agent.py`) — Local

**Input:** `list[RawTransaction]`, `UserProfile`
**Output:** `list[PreprocessedTransaction]`, `AgentLogEntry`
**Logic (all deterministic, no LLM):**
- Calculates `distance_km` between `previous_country` and `transaction_country` using geo lookup
- Calculates `time_since_last_sec` from timestamps
- Computes `daily_total_usd` (sum of the day's transactions)
- Counts `tx_count_per_day`
- Checks `is_new_country` against `historical_countries`
- Extracts `hour_of_day`

**Log example:** `"Preprocessed 5 transactions | Distance: 5,000km | Time delta: 3,600s | Daily total: $55,250 | New country: YES"`

**Runs in parallel with Agent 3.**

#### Agent 3: Baseline Calculator Agent (`baseline_agent.py`) — LLM

**Input:** `user_id`, `list[RawTransaction]` (current batch + historical), `UserProfile`
**Output:** `UserBaseline`, `AgentLogEntry`
**Logic:**
- Sends the user's transaction history + current batch to the LLM
- LLM computes/updates: avg transaction amount, avg daily total, avg transactions per day, standard deviation, normal hour range
- LLM also decides `excluded_anomalies_count` (how many past transactions it considers outliers)
- Updated baseline is written back to `data/baselines.json`

**LLM Prompt:**
```
You are a financial data analyst. Given the following transaction history
for a user, compute their behavioral baseline.

User: {user_id} ({full_name}), {country}, {income_level} income
Transaction history (last 30 days):
{list of transactions with amounts, timestamps, countries}

Current batch (today):
{today's transactions}

Compute and return as JSON:
- avg_tx_amount_usd: average transaction amount
- avg_daily_total_usd: average total spent per day
- avg_tx_per_day: average number of transactions per day
- std_dev_amount: standard deviation of transaction amounts
- normal_hour_range: [earliest_typical_hour, latest_typical_hour]
- excluded_anomalies_count: how many transactions you'd exclude as outliers

Return ONLY valid JSON, no explanation.
```

**Log example:** `"Baseline computed via LLM — avg $200/tx, $600/day, 4 tx/day, σ=$75"`

**Runs in parallel with Agent 2.**

#### Agent 4: Anomaly Detector Agent (`anomaly_agent.py`) — LLM

**Input:** `list[PreprocessedTransaction]`, `UserBaseline`, `UserProfile`, `Rulebook` (current jurisdiction's rulebook)
**Output:** `AnomalyResult`, `AgentLogEntry`
**Logic:**
- Sends ALL context to the LLM: preprocessed transactions, baseline, user profile, and the full rulebook for that jurisdiction
- The LLM **reasons** about whether there are anomalies
- The LLM assigns a risk score (0–100), a risk band, identifies specific flags, cites specific regulations, and writes its reasoning chain
- This replaces the old deterministic point system — the LLM does the thinking

**LLM Prompt:**
```
You are a senior compliance analyst at a crypto trading platform.
You are evaluating a user's transactions for anomalies.

## User Profile
- ID: {user_id}
- Name: {full_name}
- Country: {country} ({jurisdiction})
- Income: {income_level}, Occupation: {occupation}
- KYC: {kyc_status}, Risk Profile: {risk_profile}
- Historical countries: {historical_countries}

## User Baseline
- Avg tx amount: ${avg_tx_amount_usd}
- Avg daily total: ${avg_daily_total_usd}
- Avg tx per day: {avg_tx_per_day}
- Std deviation: ${std_dev_amount}
- Normal hours: {normal_hour_range}

## Today's Preprocessed Transactions
{for each transaction:}
- Amount: ${amount} {currency} ({type})
- From: {city}, {country}
- Time: {timestamp} (hour: {hour_of_day})
- Distance from previous: {distance_km}km in {time_since_last_sec}s
  (speed: {calculated_speed} km/h)
- Daily total so far: ${daily_total_usd}
- Transaction count today: {tx_count_per_day}
- New country: {is_new_country}

## Jurisdiction Rulebook ({jurisdiction} — version {version})
### Amount-based rules:
{amount_based rules}
### Frequency-based rules:
{frequency_based rules}
### Location-based rules:
{location_based rules}
### Behavioural pattern rules:
{behavioural_pattern rules}
### Risk scoring:
{risk_score rules with point values}
### Risk bands:
{risk_bands definitions}

## Your Task
Analyze the transactions against the user's baseline and the jurisdiction
rulebook. For each anomaly found:
1. Identify the specific rule violated
2. Cite the specific regulation/Act
3. Assign points based on the rulebook's scoring table

Then compute the total risk score (capped at 100) and assign a risk band.

Return as JSON:
{
  "is_anomaly": true/false,
  "risk_score": 0-100,
  "risk_band": "HIGH"/"MEDIUM"/"LOW"/"CLEAN",
  "flags": ["list of specific flags with points"],
  "regulations_violated": ["specific Act names"],
  "reasoning": "2-4 sentence explanation of your analysis, citing
                specific regulations. Be direct and professional."
}
```

**Log example:** `"Anomaly detected — Risk: 100/100 HIGH | Physics violation + Amount spike + VARA breach | 3 regulations violated"`

### Transaction Analysis Flow Diagram

```
Frontend: User sets params → clicks "Inject Transaction Batch"
│
├─ Backend: Faker script generates transactions
│
├─ 1. Profile Agent (local)
│     └─ loads user profile
│
├─ PARALLEL:
│   ├─ 2. Preprocessor Agent (local)
│   │     └─ enriches transactions (distance, time, totals)
│   │
│   └─ 3. Baseline Calculator Agent (LLM)
│         └─ computes/updates user baseline from history
│
├─ 4. Anomaly Detector Agent (LLM)
│     └─ reasons about anomalies using preprocessed + baseline + rulebook
│     └─ assigns risk score, flags, cites regulations
│
└─ Return: FullAnalysisResponse (score + reasoning + flags + full agent chain)
```

---

### WORKFLOW 2: Compliance Update (Regulatory Intelligence)

Triggered when the user pushes a new regulatory act on the Regulatory Hub.

#### Agent 5: Summarizer Agent (`summarizer_agent.py`) — LLM

**Input:** New regulation (Regulation object)
**Output:** `summary: str`, `AgentLogEntry`
**Logic:**
- Takes the new regulatory act
- LLM generates a clear, concise summary of what it means in plain language

**LLM Prompt:**
```
You are a regulatory expert. Summarize the following new regulatory act
in 3-4 clear sentences. Focus on: what it requires, who it affects,
key thresholds, and penalties for non-compliance.

Regulation:
- ID: {regulation_update_id}
- Title: {update_title}
- Summary: {summary}
- Effective date: {date_effective}

Write a plain-language summary suitable for a compliance officer.
```

**Log example:** `"Summarized MT-REG-001: VFA Licensing Enhancements — annual renewal, cybersecurity audits, €200k fines"`

#### Agent 6: Comparison Agent (`comparison_agent.py`) — LLM

**Input:** Old regulations (list), new regulation
**Output:** `comparison_points: list[str]`, `AgentLogEntry`
**Logic:**
- Takes the old regulatory framework + the new regulation
- LLM generates specific comparison points (what changed, what's new, what's stricter)

**LLM Prompt:**
```
You are a regulatory analyst. Compare the following old and new
regulatory frameworks and generate specific comparison points.

Old regulations for {jurisdiction}:
{for each old regulation: id, title, summary, date}

New regulation being introduced:
- ID: {regulation_update_id}
- Title: {update_title}
- Summary: {summary}
- Effective date: {date_effective}

Generate 4-6 specific comparison points. For each point, state:
- What aspect changed (thresholds, reporting, licensing, etc.)
- The old requirement vs the new requirement
- Whether it's stricter, relaxed, or entirely new

Return as a JSON array of strings.
```

**Log example:** `"Generated 5 comparison points — 3 stricter requirements, 1 new obligation, 1 modified threshold"`

#### Agent 7: Analyzer Agent (`analyzer_agent.py`) — LLM

**Input:** Old regulations, new regulation, user baselines for that jurisdiction
**Output:** `impact_analysis: str`, `AgentLogEntry`
**Logic:**
- Takes old regs, new reg, AND the baseline averages for users in that jurisdiction
- LLM analyzes how the new regulation would affect customers and the company
- Includes **numbers** — e.g., "3 out of 4 UAE users currently have daily totals above the new reporting threshold"

**LLM Prompt:**
```
You are a compliance impact analyst. Analyze how a new regulation
affects customers and the company.

Jurisdiction: {jurisdiction}

Old regulations:
{old regulation summaries}

New regulation:
- {update_title}: {summary}
- Effective: {date_effective}

User baselines in this jurisdiction (current behavior):
{for each user in this jurisdiction:}
- {user_id} ({full_name}): avg tx ${avg_tx_amount_usd}, avg daily ${avg_daily_total_usd},
  {avg_tx_per_day} tx/day, income: {income_level}

Analyze:
1. How many users would be affected by the new regulation? Be specific.
2. What behavioral changes might users make to evade the new rules?
3. What is the estimated cost/operational impact on the company?
4. What are the specific risks if the company doesn't adapt its monitoring?

Include numbers and percentages. Be specific and actionable.
Return as a structured analysis paragraph (4-6 sentences).
```

**Log example:** `"Impact analysis complete — 3/4 UAE users affected, estimated 15% increase in flagged transactions, $200k compliance cost increase"`

#### Agent 8: Rulebook Editor Agent (`rulebook_editor_agent.py`) — LLM

**Input:** Analyzer Agent output, current rulebook for that jurisdiction
**Output:** Updated `Rulebook`, `rulebook_changes: str`, `AgentLogEntry`
**Logic:**
- Takes the analysis from Agent 7 + the current rulebook
- LLM **reasons about what changes are needed** in the rulebook
- LLM outputs the modified rulebook JSON
- The modified rulebook is **written back** to `data/compliance/{jurisdiction}.json`
- This is the key: the rulebook used by the Anomaly Detector Agent in Workflow 1 is now updated

**LLM Prompt:**
```
You are a compliance rulebook engineer. Based on the following impact
analysis and the current rulebook, make necessary changes to the
monitoring rulebook.

Impact Analysis:
{analyzer_agent_output}

Current Rulebook for {jurisdiction}:
{full current rulebook JSON}

Your task:
1. Review each category (amount_based, frequency_based, location_based,
   behavioural_pattern) and determine if rules need updating
2. Review the risk_score rules and determine if point values or conditions
   need adjusting
3. Add new rules if the new regulation introduces requirements not currently
   covered
4. Adjust risk_bands descriptions if thresholds have changed

Return the COMPLETE updated rulebook as valid JSON with the same structure.
Also provide a brief description of what you changed and why.

Return format:
{
  "updated_rulebook": { ...full rulebook JSON... },
  "changes_description": "Brief description of changes made"
}
```

**Log example:** `"Rulebook updated — added VARA stablecoin rule, adjusted AML threshold from €1500 to €1000, new geo-fencing rule for non-UAE IPs"`

### Compliance Update Flow Diagram

```
Frontend: User selects regulation → clicks "Push Compliance"
│
├─ 1. Summarizer Agent (LLM)
│     └─ summarizes the new regulation
│
├─ 2. Comparison Agent (LLM)
│     └─ compares old vs new regulations
│
├─ 3. Analyzer Agent (LLM)
│     └─ analyzes impact on users & company (with numbers)
│
├─ 4. Rulebook Editor Agent (LLM)
│     └─ modifies the rulebook based on analysis
│     └─ writes updated rulebook back to JSON
│
└─ Return: CompliancePushResponse
      (summary + comparison + impact + rulebook changes + full agent chain)
```

**After this workflow completes:** The next time a transaction batch is injected (Workflow 1), the Anomaly Detector Agent will use the **updated rulebook**. The regulations are now live.

---

### Version Labeling (Simplified)

Versions are **simple labels** — just a string that increments when a new compliance is pushed:
- Start: `v1` (old regulations + original rulebook)
- After first push: `v2` (old + new regulations, modified rulebook)
- After second push: `v3` (accumulated)

The version label is displayed on the frontend for reference. No complex state machine, no rollback, no draft/apply system. When you push, it's live.

---

## 7. API Contract (FastAPI Endpoints)

### GET `/api/init`

Returns all users with their profiles and current baselines.

**Response:**
```json
{
  "users": [
    {
      "profile": {
        "user_id": "MT-USER-001",
        "full_name": "John Doe",
        "age": 25,
        "country": "MT",
        "income_level": "medium",
        "occupation": "Freelancer",
        "kyc_status": "verified",
        "risk_profile": "medium",
        "historical_countries": ["MT", "IT"]
      },
      "baseline": {
        "user_id": "MT-USER-001",
        "avg_tx_amount_usd": 150.75,
        "avg_daily_total_usd": 450.00,
        "avg_tx_per_day": 3,
        "std_dev_amount": 50.25,
        "normal_hour_range": [9, 18],
        "excluded_anomalies_count": 2
      },
      "current_risk_score": 0,
      "current_risk_band": "CLEAN"
    }
  ]
}
```

### GET `/api/compliance/{jurisdiction_code}`

Returns the current compliance state for a jurisdiction.

**Path params:** `jurisdiction_code` = `MT` | `AE` | `KY`

**Response:**
```json
{
  "jurisdiction": "Malta",
  "jurisdiction_code": "MT",
  "current_version": "v1",
  "old_regulations": [
    {
      "regulation_update_id": "MT-OLD-001",
      "update_title": "Virtual Financial Assets Act 2018",
      "summary": "...",
      "date_effective": "November 1, 2018"
    }
  ],
  "new_regulations": [],
  "rulebook": {
    "amount_based": ["..."],
    "frequency_based": ["..."],
    "location_based": ["..."],
    "behavioural_pattern": ["..."],
    "risk_score": { "range": "0-100", "rules": [...], "capping": "..." },
    "risk_bands": { "HIGH": "...", "MEDIUM": "...", "LOW": "...", "CLEAN": "..." }
  },
  "available_new_regulations": [
    {
      "regulation_update_id": "MT-REG-001",
      "update_title": "VFA Licensing Enhancements",
      "summary": "...",
      "date_effective": "April 10, 2026"
    },
    {
      "regulation_update_id": "MT-REG-002",
      "update_title": "MDIA DLT System Certification",
      "summary": "...",
      "date_effective": "July 15, 2026"
    },
    {
      "regulation_update_id": "MT-REG-003",
      "update_title": "EU-Aligned AML Reporting for VFAs",
      "summary": "...",
      "date_effective": "October 20, 2026"
    }
  ]
}
```

### POST `/api/compliance/{jurisdiction_code}/push`

Pushes a new regulation into the compliance agentic workflow (4 sub-agents).

**Request body:**
```json
{
  "regulation_update_id": "MT-REG-001"
}
```

**Response:**
```json
{
  "jurisdiction_code": "MT",
  "new_version": "v2",
  "summary": "The VFA Licensing Enhancements regulation requires all VFA service providers...",
  "comparison_points": [
    "Licensing: Previously one-time registration → Now annual renewal with MFSA",
    "Audits: No cybersecurity audit requirement → Now mandatory annual cybersecurity audits",
    "Fines: Max €150,000 → Now up to €200,000 for non-compliance",
    "AML: Basic AML compliance → Enhanced AML risk assessments required"
  ],
  "impact_analysis": "3 out of 4 Malta users currently transact above €1,000 daily, which would trigger the new real-time monitoring. Estimated 12-18% increase in compliance costs...",
  "rulebook_changes": "Added annual licensing check rule, adjusted AML monitoring threshold to €1,000, added cybersecurity audit compliance requirement",
  "updated_rulebook": { "...full updated rulebook..." },
  "agent_chain": [
    {
      "agent": "Summarizer Agent",
      "icon": "📝",
      "status": "success",
      "message": "Summarized MT-REG-001: Annual VFA licensing renewal with cybersecurity audits",
      "duration_ms": 800
    },
    {
      "agent": "Comparison Agent",
      "icon": "⚖️",
      "status": "success",
      "message": "Generated 4 comparison points — 3 stricter, 1 new obligation",
      "duration_ms": 900
    },
    {
      "agent": "Analyzer Agent",
      "icon": "📊",
      "status": "alert",
      "message": "3/4 Malta users affected, 12-18% cost increase, €200k fine risk",
      "duration_ms": 1100
    },
    {
      "agent": "Rulebook Editor Agent",
      "icon": "✏️",
      "status": "complete",
      "message": "Rulebook updated — 2 rules modified, 1 rule added",
      "duration_ms": 1300
    }
  ]
}
```

### POST `/api/ingest-batch`

Injects a transaction batch through the transaction analysis workflow (Faker generates, then 4 agents process).

**Request body:**
```json
{
  "user_id": "AE-USER-001",
  "num_transactions": 5,
  "overrides": {
    "transaction_amount_usd": 55000.00,
    "transaction_country": "KP",
    "transaction_city": "Pyongyang",
    "transaction_currency": "USDT"
  }
}
```

- `user_id`: which user to generate transactions for
- `num_transactions`: how many transactions the Faker script should generate
- `overrides`: optional overrides to Faker defaults (this is how you inject anomalies — set a huge amount or a different country)

**Response:**
```json
{
  "user_id": "AE-USER-001",
  "user_name": "Jane Smith",
  "jurisdiction": "UAE",
  "risk_score": 100,
  "risk_band": "HIGH",
  "reasoning": "VARA Violation: The user executed a $55,000 USDT transfer from Pyongyang, North Korea — a jurisdiction with no VARA licensing. This transaction is 275× above the user's baseline average of $200. Additionally, the geo hop from Dubai to Pyongyang (5,000km) in 1 hour is physically impossible, indicating proxy or VPN usage which directly violates DFSA geo-fencing requirements.",
  "flags": [
    "Impossible geo hop: 5,000 km/h exceeds 800 km/h threshold [+60pts]",
    "Single tx $55,000 > 5× avg $200 [+55pts]",
    "Daily total $55,250 > 2× avg daily $600 [+30pts]",
    "New country KP never seen in history [+45pts]"
  ],
  "regulations_violated": [
    "VARA Stablecoin Issuance Guidelines (UAE-REG-001)",
    "DFSA Token Suitability Assessment — geo-fencing violation (UAE-REG-002)",
    "CARF Crypto Reporting Framework — AED 50,000 threshold (UAE-REG-003)"
  ],
  "agent_chain": [
    {
      "agent": "Profile Agent",
      "icon": "🔍",
      "status": "success",
      "message": "Loaded AE-USER-001 (Jane Smith, UAE, high income, verified KYC)",
      "duration_ms": 12
    },
    {
      "agent": "Preprocessor Agent",
      "icon": "📊",
      "status": "success",
      "message": "Preprocessed 5 transactions | Distance: 5,000km | Time: 3,600s | Daily total: $55,250 | New country: YES",
      "duration_ms": 45
    },
    {
      "agent": "Baseline Calculator Agent",
      "icon": "📈",
      "status": "success",
      "message": "Baseline computed — avg $200/tx, $600/day, 4 tx/day, σ=$75",
      "duration_ms": 1100
    },
    {
      "agent": "Anomaly Detector Agent",
      "icon": "🚨",
      "status": "high",
      "message": "ANOMALY DETECTED — Risk: 100/100 HIGH | 4 flags | 3 regulations violated",
      "duration_ms": 1500
    }
  ],
  "preprocessed": {
    "distance_km": 5000.0,
    "time_since_last_sec": 3600,
    "daily_total_usd": 55250.50,
    "is_new_country": true,
    "tx_count_per_day": 5
  },
  "baseline": {
    "user_id": "AE-USER-001",
    "avg_tx_amount_usd": 200.0,
    "avg_daily_total_usd": 600.0,
    "avg_tx_per_day": 4,
    "std_dev_amount": 75.0,
    "normal_hour_range": [10, 20],
    "excluded_anomalies_count": 1
  },
  "generated_transactions": [
    {
      "user_id": "AE-USER-001",
      "timestamp": "2026-02-07T14:00:00Z",
      "transaction_amount_usd": 55000.0,
      "transaction_currency": "USDT",
      "transaction_type": "transfer",
      "transaction_country": "KP",
      "transaction_city": "Pyongyang"
    }
  ],
  "timestamp": "2026-02-07T14:00:00Z"
}
```

### GET `/api/rules/{jurisdiction_code}`

Returns the **current** rulebook for a jurisdiction (reflects any edits by the Rulebook Editor Agent).

**Response:**
```json
{
  "jurisdiction": "Malta",
  "current_version": "v1",
  "rulebook": { "...current rulebook..." }
}
```

---

## 8. Frontend — Screen 1: Live Monitor

**Route:** `/monitor`

### Layout
Two-panel split: Left (35%) + Right (65%)

### Left Panel: User Roster (`UserRoster.tsx` + `UserCard.tsx`)

- Fetches user list from `GET /api/init` on mount
- Renders 10 `UserCard` components
- **Sorted by `current_risk_score` descending** (highest risk at top)
- When `POST /api/ingest-batch` returns new scores, the list re-sorts with **Framer Motion `layoutId`** animation
- Newly flagged users get a **red pulse border animation** (CSS keyframe, 2 cycles)

**UserCard contents:**
- Avatar (initials-based, colored circle — color derived from risk band)
- Full name
- Country flag (emoji: 🇲🇹 / 🇦🇪 / 🇰🇾)
- `RiskBadge` component (colored pill: RED/AMBER/GREEN/GREY)
- Risk score number

**Interaction:** Click a card → sets `selectedUserId` state → right panel updates

### Right Panel: Intelligence Detail (`IntelligenceDetail.tsx`)

Only renders when a user is selected. Scrollable.

**Components in order:**

1. **Header** — name, jurisdiction badge, KYC status, `RiskGauge`
2. **Identity Card** (`IdentityCard.tsx`) — age, occupation, income, historical countries
3. **Behavioral Analysis** (`BehavioralAnalysis.tsx`)
   - `StatisticalBrain.tsx` — bar charts or comparison cards: baseline avg vs current for amount, daily total, frequency
   - `PhysicsBrain.tsx` — distance, time, speed calculation, "Physics Violation" badge if triggered
4. **AI Guardian** (`AIGuardian.tsx`)
   - `AgentChainLog.tsx` — vertical timeline showing each agent step with icon, status color, message, duration
   - Below the chain: the full `reasoning` text from the Anomaly Detector Agent in the terminal-style box
   - Below reasoning: list of `regulations_violated` with Act names highlighted in Deriv red

### Data Injection Flow (`DataInjectionFlow.tsx`)

Collapsible bottom drawer (slides up from bottom of screen).

**Toggle button:** Fixed at bottom-center — "Data Injection Flow" label with chevron icon.

**Contents when open:**
- **User selector dropdown** (populated from user list)
- **Number of transactions** — numeric input (how many the Faker script generates, default: 5)
- **Override controls** (optional — to inject anomalies):
  - Transaction amount override (USD) — leave blank for Faker defaults
  - Transaction country override — dropdown (with preset countries including risky ones like KP, IR)
  - Transaction currency override — dropdown (ETH, BTC, USDT, etc.)
  - Transaction city override — text input
- **"Inject Transaction Batch"** button (Deriv red, prominent)

**On submit:**
1. Sends `user_id`, `num_transactions`, and `overrides` to `POST /api/ingest-batch`
2. Backend: Faker generates transactions → Profile Agent → Preprocessor + Baseline in parallel → Anomaly Detector
3. Response updates user list with new scores
4. Auto-selects the injected user in the roster
5. Right panel shows new analysis with full agent chain + LLM reasoning

---

## 9. Frontend — Screen 2: Regulatory Hub

**Route:** `/regulatory`

### Layout
Full-width content area with world map background.

### Background (`WorldMapBackground.tsx`)
- SVG or image of a black-and-white world map
- Opacity: 5–8%
- When a jurisdiction tab is active, the corresponding country subtly highlights (opacity bump to ~15%)

### Jurisdiction Tabs (`JurisdictionTabs.tsx`)
Three tabs at the top: **Malta** | **UAE** | **Cayman Islands**
- Each tab has a flag icon
- Active tab: Deriv red underline or bottom border
- Clicking a tab fetches data via `GET /api/compliance/{jurisdiction_code}`

### Tab Content (per jurisdiction)

#### Version Label (`VersionLabel.tsx`)
Simple badge showing current version: `v1`, `v2`, `v3`
Updates after each push.

#### Current Compliance Summary (`ComplianceSummary.tsx`)
Card showing:
- Current version label
- Old (foundational) regulations — brief list
- Any new regulations already pushed — brief list
- "Currently monitoring against {n} regulations"

#### Active Rulebook (`ActiveRulebook.tsx`)
Collapsible sections showing the current (possibly modified) rulebook:
- Amount-based rules
- Frequency-based rules
- Location-based rules
- Behavioral pattern rules
- Risk scoring table (categories, rules, point values)
- Risk bands

Each rule shows the text + point value + highlighted Act name in Deriv red.

**Important:** This component re-renders after a compliance push to show the Rulebook Editor Agent's changes.

#### Push New Compliance (`PushCompliance.tsx`)
This is the control for triggering the compliance agentic workflow.

- Shows a list of **available new regulations** for this jurisdiction (loaded from `available_new_regulations` in the API response)
- Each regulation is a card showing: ID, title, summary, effective date
- Each card has a **"Push"** button
- Clicking "Push" calls `POST /api/compliance/{code}/push` with that regulation's ID
- While the 4 agents are running, show a loading state with agent names appearing one by one

#### Compliance Agent Output (`ComplianceAgentOutput.tsx`)
After push completes, this section displays the full output from all 4 compliance agents:

**Summarizer output:**
- Clean summary card of the new regulation

**Comparison output:**
- List of comparison points (old vs new) — each point as a bullet or card

**Analyzer output:**
- Impact analysis text with numbers (users affected, cost estimates, risk areas)

**Rulebook Editor output:**
- Description of what changed in the rulebook
- `RulebookDiff.tsx` — a before/after view showing the old rulebook vs new rulebook with changes highlighted (added rules in green, modified in amber, removed in red)

**Agent chain:**
- Same `AgentChainLog.tsx` component as the Live Monitor, but showing the 4 compliance agents instead of the 4 transaction agents

---

## 10. Frontend — Shared Components

### `RiskBadge.tsx`
Props: `band: "HIGH" | "MEDIUM" | "LOW" | "CLEAN"`
Renders a colored pill with the band text.

### `CountryFlag.tsx`
Props: `code: "MT" | "AE" | "KY"`
Renders the corresponding flag emoji or small icon.

### `RiskGauge.tsx`
Props: `score: number` (0–100), `animated: boolean`
Semi-circular gauge. Color transitions from teal (0) → amber (50) → red (75+).
Animated on score change using Framer Motion.

### `AgentChainLog.tsx`
Props: `chain: AgentLogEntry[]`
Vertical timeline. Each step shows:
- Icon (emoji)
- Agent name
- Status dot (green/amber/red)
- Message text
- Duration (ms)

Steps appear sequentially with a staggered animation (100ms delay between each) to simulate the agents "working."

**Used on both screens:** Live Monitor (transaction agents) and Regulatory Hub (compliance agents).

### `ThemeToggle.tsx`
Sun/moon icon button. Uses `next-themes` to switch between dark and light mode.

---

## 11. Faker Data Generation Script

### Location: `backend/scripts/faker_generator.py`

### Purpose
Generates realistic synthetic transaction data for a given user. Used by the `POST /api/ingest-batch` endpoint.

### How It Works

```python
from faker import Faker
import random

def generate_transactions(
    user_id: str,
    user_profile: UserProfile,
    num_transactions: int = 5,
    overrides: dict = None
) -> list[RawTransaction]:
    """
    Generates a batch of realistic transactions for a user.
    
    Default behavior: generates normal, baseline-consistent transactions.
    Overrides: allows injecting anomalous values (high amount, different country, etc.)
    """
    fake = Faker()
    transactions = []
    
    # User's normal parameters (derived from profile)
    normal_countries = user_profile.historical_countries
    normal_currencies = ["ETH", "BTC", "USDT"]
    normal_amount_range = (50, 500)  # varies by income level
    normal_types = ["deposit", "withdrawal", "transfer"]
    
    for i in range(num_transactions):
        tx = {
            "user_id": user_id,
            "timestamp": generate_timestamp_for_today(i),
            "transaction_amount_usd": round(random.uniform(*normal_amount_range), 2),
            "transaction_currency": random.choice(normal_currencies),
            "transaction_type": random.choice(normal_types),
            "transaction_country": random.choice(normal_countries),
            "transaction_city": fake.city()
        }
        
        # Apply overrides (this is how anomalies are injected)
        if overrides:
            for key, value in overrides.items():
                if value is not None:
                    tx[key] = value
        
        transactions.append(RawTransaction(**tx))
    
    return transactions
```

### Override Behavior
- **No overrides:** Faker generates normal transactions consistent with user profile
- **Amount override:** e.g., `55000` — all transactions use this amount (spike)
- **Country override:** e.g., `"KP"` — all transactions from this country (geo anomaly)
- **Can combine:** Amount + country override = layering attack scenario

### Amount Ranges by Income Level

| Income Level | Normal Range | Description |
|-------------|-------------|-------------|
| low | $20–$200 | Student-level transactions |
| medium | $50–$500 | Mid-range trader |
| high | $100–$2,000 | Active trader |

---

## 12. Static Data Files (JSON)

### `data/users.json`

Contains 10 user profiles. Distribution: ~3-4 per jurisdiction. Mix of income levels and occupations.

```json
[
  {
    "user_id": "MT-USER-001",
    "age": 25,
    "country": "MT",
    "full_name": "John Doe",
    "income_level": "medium",
    "occupation": "Freelancer",
    "kyc_status": "verified",
    "risk_profile": "medium",
    "historical_countries": ["MT", "IT"]
  },
  {
    "user_id": "AE-USER-001",
    "age": 25,
    "country": "AE",
    "full_name": "Jane Smith",
    "income_level": "high",
    "occupation": "Engineer",
    "kyc_status": "verified",
    "risk_profile": "high",
    "historical_countries": ["AE", "SA"]
  },
  {
    "user_id": "KY-USER-001",
    "age": 25,
    "country": "KY",
    "full_name": "Alex Johnson",
    "income_level": "low",
    "occupation": "Student",
    "kyc_status": "verified",
    "risk_profile": "low",
    "historical_countries": ["KY", "US"]
  }
]
```

### `data/baselines.json`

Contains initial baselines (will be updated by Baseline Calculator Agent):

```json
[
  {
    "user_id": "MT-USER-001",
    "avg_tx_amount_usd": 150.75,
    "avg_daily_total_usd": 450.00,
    "avg_tx_per_day": 3,
    "std_dev_amount": 50.25,
    "normal_hour_range": [9, 18],
    "excluded_anomalies_count": 2
  }
]
```

### `data/compliance/malta.json` (and `uae.json`, `cayman.json`)

Contains the compliance state for each jurisdiction:

```json
{
  "jurisdiction": "Malta",
  "jurisdiction_code": "MT",
  "current_version": "v1",
  "old_regulations": [
    {
      "regulation_update_id": "MT-OLD-001",
      "update_title": "Virtual Financial Assets Act 2018",
      "summary": "Establishes a regulatory framework for virtual financial assets, requiring licensing for issuers and service providers, with emphasis on AML compliance and investor protection. Fines up to €150,000 for violations.",
      "date_effective": "November 1, 2018"
    }
  ],
  "new_regulations": [],
  "rulebook": {
    "amount_based": [
      "Transaction amount > 3× user's historical average (violates basic AML thresholds under VFA Act)",
      "Daily total amount > 2× user's usual daily total"
    ],
    "frequency_based": [
      "Transactions per day > 2× user's normal frequency",
      "Multiple transactions within 15 min (burst activity)"
    ],
    "location_based": [
      "Transaction from a new country not seen in history",
      "Rapid country switching within short time (geo-hopping)"
    ],
    "behavioural_pattern": [
      "Inconsistent behaviour vs declared profile (e.g., high volume from low-activity history)"
    ],
    "risk_score": {
      "range": "0-100",
      "rules": [
        { "category": "Amount", "rule": "Single tx > 5× user avg", "points": 55 },
        { "category": "Amount", "rule": "Single tx > 3× user avg (but ≤5×)", "points": 35 },
        { "category": "Amount/Volume", "rule": "Daily total > 2× avg daily", "points": 30 },
        { "category": "Frequency", "rule": "≥4 tx in ≤15 min (burst)", "points": 35 },
        { "category": "Geo", "rule": "New country (never seen before)", "points": 45 },
        { "category": "Geo", "rule": "Impossible geo hop (actual time < min travel time)", "points": 60 },
        { "category": "Profile", "rule": "High volume inconsistent with profile", "points": 35 }
      ],
      "capping": "min(risk_score, 100)"
    },
    "risk_bands": {
      "HIGH": "≥75 (alert for MFSA non-compliance)",
      "MEDIUM": "50–74 (review for AML risks)",
      "LOW": "25–49 (watch for patterns)",
      "CLEAN": "<25"
    }
  }
}
```

### `data/compliance/new_regulations/malta_v2.json` (pre-defined regulations available to push)

```json
[
  {
    "regulation_update_id": "MT-REG-001",
    "update_title": "VFA Licensing Enhancements",
    "summary": "Requires all VFA service providers to renew licenses annually with MFSA, including enhanced cybersecurity audits and AML risk assessments. Fines up to €200,000 for non-compliance.",
    "date_effective": "April 10, 2026"
  },
  {
    "regulation_update_id": "MT-REG-002",
    "update_title": "MDIA DLT System Certification",
    "summary": "Mandates certification of DLT platforms for reliability, with quarterly reporting on system uptime and security breaches; prohibits non-certified platforms from operating.",
    "date_effective": "July 15, 2026"
  },
  {
    "regulation_update_id": "MT-REG-003",
    "update_title": "EU-Aligned AML Reporting for VFAs",
    "summary": "Expands AML obligations to include real-time transaction monitoring over €1,000, with mandatory reports to FIAU; aligns with EU's TFR for cross-border transfers.",
    "date_effective": "October 20, 2026"
  }
]
```

---

## 13. LLM Integration

### Where the LLM Is Used (5 agents total)

| Agent | Workflow | Purpose |
|-------|----------|---------|
| Baseline Calculator Agent | Transaction Analysis | Computes user baselines from transaction history |
| Anomaly Detector Agent | Transaction Analysis | Reasons about anomalies, assigns risk score, cites regulations |
| Summarizer Agent | Compliance Update | Summarizes new regulatory act |
| Comparison Agent | Compliance Update | Compares old vs new regulations |
| Analyzer Agent | Compliance Update | Analyzes impact on users & company with numbers |
| Rulebook Editor Agent | Compliance Update | Modifies the rulebook based on analysis |

### What Is NOT LLM (2 agents)

| Agent | Workflow | Why Not LLM |
|-------|----------|-------------|
| Profile Agent | Transaction Analysis | Pure data lookup — no reasoning needed |
| Preprocessor Agent | Transaction Analysis | Deterministic math (distance, time, totals) — LLM would be slower and less accurate |

### Setup

- API key stored in `backend/.env`
- Client wrapper in `backend/utils/llm.py`
- Async calls using `openai` SDK (or `httpx` for other providers)
- All LLM agents use structured output (JSON mode) to ensure parseable responses

### `backend/utils/llm.py` (conceptual)

```python
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
)

async def call_llm(
    system_prompt: str,
    user_prompt: str,
    json_mode: bool = True
) -> str:
    """Wrapper for LLM calls used by all agents."""
    response = await client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "gpt-4o"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"} if json_mode else None,
        temperature=0.3  # Low temperature for consistency
    )
    return response.choices[0].message.content
```

### Fallback Strategy

If any LLM call fails (timeout, rate limit, key issue):
- **Baseline Calculator:** Falls back to simple mathematical averages computed locally
- **Anomaly Detector:** Falls back to deterministic point-based scoring (the original rule system)
- **Compliance agents:** Returns an error message, doesn't modify the rulebook

The system **never breaks** because an LLM is down. Every LLM agent has a fallback path.

### Temperature Settings

| Agent | Temperature | Rationale |
|-------|-------------|-----------|
| Baseline Calculator | 0.1 | Needs precise, consistent numbers |
| Anomaly Detector | 0.3 | Needs reasoning but should be consistent |
| Summarizer | 0.4 | Slightly creative for readable summaries |
| Comparison | 0.3 | Structured comparison, moderate creativity |
| Analyzer | 0.3 | Analytical, needs precision with numbers |
| Rulebook Editor | 0.2 | Must produce valid JSON rulebook, low creativity |

---

## 14. Environment Configuration

### Backend `.env`

```env
# LLM Configuration
LLM_API_KEY=sk-your-api-key-here
LLM_MODEL=gpt-4o
LLM_BASE_URL=https://api.openai.com/v1

# Server
HOST=0.0.0.0
PORT=8000

# CORS (frontend URL)
FRONTEND_URL=http://localhost:3000
```

### Frontend `.env.local`

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend `requirements.txt`

```
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
python-dotenv>=1.0.0
openai>=1.0.0
httpx>=0.25.0
faker>=20.0.0
```

### Running Locally

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 15. Demo Script

### Setup
- Backend running on `localhost:8000`
- Frontend running on `localhost:3000`
- All jurisdictions start at v1 (old regulations, original rulebook)
- All users start at CLEAN or LOW risk

### Act 1: The Regulatory Landscape (20 seconds)

1. Open **Regulatory Hub**
2. Click **UAE** tab — show v1 is active (SCA Crypto Regulation 2020)
3. Show the current rulebook — "These are the rules we're monitoring against today."

### Act 2: New Compliance Arrives (45 seconds)

4. In the available regulations section, find **"VARA Stablecoin Issuance Guidelines"**
5. Click **"Push"**
6. Watch the **4 compliance agents run** (agent chain appears step by step):
   - Summarizer: "VARA requires stablecoin licensing, AED reserves, privacy coin ban..."
   - Comparison: "Old: no stablecoin rules → New: full VARA licensing framework"
   - Analyzer: "3 out of 4 UAE users affected, $200k compliance cost, 10-15% user reduction risk"
   - Rulebook Editor: "Added VARA stablecoin rule, geo-fencing for non-UAE users, AED 50k threshold"
7. Show the **rulebook diff** — before vs after
8. Say: "Our AI just read the regulation, analyzed its impact, and **autonomously updated the monitoring rulebook**. We're now live on v2."

### Act 3: Business as Usual (15 seconds)

9. Switch to **Live Monitor**
10. Show all 10 users — mostly CLEAN/LOW
11. Click a normal user — show baseline, clean agent chain
12. Say: "Under the updated VARA rules, most users are still compliant."

### Act 4: The Anomaly (40 seconds)

13. Open **Data Injection Flow**
14. Select **Jane Smith (AE-USER-001)**
15. Set overrides: amount $55,000, country: North Korea (KP)
16. Set num_transactions: 5
17. Click **"Inject Transaction Batch"**
18. Watch the **4 transaction agents run** (agent chain appears step by step):
    - Profile Agent: "Loaded Jane Smith..."
    - Preprocessor + Baseline run in parallel
    - Anomaly Detector: "ANOMALY DETECTED — Risk 100/100 HIGH"
19. Jane's card flashes red, jumps to #1
20. Risk gauge sweeps to 100
21. AI Guardian shows the LLM's full reasoning citing VARA, DFSA, CARF violations

### Act 5: The Punchline (15 seconds)

22. Say: "Two agentic workflows. The first read a new UAE regulation and autonomously rewrote the rulebook. The second detected an anomaly by reasoning about physics, behavior, and the rules that were just updated 60 seconds ago. Eight AI agents, full explainability, every decision traceable."

**Total demo time: ~2.5 minutes**

---

## Appendix: Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| No database | JSON files (mutable) | Hackathon MVP — zero setup, portable, easy to reset. Rulebook JSON is written to at runtime. |
| No orchestrator | Sequential agent calls | Simple demo, predictable flow, easy to debug |
| Pydantic everywhere | Strict typing | Professional, catches errors early, self-documenting |
| Faker for data generation | Realistic synthetic data | Generates volume with realistic noise, feels like a real system |
| Preprocessor is local | Deterministic Python | Distance/time math should be precise, not hallucinated by LLM |
| Baseline via LLM | Dynamic baselines | Baselines update as new data flows, more "adaptive" narrative |
| Anomaly detection via LLM | LLM reasoning | Judges want "AI must add value" — LLM reasoning is the core differentiator |
| Rulebook Editor Agent | LLM modifies rules | The AI autonomously updates the rulebook — strongest "agentic" proof point |
| Simple version labels | v1, v2, v3 | No complex state machine, just increment on push |
| Agent chain in response | Full visibility | Judges see both workflows' agents working, meets explainability requirement |
| Dark mode default | Deriv brand | Professional appearance, matches Deriv's institutional aesthetic |
| Parallel preprocessing + baseline | Speed + realism | Shows agents running concurrently, reduces total latency |
| Fallback for every LLM agent | Reliability | System never breaks if LLM is down — every agent has a local fallback |
