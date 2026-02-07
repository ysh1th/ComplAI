# ComplAi AI Compliance Manager

An AI-powered compliance monitoring dashboard for crypto trading that combines behavioral anomaly detection with regulatory intelligence across three jurisdictions — Malta, UAE, and Cayman Islands.

Built for the Deriv Hackathon 2026.

---

## Architecture

The application consists of two main parts:

- **Backend** — Python FastAPI server with 8 AI agents (2 agentic workflows)
- **Frontend** — Next.js 16 dashboard with two screens (Live Monitor + Regulatory Hub)

### Two Agentic Workflows

**Workflow 1: Transaction Analysis (Behavioral Monitoring)**

```
User injects transaction data
  → Profile Agent (local)
  → Preprocessor Agent (local) + Baseline Calculator Agent (LLM) [parallel]
  → Anomaly Detector Agent (LLM)
  → Returns: risk score, flags, reasoning, regulations violated
```

**Workflow 2: Compliance Update (Regulatory Intelligence)**

```
User pushes a new regulation
  → Summarizer Agent (LLM)
  → Comparison Agent (LLM)
  → Analyzer Agent (LLM)
  → Rulebook Editor Agent (LLM) — autonomously modifies the rulebook
  → Returns: summary, comparison, impact analysis, updated rulebook
```

---

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** and **npm**
- **OpenAI API key** (or compatible LLM provider)

---

## Setup & Run

### 1. Clone / Navigate to the project

```bash
cd Deriv_Hackathon
```

### 2. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Configure your LLM API key
# Edit the .env file and replace the placeholder key with your real one
```

Open `backend/.env` and set your API key:

```env
LLM_API_KEY=sk-your-real-openai-api-key
LLM_MODEL=gpt-4o
LLM_BASE_URL=https://api.openai.com/v1
```

> **Note:** The application works without a real API key — every LLM agent has a deterministic fallback. However, for the full AI-powered experience (LLM reasoning, dynamic baselines, intelligent rulebook editing), a valid key is required.

Start the backend server:

```bash
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at **http://localhost:8000**.

### 3. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install Node dependencies
npm install

# Start the development server
npm run dev
```

The dashboard will be available at **http://localhost:3000**.

---

## Using the Application

### Screen 1: Live Monitor (`/monitor`)

1. **View Users** — The left panel shows all 10 users sorted by risk score (highest first). Click any user to view their intelligence profile.

2. **Inject Transaction Data** — Click the red **"Data Injection Flow"** button at the bottom of the screen. This opens a drawer where you can:
   - Select a target user
   - Set the number of transactions to generate
   - Optionally override values to inject anomalies:
     - **Amount** — e.g., `55000` for a large transaction
     - **Country** — e.g., `KP` (North Korea) for a geo anomaly
     - **Currency** — e.g., `USDT`
   - Click **"Inject Transaction Batch"**

3. **View Results** — After injection, the selected user's card updates with the new risk score, and the right panel shows:
   - Risk gauge (animated)
   - Statistical Brain (baseline vs current comparison)
   - Physics Brain (distance, speed, impossible travel detection)
   - AI Guardian (full agent chain log + LLM reasoning)

### Screen 2: Regulatory Hub (`/regulatory`)

1. **Select Jurisdiction** — Click the Malta, UAE, or Cayman Islands tab.

2. **View Current State** — See the compliance summary, active rulebook, and risk scoring table.

3. **Push New Regulation** — In the "Available New Regulations" section, click **"Push"** on any regulation card. This triggers the 4-agent compliance workflow:
   - Summarizer summarizes the regulation
   - Comparison Agent compares old vs new
   - Analyzer Agent assesses impact on users
   - Rulebook Editor Agent autonomously modifies the monitoring rules

4. **View Output** — After the push completes, see the full agent chain, summary, comparison points, impact analysis, and rulebook changes.

---


---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, TypeScript, Tailwind CSS v4, Framer Motion, Recharts, Lucide Icons, next-themes |
| Backend | Python 3.11+, FastAPI, Pydantic v2, Uvicorn |
| Data Generation | Faker |
| LLM Integration | OpenAI SDK (GPT-4o) with fallbacks |
| Database | None — JSON files (mutable at runtime) |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/init` | Returns all users with profiles, baselines, and risk state |
| GET | `/api/compliance/{code}` | Returns compliance state for MT, AE, or KY |
| GET | `/api/rules/{code}` | Returns current rulebook for a jurisdiction |
| POST | `/api/ingest-batch` | Triggers transaction analysis workflow |
| POST | `/api/compliance/{code}/push` | Triggers compliance update workflow |
| GET | `/api/health` | Health check |

