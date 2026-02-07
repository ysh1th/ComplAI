# Deriv AI Compliance Manager — Project Blueprint

> Single source of truth for the complete project vision, architecture, and plan.
> Last updated: February 7, 2026

---

## 1. What It Is

A real-time compliance monitoring dashboard for Deriv that uses AI to do two things:

1. **Watch users** — detect when a customer's behavior deviates from their normal profile in ways that could signal money laundering, fraud, or regulatory violations.
2. **Watch regulations** — track evolving compliance laws across multiple jurisdictions and understand how new rules impact the business and its users.

The system operates across **three jurisdictions** where Deriv holds licenses:
- **Malta (MT)** — regulated by MFSA, governed by VFA Act
- **UAE (AE)** — regulated by VARA/DFSA, governed by CARF framework
- **Cayman Islands (KY)** — regulated by CIMA, governed by VASP Act

---

## 2. Who It's For

The end user is a **Compliance Officer** at Deriv. Someone who today manually reviews thousands of accounts, gets buried in false positives, and finds out about regulatory changes weeks too late. This tool gives them machine-scale monitoring with human-readable explanations.

---

## 3. The Domain

Scoped to **crypto trading compliance** — specifically:
- KYC validation
- Cross-border payment monitoring
- AML/CFT rules
- Tax reporting thresholds

**Demo user base:** 10 users, all 25 years old, spread across the three jurisdictions (~3-4 per jurisdiction).

---

## 4. The Two Halves of the System

The app has two main screens, each representing one half of the compliance problem.

---

### Screen 1: Live Monitor (Behavioral Intelligence)

The operational dashboard. The compliance officer opens this every day.

#### Left Panel — User Roster

A ranked list of all 10 user profiles, sorted by risk score (highest risk at top).

Each card shows:
- User's name
- Country flag (🇲🇹 / 🇦🇪 / 🇰🇾)
- Color-coded risk badge (RED / AMBER / GREEN / CLEAN)
- Numeric risk score (0–100)

When new data is injected and a user's score changes, their card:
- Flashes/pulses with a red border animation
- Smoothly re-sorts to its new position in the list

#### Right Panel — Intelligence Detail

When you click a user, you see their full intelligence profile:

**Header:**
- User's full name
- Jurisdiction badge
- KYC status indicator (verified / pending)
- **Animated Risk Gauge (0–100)** — semi-circular, color transitions green → amber → red

**Identity Card:**
- Age, Occupation, Income Level, Country
- Historical countries (flag icons)
- KYC status, Risk profile

**Behavioral Analysis — Statistical Brain:**
- Visual comparison: average tx amount vs current tx amount
- Average daily total vs today's total
- Normal tx frequency vs today's frequency
- Values exceeding thresholds (3×, 5×) turn red with warning indicators

**Behavioral Analysis — Physics Brain:**
- Last known location vs current transaction location
- Distance (km) and time elapsed
- If impossible travel detected (speed > 800 km/h): **"Physics Violation"** badge with plane icon

**AI Guardian (Anomaly Log):**
- Terminal-style dark box with monospace font
- Displays flagged rules and reasons in natural language
- Example: "⚠️ VARA Violation: User moved $55,000 (exceeds 5× baseline of $200) and jumped 5,000km from Dubai to Pyongyang in 1 hour. Impossible travel detected."
- Each entry has a timestamp and the specific regulation violated

#### Data Injection Flow

A bottom drawer / collapsible panel for manually injecting transaction batches.

Contains:
- **User selector** — dropdown to pick which user
- **Injection parameters** — transaction amount, country, currency, timestamp (maps to data headers)
- **"Inject Transaction Batch"** button — sends data through the full backend pipeline

The dashboard updates in real time after injection — card re-sorts, gauge animates, AI Guardian populates.

> In production, this injection point would be a real-time data feed (Kafka, webhooks). For the hackathon, it's manual injection.

---

### Screen 2: Regulatory Hub (Regulatory Intelligence)

The strategic compliance screen. Answers: "What laws apply to us, what's changed, and what does it mean?"

