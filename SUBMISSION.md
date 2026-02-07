# Deriv AI Compliance Manager

**Team Submission — Deriv Hackathon 2026**

---

## Problem Statement

Compliance officers at crypto trading platforms face two core challenges:

1. **Behavioral Monitoring at Scale** — Manually reviewing thousands of transactions across multiple jurisdictions is slow, error-prone, and unable to catch sophisticated anomalies like impossible travel or layered transactions.
2. **Regulatory Change Management** — When new regulations drop (e.g., VARA in UAE, MiCA-aligned rules in Malta), updating internal monitoring rules is a manual, weeks-long process that leaves the company exposed during the gap.

There is no tool today that can **detect anomalies** and **adapt to new regulations** autonomously, in real time, with full explainability.

---

## Our Solution

**Deriv AI Compliance Manager** is an AI-powered compliance monitoring dashboard that combines **behavioral anomaly detection** with **regulatory intelligence** across three jurisdictions — Malta, UAE, and Cayman Islands.

It features a **Dual Brain** architecture:

- **Behavioral Brain** — Detects transaction anomalies using LLM-powered reasoning against user baselines, preprocessed transaction data, and jurisdiction-specific rulebooks.
- **Regulatory Brain** — Reads new compliance regulations, compares them against existing rules, analyzes impact on users, and **autonomously rewrites the monitoring rulebook** — all without human intervention.

---

## How It Works

### Two Agentic Workflows, Eight AI Agents

#### Workflow 1: Transaction Analysis (Behavioral Monitoring)

When a compliance officer injects transaction data for a user:

| Step | Agent | Type | What It Does |
|------|-------|------|-------------|
| 1 | **Profile Agent** | Local | Loads user profile (KYC, jurisdiction, income, history) |
| 2a | **Preprocessor Agent** | Local | Enriches transactions — calculates distance, travel speed, daily totals, new country flags |
| 2b | **Baseline Calculator Agent** | LLM | Computes/updates the user's behavioral baseline from transaction history |
| 3 | **Anomaly Detector Agent** | LLM | Reasons about anomalies using all context + the jurisdiction rulebook. Assigns a risk score (0–100), identifies flags, and cites specific regulations violated |

Steps 2a and 2b run **in parallel** for speed.

**Output:** A full risk assessment with score, risk band (HIGH/MEDIUM/LOW/CLEAN), flags, LLM reasoning, and the complete agent chain — every decision is traceable.

#### Workflow 2: Compliance Update (Regulatory Intelligence)

When a compliance officer pushes a new regulation:

| Step | Agent | Type | What It Does |
|------|-------|------|-------------|
| 1 | **Summarizer Agent** | LLM | Summarizes the new regulation in plain language |
| 2 | **Comparison Agent** | LLM | Generates specific comparison points (old vs new — what's stricter, what's new) |
| 3 | **Analyzer Agent** | LLM | Analyzes impact on real users with numbers (e.g., "3 out of 4 UAE users affected") |
| 4 | **Rulebook Editor Agent** | LLM | **Autonomously modifies** the monitoring rulebook based on the analysis |

**Output:** Summary, comparison points, impact analysis, rulebook diff, and the updated rulebook — now live for all future anomaly detection.

**The key insight:** After Workflow 2 updates the rulebook, Workflow 1 immediately uses the new rules. Regulations go from text to enforcement in seconds.

---

## The Two User Controls (World Simulator)

The user acts as a **simulator for the world**, controlling the environment in two ways:

1. **Changing user trading behavior** — Via the Data Injection Flow, the user sets parameters (amount, country, currency) and the Faker script generates transactions. Overrides allow injecting anomalies like $55,000 transfers from North Korea.

2. **Pushing new compliance** — Via the Regulatory Hub, the user selects a new regulation and pushes it through the 4-agent compliance workflow. The rulebook updates autonomously.

---

## Jurisdictions Covered

| Jurisdiction | Code | Foundational Regulation | Users |
|-------------|------|------------------------|-------|
| **Malta** | MT | Virtual Financial Assets Act 2018 | 3 users |
| **UAE** | AE | SCA Crypto Regulation 2020 | 4 users |
| **Cayman Islands** | KY | VASP Act 2020 | 3 users |