---

## Project Structure

```
Deriv_Hackathon/
├── README.md
├── IMPLEMENTATION_GUIDE.md
│
├── backend/
│   ├── main.py                          # FastAPI app with all endpoints
│   ├── requirements.txt                 # Python dependencies
│   ├── .env                             # LLM API key configuration
│   ├── models/                          # Pydantic schemas
│   │   ├── user.py                      # UserProfile, UserBaseline
│   │   ├── transaction.py               # RawTransaction, PreprocessedTransaction
│   │   ├── compliance.py                # Regulation, Rulebook, JurisdictionCompliance
│   │   ├── risk.py                      # AnomalyResult, RiskBand
│   │   └── agent_log.py                 # AgentLogEntry, FullAnalysisResponse
│   ├── agents/                          # 8 AI agents
│   │   ├── profile_agent.py             # Local — loads user profile
│   │   ├── preprocessor_agent.py        # Local — enriches transactions
│   │   ├── baseline_agent.py            # LLM — computes user baselines
│   │   ├── anomaly_agent.py             # LLM — detects anomalies
│   │   ├── summarizer_agent.py          # LLM — summarizes regulations
│   │   ├── comparison_agent.py          # LLM — compares old vs new
│   │   ├── analyzer_agent.py            # LLM — analyzes impact
│   │   └── rulebook_editor_agent.py     # LLM — modifies rulebook
│   ├── scripts/
│   │   └── faker_generator.py           # Synthetic transaction generator
│   ├── utils/
│   │   ├── llm.py                       # LLM client wrapper
│   │   └── geo.py                       # Distance/speed calculations
│   └── data/
│       ├── users.json                   # 10 user profiles
│       ├── baselines.json               # User baselines (updated at runtime)
│       └── compliance/
│           ├── malta.json               # Malta compliance + rulebook
│           ├── uae.json                 # UAE compliance + rulebook
│           ├── cayman.json              # Cayman compliance + rulebook
│           └── new_regulations/         # Regulations available to push
│
└── frontend/
    ├── package.json
    ├── app/
    │   ├── layout.tsx                   # Root layout with sidebar
    │   ├── monitor/page.tsx             # Screen 1: Live Monitor
    │   └── regulatory/page.tsx          # Screen 2: Regulatory Hub
    ├── components/
    │   ├── layout/                      # Sidebar, ThemeToggle
    │   ├── monitor/                     # UserRoster, IntelligenceDetail, etc.
    │   ├── regulatory/                  # JurisdictionTabs, ActiveRulebook, etc.
    │   └── shared/                      # RiskBadge, RiskGauge, AgentChainLog
    ├── lib/
    │   ├── api.ts                       # API client
    │   ├── types.ts                     # TypeScript interfaces
    │   └── utils.ts                     # Helper functions
    └── hooks/                           # useUsers, useCompliance, useInjectBatch
```

---

## Jurisdictions & Users

| Jurisdiction | Code | Users |
|-------------|------|-------|
| Malta | MT | Marco Vella, Sofia Borg, Luca Camilleri |
| UAE | AE | Rashid Al-Maktoum, Aisha Khalifa, Omar Farooq, Fatima Noor |
| Cayman Islands | KY | Alex Johnson, Brianna Clarke, Derek Walters |

Each jurisdiction starts at **v1** with foundational regulations and an original rulebook. Three new regulations are available to push per jurisdiction (up to v4).

---

## LLM Fallback Behavior

If the LLM API is unavailable or the API key is not configured:

| Agent | Fallback |
|-------|----------|
| Baseline Calculator | Simple mathematical averages computed locally |
| Anomaly Detector | Deterministic point-based scoring from the rulebook |
| Summarizer | Returns the regulation's existing summary text |
| Comparison Agent | Returns generic comparison points |
| Analyzer Agent | Returns a template-based impact analysis |
| Rulebook Editor | Adds a generic monitoring rule without full analysis |

The application never breaks — every LLM agent has a working fallback path.