#### Background
Translucent black-and-white world map (opacity ~5–8%). When a jurisdiction tab is selected, the corresponding country subtly highlights.

#### Jurisdiction Tabs
Three tabs: **Malta** | **UAE** | **Cayman Islands**
Each tab has a small flag icon. Active tab gets a Deriv red underline.

#### Tab Content (per jurisdiction)

**Section A — Current Compliance Summary:**
- Brief overview of what regulations are currently active
- The "law of the land" right now

**Section B — Active Rulebook:**
Detailed rules the risk engine evaluates against, categorized:
- **Amount-based** (e.g., "Single tx > 5× user avg")
- **Frequency-based** (e.g., "4+ transactions in 15 minutes")
- **Location-based** (e.g., "Impossible geo hop")
- **Behavioral pattern** (e.g., "High volume inconsistent with declared income")

Each rule shows:
- Point value
- Specific Act referenced (VFA, VARA, CIMA) highlighted in **Deriv red**

**Section C — New Compliance Updates:**
- **"Fetch New Compliance"** button — pulls the next version as a draft
- New regulations appear as update cards showing:
  - Regulation ID, Title, Summary
  - Date effective
  - Impact on business model
  - Impact on user behaviors
  - Status: New / Reviewed / Applied

**Section D — Impact Analysis:**
- AI-generated summary of what the new compliance means
- Which existing rules are affected
- Suggested threshold changes (LLM/RAG integration point for later)

---

## 5. Compliance Versioning System

Regulations are not static. The system tracks them as **versioned snapshots**.

### Version Timeline (per jurisdiction)

```
Malta:  v1 (Nov 2018) ──●── v2 (Apr 2026) [ACTIVE] ──○── v3 (Draft)
UAE:    v1 (Oct 2020) ──●── v2 (Apr 2026) [ACTIVE] ──○── v3 (Draft)
Cayman: v1 (Jul 2020) ──●── v2 (Mar 2026) [ACTIVE] ──○── v3 (Draft)
```

### Version Statuses

| Status | Meaning |
|--------|---------|
| **archived** | Previously active, now superseded. Kept for history/audit. |
| **active** | Currently enforced. The rulebook the risk engine evaluates against. |
| **draft** | Fetched/detected but not yet applied. Pending review. |
| **rolled_back** | Was active, got intentionally reverted. |

### Version Data Structure (conceptual)

```json
{
  "jurisdiction": "Malta",
  "versions": [
    {
      "version": "v1",
      "status": "archived",
      "effective_date": "2018-11-01",
      "regulations": ["MT-OLD-001"],
      "rulebook": { "...v1 scoring rules..." }
    },
    {
      "version": "v2",
      "status": "active",
      "effective_date": "2026-04-10",
      "regulations": ["MT-REG-001", "MT-REG-002", "MT-REG-003"],
      "rulebook": { "...v2 scoring rules..." }
    }
  ],
  "active_version": "v2"
}
```

### Version Actions on Frontend

- **Fetch** — pull the next version as a draft
- **Apply** — promote a draft to active (risk engine now uses new rules)
- **Roll Back** — revert to previous version (marks current as rolled_back)
- **Compare** — side-by-side diff of any two versions

### Version History Log (audit trail)

```
[2026-04-10] v2 applied — 3 new regulations added (MT-REG-001, 002, 003)
[2018-11-01] v1 applied — Initial VFA Act framework
```

### Impact on Risk Engine

Changing the active version **re-evaluates all users** against the new rulebook. Users who were CLEAN under v1 might become MEDIUM under v2 because thresholds changed. This is a powerful demo moment.

---

## 6. The Risk Engine (Backend Pipeline)

Python FastAPI backend. When a transaction batch is injected via `POST /api/ingest-batch`:

### Step 1 — Context Loading
- Look up the user's jurisdiction
- Load the **active version** of that jurisdiction's rulebook

### Step 2 — Physics Check (Geolocation)
- Input: `distance_km`, `time_since_last_sec`
- Calculate: speed = distance_km / (time_since_last_sec / 3600)
- If speed > 800 km/h → **Impossible travel**
- Points: +60
- Log: "Impossible geo hop (proxy use detected)"

