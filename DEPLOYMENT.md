# ComplAI Deployment Guide

Deploy the backend on **Railway** and the frontend on **Vercel**. Set up **Supabase** first so the backend has a database.

---

## Prerequisites

- GitHub repo with this codebase
- [Supabase](https://supabase.com) project (create one if needed)
- Google AI API key (for LLM)

---

## 0. Supabase setup

Do this before deploying the backend. The backend needs these tables and seed data to run.

### 0.1 Create a Supabase project

1. Go to [supabase.com](https://supabase.com) and sign in.
2. **New project** → choose org, name, database password, region.
3. Wait for the project to be ready.
4. In **Settings** → **API**: copy **Project URL** and **anon public** key. You will use these as `SUPABASE_URL` and `SUPABASE_KEY` in Railway and when running the seed script.

### 0.2 Create tables (run SQL migration)

1. In the Supabase dashboard, open **SQL Editor**.
2. Open the file **`backend/scripts/create_tables.sql`** from this repo and copy its full contents.
3. Paste into the SQL Editor and click **Run**.
4. Confirm there are no errors. This creates: `profiles`, `baselines`, `risk_state`, `transactions`, `compliance_state`, `rulebooks`, `new_regulations`, `compliance_drafts`, `agent_traces`, `agent_steps`.

### 0.3 Seed the database (run seed script)

The seed script reads from **`backend/data/`** and requires `SUPABASE_URL` and `SUPABASE_KEY`. Run it **once** from your machine (or any environment that has the repo and env vars).

1. From the **repo root**:
   ```bash
   cd backend
   ```
2. Create a **`.env`** in `backend/` with:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   ```
   Use the same URL and anon key from step 0.1.

3. Install dependencies and run the seed script:
   ```bash
   pip install -r requirements.txt
   python scripts/seed_supabase.py
   ```
   Or with a virtualenv:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate   # macOS/Linux
   pip install -r requirements.txt
   python scripts/seed_supabase.py
   ```

4. The script expects these files under **`backend/data/`** (they are in the repo):
   - `users.json` — user profiles
   - `baselines.json` — user baselines
   - `initial_risk_state.json` — optional; initial risk state
   - `historical_transactions.json` — optional; historical transactions
   - `compliance/malta.json`, `compliance/uae.json`, `compliance/cayman.json` — compliance state and rulebooks
   - `compliance/new_regulations/malta_v2.json`, `uae_v2.json`, `cayman_v2.json` — new regulations to push

   If a file is missing, the script skips that part and continues.

5. When it finishes, you should see messages like “Seeded N profiles”, “Seeded compliance state…”, etc. The app will then work with real data once the backend is deployed.

**Summary:** Run **`backend/scripts/create_tables.sql`** in the Supabase SQL Editor once, then run **`backend/scripts/seed_supabase.py`** once from your machine (with `backend/.env` set). After that, you only need to deploy Railway and Vercel; no need to run these again unless you reset the database.

---

## 1. Railway (Backend)

1. Go to [railway.app](https://railway.app) and sign in with GitHub.

2. **New Project** → **Deploy from GitHub repo** → select your ComplAI repo.

3. **Set root directory**  
   In the service: **Settings** → **Source** → **Root Directory** → set to `backend`.

4. **Environment variables**  
   In the service: **Variables** → add:

   | Variable       | Value                          |
   |----------------|--------------------------------|
   | `LLM_API_KEY`  | Your Google AI API key         |
   | `LLM_MODEL`    | `gemini-2.0-flash`             |
   | `LLM_BASE_URL` | `https://api.openai.com/v1`    |
   | `SUPABASE_URL` | Your Supabase project URL      |
   | `SUPABASE_KEY` | Your Supabase anon key         |
   | `FRONTEND_URL` | *(Set after Vercel deploy)*    |

5. **Deploy**  
   Railway uses Nixpacks, installs from `requirements.txt`, and runs the `Procfile`. `PORT` is set automatically.

6. **Public URL**  
   **Settings** → **Networking** → **Public Networking** → **Generate Domain**.  
   Copy the URL (e.g. `complai-backend-production.up.railway.app`). You will use it for the frontend and for `FRONTEND_URL` after Vercel is live.

---

## 2. Vercel (Frontend)

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub.

2. **Add New** → **Project** → import your ComplAI repo.

3. **Root Directory**  
   Set to `frontend` (or leave default and configure build to use `frontend`).

4. **Environment variables**  
   Add:

   | Variable                | Value                                      |
   |-------------------------|--------------------------------------------|
   | `NEXT_PUBLIC_API_URL`   | `https://<your-railway-domain>` (no slash) |

   Example: `https://complai-backend-production.up.railway.app`

5. **Deploy**  
   Vercel runs `next build` and deploys. Copy your Vercel URL (e.g. `https://complai.vercel.app`).

6. **CORS**  
   In Railway, set **Variables** → `FRONTEND_URL` to your Vercel URL (e.g. `https://complai.vercel.app`).  
   Redeploy the backend or wait for the next restart so CORS allows the frontend origin.

---

## 3. Recommended order

1. **Supabase:** Create project → run `backend/scripts/create_tables.sql` in SQL Editor → run `backend/scripts/seed_supabase.py` locally with `backend/.env` set.
2. Deploy backend on Railway (use same `SUPABASE_URL` and `SUPABASE_KEY`).
3. Copy Railway public URL.
4. Deploy frontend on Vercel with `NEXT_PUBLIC_API_URL` = Railway URL.
5. Copy Vercel URL.
6. In Railway, set `FRONTEND_URL` to Vercel URL and redeploy (or let it pick up on next deploy).

---

## 4. Post-deploy checks

- **Backend:** Open `https://<railway-domain>/api/health` — should return JSON with `"status": "ok"`.
- **Frontend:** Open your Vercel URL, go to Regulatory Hub, and confirm it loads compliance data (no CORS errors in the browser console).
- **Data:** If Regulatory Hub or Monitor show no data, ensure Supabase setup (section 0) was completed: tables created and `seed_supabase.py` run successfully.

---

## 5. Local development

- **Backend:** From repo root, `cd backend` then `uvicorn main:app --reload --port 8000`.  
  Use a `.env` in `backend/` (see `backend/.env.example`).

- **Frontend:** From repo root, `cd frontend` then `npm run dev`.  
  Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local` (or leave unset to default to localhost).
