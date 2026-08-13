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
  `hospital_c` — a logged-in Hospital A user can only ever read/write
  Hospital A's dataset (every route checks the session's hospital against
  the URL), and because IDs are looked up scoped to that hospital's
  dataset, guessing another hospital's ID doesn't leak anything either.
- **Data model** (see `bigquery/setup_bigquery.py` for exact schemas)
  mirrors a real patient visit — sign up → get admitted → get a room →
  receive treatment → get billed → get discharged → view it in the
  portal — as ten small tables per hospital:
  - Dimension-shaped (who/what): `users` (login), `patients`
    (demographics), `staff_profiles` (department/title), `rooms`
    (physical inventory, seeded), `hospital_info` (name/address/phone,
    one row, seeded)
  - Fact-shaped (events, insert-only): `encounters` (one row per
    admission/visit), `room_assignments`, `treatments`, `discharges`,
    `billing_charges` (auto-generated whenever an encounter is created, a
    room is assigned, or a treatment is added — see `add_charge` calls in
    `app/bigquery_client.py`)

  This is meant to be queried directly in BigQuery once there's enough
  data — e.g. join `rooms`/`room_assignments`/`discharges` for occupancy
  over time, `staff_profiles`/`encounters` for caseload by department, or
  `billing_charges` for revenue by hospital/charge type. Building the
  actual marts/views is a deliberate next step, not part of this app.

  **Nothing is ever updated in place**: BigQuery on this project's free
  tier rejects `UPDATE`, so instead of an `encounters.status` column,
  every state change (admit, assign a room, add a treatment, discharge)
  is its own new row, and "is this encounter still active" / "what room
  are they in now" / "what do they owe" are derived at query time from
  the latest rows (`app/bigquery_client.py`'s `_encounter_rows`,
  `get_current_room`, `list_available_rooms`,
  `list_charges_for_encounter`). The old `records` table from an earlier
  version of this app is unused now; it's still in BigQuery but nothing
  reads or writes it.

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
   only, not meant to reach production). It also seeds a `staff_profiles`
   row for the demo staff account.
6. Seed a handful of rooms per hospital so there's something to assign:
   ```bash
   python -m bigquery.seed_rooms
   ```
7. Seed each hospital's own info (name/address/phone):
   ```bash
   python -m bigquery.seed_hospital_info
   ```

## 3. Run locally

```bash
uvicorn app.main:app --reload --port 8080
```

Visit `http://localhost:8080`, pick a hospital, and log in with one of the
seeded demo accounts (or sign up — patients fill in demographics, staff
fill in department/title, at signup). As staff you can admit a patient
(creates an encounter), then from the encounter page assign/reassign a
room, add treatments, discharge them, and see the running bill for that
visit. As that patient, your portal shows every visit, the room you were
in, the treatments you received, and what you were billed.

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
  transactional database — no unique constraints (the signup email check
  and the insert aren't atomic, so two simultaneous signups with the same
  email could both slip through), and every write is a load job rather
  than a fast row insert. That's a deliberate workaround: both the
  streaming insert API and DML `INSERT` are rejected on GCP projects
  without billing enabled ("...not allowed in the free tier"), but load
  jobs are free-tier-safe. Load jobs are also quota-limited (~1,500 per
  table per day), which is plenty for a demo but not a real signup/write
  volume. If this grows past a handful of users, move `users`/`patients`
  to a real OLTP store (e.g. Cloud SQL) and keep BigQuery for the
  encounter/treatment/room history and analytics only — or enable billing
  on the project and switch back to DML/streaming.
- **No rate limiting or account lockout** on the login/signup endpoints.
- **Room double-booking is checked, not prevented**: two staff assigning
  the same room at nearly the same moment could both pass the
  availability check before either write lands (no unique constraint to
  fall back on). Fine at demo scale, worth a lock/queue if this became
  real.
- **`SESSION_SECRET_KEY` must be a real secret** in any deployed
  environment — never commit `.env` (already gitignored).