### Step 3 — Statistical Check (Baseline)
- Input: `transaction_amount_usd`, `avg_tx_amount_usd`
- If tx > 5× avg → +55 points
- If tx > 3× avg (but ≤5×) → +35 points
- Log: "Single tx > 5× avg (exceeds threshold)"

### Step 4 — Regulatory Check (Thresholds)
- Input: `daily_total_usd`, jurisdiction thresholds
- If daily total > regulatory limit → +30 points
- Check frequency bursts (≥4 tx in ≤15 min) → +35 points
- New country never seen before → +45 points
- Profile inconsistency (low income + high volume) → +35 points

### Step 5 — Aggregation
- **Total Score:** Sum of all points (capped at 100)
- **Risk Band:**
  - ≥75 → **HIGH** (Red) — alert with specific regulation cited
  - 50–74 → **MEDIUM** (Amber) — review needed
  - 25–49 → **LOW** (Green) — watch list
  - <25 → **CLEAN** (Grey) — no action
- **AI Summary:** Combine all log strings into a coherent natural language explanation

---

## 7. The Data That Flows Through the System

Seven data structures:

### A. Old Compliance (1 per jurisdiction)
Historical regulatory baseline.
- `regulation_update_id`, `update_title`, `summary`, `date_effective`

### B. New Compliance (3 per jurisdiction, versioned)
Evolving regulations with impact data.
- `regulation_update_id`, `update_title`, `summary`, `date_effective`
- `impact_on_business_model`, `impact_on_user_behaviors`

### C. User Bio/KYC (10 users)
Identity and profile data.
- `user_id`, `age`, `country`, `full_name`, `income_level`
- `occupation`, `kyc_status`, `risk_profile`, `historical_countries`

### D. User Baselines (10 users)
Historical behavioral averages.
- `user_id`, `avg_tx_amount_usd`, `avg_daily_total_usd`
- `avg_tx_per_day`, `std_dev_amount`, `normal_hour_range`

### E. Raw Transaction Batches (injected via Data Injection Flow)
What gets injected.
- `user_id`, `timestamp`, `transaction_amount_usd`
- `transaction_currency`, `transaction_type`
- `transaction_country`, `transaction_city`

### F. Preprocessed Transactions (enriched by backend)
Computed fields added by the pipeline.
- `hour_of_day`, `time_since_last_sec`, `previous_country`
- `distance_km`, `actual_travel_hours`
- `daily_total_usd`, `tx_count_per_day`, `is_new_country`

### G. Anomaly Flags/Logs (output)
What the risk engine returns.
- `user_id`, `timestamp`, `batch_date`
- `flagged_rule`, `risk_score`, `risk_band`, `reason`

---

## 8. API Endpoints (FastAPI)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/init` | Returns list of users + baselines |
| `GET` | `/api/rules/{jurisdiction}` | Returns the active version's rulebook for a jurisdiction |
| `GET` | `/api/compliance/{jurisdiction}` | Returns all compliance versions for a jurisdiction |
| `POST` | `/api/compliance/{jurisdiction}/fetch` | Fetches next compliance version as draft |
| `POST` | `/api/compliance/{jurisdiction}/apply` | Promotes draft to active |
| `POST` | `/api/compliance/{jurisdiction}/rollback` | Rolls back to previous version |
| `POST` | `/api/ingest-batch` | Injects transaction batch, returns risk score + logs |

---

## 9. Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 |
| Backend | Python FastAPI |
| Data | JSON files served via API (no database for MVP) |
| AI/LLM | LLM for natural language explanations + regulatory impact (RAG planned for later) |

---

## 10. Design System

| Element | Value |
|---------|-------|
| **Deriv Red** | `#FF444F` — HIGH risk, alerts, active states, regulation highlights |
| **Black** | `#0E0E0E` — dark mode background |
| **Teal** | `#00A79E` — LOW risk, safe states, success |
| **Amber** | `#F5A623` — MEDIUM risk |
| **Font** | Inter |
| **Modes** | Dark mode (default) + Light mode toggle |

