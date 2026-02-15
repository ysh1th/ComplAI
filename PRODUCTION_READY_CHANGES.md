## Production ready architecture (Changes Only)

Here are the specific additions and changes needed to move the agentic architecture to a production-ready state:

### 1. Robust Output Guardrails (The Pydantic Retry Loop)

The current MVP assumes the LLM always returns valid JSON. In production, you need a **Self-Correction Wrapper** for every agent call:

- **Validation Wrapper:** Wrap all call_llm functions in a loop (max 3 attempts). If Pydantic.ValidationError is caught, the system automatically triggers a retry.
- **Error-Feedback Prompting:** The retry prompt must include the specific error message from Pydantic (e.g., *"Field 'risk_score' expected int, got string 'high'"*). This gives the LLM the context needed to fix its own mistake.
- **Deterministic Fallback:** After the 3rd failed attempt, the agent must bypass the LLM and return a "Safe Default" object to prevent the entire UI from crashing.

### 2. Logic Guardrail: The Anomaly Validator Agent

This is a "Quality Control" agent added to **Workflow 1** (Transaction Analysis):

- **Cross-Examination:** Once the *Anomaly Detector Agent* makes a decision, the *Validator Agent* reviews the output. It checks: *"Does the reasoning actually support the risk score provided?"* and *"Are the cited regulations actually relevant to the detected flags?"*
- **Re-Invocation Loop:** If the Validator finds a logical contradiction (e.g., reasoning says "no issues" but risk score is 90), it sends the task back to the *Anomaly Detector* with a "Criticism" prompt to force a re-evaluation.

### 3. Rulebook Integrity Guardrails (Specific to Agent 8)

Since the *Rulebook Editor Agent* is the only one that modifies your "System of Record," it needs the strictest constraints:

- **Structural Template Matching:** A hard check to ensure no top-level JSON keys (e.g., amount_based, location_based) were deleted or renamed during the edit.
- **Value Bounding:** Deterministic Python checks to ensure any new points assigned to a rule fall within a "Sane Range" (e.g., 0–50). If the LLM tries to assign 1,000 points to a rule, the backend must reject it.
- a template should be used by both `rule book editor`  `validator` agents to output the rule book and be checked whether the points generated are valid
- **Jurisdiction Sanitization:** A check to ensure the agent hasn't hallucinated rules for jurisdictions not present in your jurisdiction_code enum (MT, AE, KY).

### 4. Human-in-the-Loop (HITL) State Management

You must move away from the "Direct Write" model to a **Draft/Live State Machine** in Supabase:

- **The "Pending" Table:** When the *Rulebook Editor* finishes its work, it writes to a rulebook_drafts table instead of the main rulebook.
- **Stateful UI Actions:** The Frontend fetches this draft and displays it in the RulebookDiff.tsx component. The "Push" button is replaced by two actions for the Compliance Officer: **[Approve]** or **[Edit/Reject]**.
- **Promotion Logic:** Only upon a manual "Approve" click does the backend move the JSON from the drafts table to the active_rulebook table and increment the version_label.

### 5. Transition to Persistent Data (Supabase + Realtime)

JSON files are no longer viable for production state management:

- **Relational Migration:** Migrate users.json, baselines.json, historical transactions, risk state logs, agent outputs into Supabase tables. This allows for **Audit Logging** (e.g., "Show me all transactions for User X that were flagged as HIGH risk in the last 30 days").
- **Realtime WebSocket Layer:** Use Supabase Realtime to broadcast agent progress. Instead of the frontend waiting for one giant HTTP response, it can listen for "Agent Finished" events, allowing the AgentChainLog.tsx to update step-by-step as each agent completes its task on Railway.
- design schema based on the specified requirements and the application structure. a sample schema i have in my mind, but you can design or make changes to the structure based on the application:

**Table Structure:**