Each jurisdiction has 3 new regulations available to push (up to v4), with jurisdiction-specific rulebooks covering amount-based, frequency-based, location-based, and behavioral pattern rules.

---

## Frontend: Two Screens

### Screen 1: Live Monitor (`/monitor`)

- **Left Panel** — User roster sorted by risk score. Cards show name, country flag, risk badge, and score. Newly flagged users pulse red and animate to the top.
- **Right Panel** — Full intelligence detail for the selected user:
  - Risk gauge (animated, 0–100)
  - Identity card (KYC, occupation, income)
  - Statistical Brain (baseline vs current comparisons)
  - Physics Brain (distance, speed, impossible travel detection)
  - AI Guardian (agent chain log + full LLM reasoning + regulations cited)
- **Data Injection Flow** — Bottom drawer to inject transactions with optional anomaly overrides.

### Screen 2: Regulatory Hub (`/regulatory`)

- **Jurisdiction Tabs** — Malta | UAE | Cayman Islands
- **Compliance Summary** — Current version, active regulations, monitoring status
- **Active Rulebook** — Collapsible sections showing all rules with point values
- **Push New Compliance** — Cards for available regulations with a "Push" button
- **Agent Output** — Full output from all 4 compliance agents after a push, including a rulebook diff (before/after with highlighted changes)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js, TypeScript, Tailwind CSS, Framer Motion, Recharts, Lucide Icons |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, Uvicorn |
| **Data Generation** | Faker (synthetic transaction data) |
| **LLM Integration** | OpenAI SDK (GPT-4o) with structured JSON output |
| **Database** | None — JSON files (mutable at runtime) |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/init` | Returns all users with profiles, baselines, and risk state |
| GET | `/api/compliance/{code}` | Returns compliance state for MT, AE, or KY |
| GET | `/api/rules/{code}` | Returns current rulebook for a jurisdiction |
| POST | `/api/ingest-batch` | Triggers transaction analysis workflow (4 agents) |
| POST | `/api/compliance/{code}/push` | Triggers compliance update workflow (4 agents) |

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **LLM for anomaly detection** | The LLM reasons holistically across behavior, geography, and regulations — far richer than rule-based scoring |
| **LLM for rulebook editing** | The strongest "agentic" proof point — the AI autonomously updates the rules it enforces |
| **Preprocessor is local/deterministic** | Distance and speed math must be precise, not hallucinated |
| **Every LLM agent has a fallback** | The system never breaks if the LLM is down — reliability first |
| **No database, JSON files** | Zero setup, portable, easy to reset — appropriate for hackathon MVP |
| **Agent chain in every response** | Full explainability — judges and compliance officers see every agent's contribution |
| **Parallel preprocessing + baseline** | Reduces latency and demonstrates concurrent agent execution |

---

## Demo Flow (2.5 minutes)

1. **Regulatory Landscape** — Show UAE at v1 with current rulebook
2. **New Compliance Arrives** — Push VARA Stablecoin Guidelines → Watch 4 agents run → Rulebook autonomously updates → Now live on v2
3. **Business as Usual** — Switch to Live Monitor → Users are mostly CLEAN/LOW
4. **The Anomaly** — Inject $55,000 transfer from North Korea for a UAE user → 4 agents detect anomaly → Risk 100 HIGH → Full reasoning cites VARA violations
5. **The Punchline** — "Two agentic workflows. The first read a new regulation and rewrote the rulebook. The second detected an anomaly using rules that were updated 60 seconds ago. Eight AI agents, full explainability, every decision traceable."

---

## What Makes This Different

- **Not just detection — adaptation.** The system doesn't just flag anomalies; it reads new regulations and rewrites its own rules.
- **Full explainability.** Every risk score comes with the complete agent chain, LLM reasoning, and specific regulation citations.
- **Multi-jurisdictional.** Three separate regulatory frameworks, each with its own evolving rulebook.
- **The loop is closed.** Push a regulation → rulebook updates → next transaction is scored against the new rules. No human in the loop for rule adaptation.
