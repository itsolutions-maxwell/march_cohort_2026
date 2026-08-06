# Hospital Analytics

A FastAPI app for three hospitals (A, B, C). Staff and patients each log in
with email/password to their own hospital, and every read/write goes
straight to BigQuery — one dataset per hospital, no other datastore.

## How it's built

- **Everything is FastAPI.** The UI is server-rendered Jinja2 templates
  (`app/templates/`); there's no separate frontend build.
- **Auth** is real email + password, hashed with `bcrypt`. Sessions are a
  signed cookie (`starlette.middleware.sessions`) — no server-side session
  store needed.
- **Data isolation**: BigQuery datasets `hospital_a`, `hospital_b`,
  `hospital_c`, each with a `users` table and a `records` table (see
  `bigquery/setup_bigquery.py` for the schema). A logged-in Hospital A user
  can only ever read/write Hospital A's dataset — every route checks the
  session's hospital against the URL.

## 1. Local setup

```bash
cd hospital-analytics
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in GCP_PROJECT_ID and SESSION_SECRET_KEY
```

Generate a session secret:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 2. GCP / BigQuery setup (one-time, needs your own GCP project)

1. Create (or pick) a GCP project and note its project ID.
2. Enable the BigQuery API: `gcloud services enable bigquery.googleapis.com --project YOUR_PROJECT_ID`
3. Authenticate locally so the app can reach BigQuery with your user credentials:
   `gcloud auth application-default login`
   (Alternative: create a service account with `BigQuery Data Editor` +
   `BigQuery Job User`, download a key, and point
   `GOOGLE_APPLICATION_CREDENTIALS` at it in `.env`.)
4. Create the datasets and tables:
   ```bash
   python -m bigquery.setup_bigquery
   ```
5. Seed a demo staff + patient account per hospital so you have something
   to log in with:
   ```bash
   python -m bigquery.seed_users
   ```
   This prints each seeded email; the shared demo password is
   `changeme123` (change it — this is a placeholder for local testing
   only, not meant to reach production).

## 3. Run locally

```bash
uvicorn app.main:app --reload --port 8080
```

Visit `http://localhost:8080`, pick a hospital, and log in with one of the
seeded demo accounts. As staff you can capture a record for any patient at
that hospital (by email); as that patient you'll see it on your dashboard.

## 4. Deploy to Cloud Run

```bash
gcloud run deploy hospital-analytics \
  --source . \
  --project YOUR_PROJECT_ID \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=YOUR_PROJECT_ID,SESSION_SECRET_KEY=YOUR_SECRET
```

The Cloud Run service's runtime service account needs `BigQuery Data
Editor` + `BigQuery Job User` on the project (Application Default
Credentials pick it up automatically — no key file needed in prod).

## Known limitations (this is a starting skeleton, not production-ready)

- **BigQuery as an auth store**: BigQuery is an analytics warehouse, not a
  transactional database — no unique constraints, and streaming inserts
  have a short visibility delay. Fine at demo scale; if this grows past a
  handful of users, move `users` to a real OLTP store (e.g. Cloud SQL) and
  keep BigQuery for `records`/analytics only.
- **No self-registration** — accounts are seeded manually via
  `bigquery/seed_users.py`. Add a signup flow before giving this to real
  users.
- **No rate limiting or account lockout** on the login endpoint.
- **`SESSION_SECRET_KEY` must be a real secret** in any deployed
  environment — never commit `.env` (already gitignored).