- **profiles**: Stores the core user data (Age, Country, Income, KYC Status).
- **baselines**: Linked via user_id. Stores the "Average Transaction Amount," "Typical Hours," etc. (This table gets updated every time the *Baseline Agent* runs).
- **transactions**: Stores the raw and preprocessed transaction history. Every row links back to a user_id.
- **agent_traces**: This is where you store the **Agent Outputs**. Each row represents one full "run" (e.g., one Data Injection batch).
- **agent_steps**: A child table of agent_traces. It stores the individual output for each agent (*Profile, Preprocessor, Detector, Validator*), including the duration, status, and **retry count** (your loop counter).
- **rulebooks**: Stores the different versions of the rulebook (v1, v2) as JSONB columns.
- **compliance_drafts**: Stores the "Pending Review" rulebooks for the Human-in-the-Loop workflow.

### 6. Async Background Processing (Railway Workers)

To prevent timeout issues during long LLM chains:

- **Task Queuing:** The API should receive the request, trigger the agentic workflow as a background task on Railway, and return a job_id to the frontend.
- **Background Workers:** Use a Python task queue (e.g., Arq or RQ) with Railway Redis as the broker.
- **Long-Polling/Sockets:** The frontend uses the job_id to track the "Dual Brain" progress without keeping a single HTTP connection open for 30+ seconds.

---

## UI/UX changes based on Guardrails

Here is how you can plan the frontend visualization for the **Anomaly-Validator Loop** and **Guardrail Retries**:

### 1. The "Iteration Badge" (Your Idea)

To keep the UI clean but informative, use a "Retry Counter" badge next to the agent name in the AgentChainLog.tsx.

- **Visual State:** If an agent succeeds on the first try, no badge is shown.
- **Loop State:** If the Validator sends it back, a small amber circular badge appears (e.g., x2 or +1).
- **Interaction:** Clicking that badge could expand a "Refinement History" that shows exactly what the Validator disliked about the first version (e.g., *"Missing reasoning for high transaction frequency"*).

### 2. The "Self-Correction" Status Indicator

While the loop is happening in the backend, the frontend should show the current "sub-step" of the loop:

- **Phase 1:** "Anomaly Detector: Initializing reasoning..."
- **Phase 2:** "Anomaly Detector: Validating output against guardrails..."
- **Phase 3 (If failed):** "Anomaly Detector: Correcting structural errors (Attempt 2)..."
- **Phase 4 (Validator Check):** "Anomaly Validator: Reviewing logic for consistency..."
- **Final Phase:** "Validated & Complete."

### 3. Distinguishing Technical vs. Logical Retries

You have two types of loops. It helps the user to see which one is happening:

- **Technical Retry (Pydantic/JSON Guardrail):** Use a "wrench" icon or "Technical Fix" label. This tells the user: *"The AI messed up the formatting, but the system caught it."*
- **Logical Retry (Anomaly Validator):** Use a "shield" or "Logic Review" label. This tells the user: *"The AI made a decision, but a second AI checked its homework and asked for more detail."*

### 4. Nested Iteration Logs (The "Audit Trail" View)

Instead of overwriting the previous attempt, the AgentChainLog can treat the loop as a **nested list**:

- **[+] Anomaly Detector (Final Success)**
    - *Hidden by default, expandable:*
    - Attempt 1: [Failed Logic Check] -> "Reason: Risk score too high for low-value tx."
    - Attempt 2: [Passed Guardrails] -> "Self-corrected reasoning."
- This is extremely valuable for "Explanability" (XAI). It proves to auditors that the system has internal checks and balances.

### 5. Color-Coded "Pulse" for Active Loops

Since you are using Railway and Supabase Realtime:

- While the Detector and Validator are "arguing" (looping), the agent card in the sidebar or the log entry can have an **Amber Pulse**.
- If it succeeds after a loop, it turns **Green**.
- If it exhausts all 3 retries and fails, it turns **Red** and shows a "System Intervention Required" message.

### 6. The "Refinement Message"

In the terminal-style box where you show the Reasoning, you can add a small footer:

> *"Analysis refined 2 times by the Internal Validator to ensure regulatory accuracy."*
> 

### Why this matters for your specific project:

Since this is for **Compliance Officers**, they are used to "re-working" cases. Seeing the AI perform a **"Validator Loop"** mimics the human process of a Junior Analyst sending a report to a Senior Manager for review. It makes the "Dual Brain" concept feel tangible.