---

## 11. App Structure

```
App
├── Sidebar Navigation
│   ├── Deriv Logo
│   ├── Live Monitor link
│   ├── Regulatory Hub link
│   └── Theme toggle (dark / light)
│
├── Screen 1: Live Monitor
│   ├── Left Panel: User Roster (10 users, sorted by risk score)
│   │   └── User Cards (avatar, name, flag, risk badge, score)
│   ├── Right Panel: Intelligence Detail
│   │   ├── Header (name, jurisdiction, KYC status, Risk Gauge 0–100)
│   │   ├── Identity Card (bio / KYC data)
│   │   ├── Behavioral Analysis
│   │   │   ├── Statistical Brain (baseline vs current comparisons)
│   │   │   └── Physics Brain (distance, time, impossible travel)
│   │   └── AI Guardian (anomaly log terminal)
│   └── Data Injection Flow (bottom drawer)
│       ├── User selector
│       ├── Injection parameters (amount, country, currency, etc.)
│       └── "Inject Transaction Batch" button
│
├── Screen 2: Regulatory Hub
│   ├── World Map Background (translucent, highlights active country)
│   ├── Jurisdiction Tabs (Malta | UAE | Cayman Islands)
│   └── Tab Content
│       ├── Version Timeline / Selector (v1 → v2 → v3...)
│       │   └── Actions: Fetch / Apply / Roll Back / Compare
│       ├── Current Compliance Summary
│       ├── Active Rulebook (categorized rules with point values)
│       ├── New Compliance Updates (fetch button + update cards)
│       ├── Impact Analysis (AI-generated summary)
│       └── Version History Log (audit trail)
```

---

## 12. The Demo Script

**Scenario:** Detect a "Sophisticated Layering Attack" involving impossible travel and VARA violations.

1. **Open Regulatory Hub.** Show Malta's compliance. "Here's our current v1 framework — the VFA Act from 2018."

2. **Fetch new compliance.** Click the button. Three new 2026 regulations appear as a v2 draft. "New regulations just detected."

3. **Apply the version.** Click "Apply". v2 is now active. "Our monitoring rules are updated to the latest VARA/DFSA/CARF requirements."

4. **Switch to Live Monitor.** "All 10 users are currently CLEAN or LOW risk under the new rules."

5. **Open Data Injection Flow.** Select Jane Smith (AE-USER-001, UAE). Set: $55,000 USDT, country: North Korea, 5,000 km from last location.

6. **Click "Inject Transaction Batch".** Watch:
   - Jane's card flashes red, jumps to position #1
   - Risk Gauge sweeps to 100
   - AI Guardian: "⚠️ VARA Violation: Impossible geo hop (5,000 km/1h) + Transaction 275× above baseline ($55,000 vs $200 avg). Flagged for VARA non-compliance and CARF reporting threshold breach."

7. **Closing statement:** "We didn't just flag a big number. We combined physics, user behavioral history, and the specific VARA regulations that came into effect minutes ago to identify a precise regulatory breach across jurisdictions."

---

## 13. What Makes This Stand Out

- **Dual-brain approach** — physics + statistics + jurisdiction-specific law, not static thresholds
- **Compliance versioning** — full audit trail, rollback capability, version comparison
- **The connection between both screens** — new regulations change what gets flagged (dynamic compliance)
- **Explainability** — every flag traces back to a specific law in a specific jurisdiction
- **Data Injection Flow** — live demo that shows the system reacting in real time
- **Professional UI** — Deriv-branded, dark/light mode, world map, animated risk gauges

---

## 14. Future Enhancements (Post-MVP)

- **RAG system** for ingesting raw regulatory documents and auto-generating compliance versions
- **Adaptive learning** — analyst feedback loop (mark false positives, system learns)
- **Network effects** — detecting linked behavior across multiple accounts
- **Predictive flagging** — early warning signals before breaches occur
- **Compliance calendar** — tracking implementation deadlines with proactive alerts
- **Impact simulation** — "This regulatory change will increase alerts by 15% in Malta"
