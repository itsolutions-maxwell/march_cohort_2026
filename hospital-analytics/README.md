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
  portal — as eleven small tables per hospital:
  - Dimension-shaped (who/what): `users` (login), `patients`
    (demographics + `payer_type`), `staff_profiles` (department/title),
    `rooms` (physical inventory, seeded — `general`/`private`/
    `semi_private`/`icu`/`er`/`operating_room`), `hospital_info`
    (name/address/phone, one row, seeded)
  - Fact-shaped (events, insert-only): `encounters` (one row per
    admission/visit — `department`, `expected_discharge_date`),
    `room_assignments`, `treatments` (`category` — lab/imaging/pathology
    types get pending → result tracking), `test_completions` (the
    "result" event for a pending treatment), `discharges`,
    `billing_charges` (auto-generated whenever an encounter is created, a
    room is assigned, or a treatment is added — see `add_charge` calls in
    `app/bigquery_client.py`), `payments` (recorded against an encounter's
    bill; outstanding = charged − paid)

  **Nothing is ever updated in place**: BigQuery on this project's free
  tier rejects `UPDATE`, so instead of an `encounters.status` column,
  every state change (admit, assign a room, add a treatment, complete a
  test, record a payment, discharge) is its own new row, and "is this
  encounter still active" / "what room are they in now" / "what do they
  owe" are derived at query time from the latest rows
  (`app/bigquery_client.py`'s `_encounter_rows`, `get_current_room`,
  `list_available_rooms`, `list_charges_for_encounter`). The old `records`
  table from an earlier version of this app is unused now; it's still in
  BigQuery but nothing reads or writes it.

## Medallion architecture: raw → silver → gold

The per-hospital tables above are the **bronze** layer — exactly what the
app writes, one dataset per hospital, never cross-referenced. On top of
that, `bigquery/sql_queries/` holds hand-run SQL (not app code — you run
these yourself, in BigQuery, as a teaching exercise in the medallion
pattern) that builds three more datasets:

- **`raw/`** — one view per bronze table, per-view UNION ALL of
  `hospital_a`/`hospital_b`/`hospital_c` tagged with `hospital_id`. No
  cleaning, no dedup, no null handling — it's exactly what's in the source
  tables, combined.
- **`silver/`** — cleaned and conformed. `silver/01_users.sql` is the one
  to read first: it drops junk rows, normalizes email, dedupes on
  `(hospital, email)`, and splits `full_name` into `first_name`/
  `last_name` (there's no separate name column anywhere upstream — this is
  silver *adding* structure raw never had). `silver/05_encounters.sql` is
  the other important one: it resolves "current room" and "is discharged"
  from the raw event log, the same way `_encounter_rows` does in Python,
  but as SQL every other view can reuse.
  `silver/08_data_quality_duplicate_patients.sql` is a fixed, all-three-
  hospitals version of the `duplicate_patients.sql` query already in this
  folder (the original only checked `hospital_a`/`hospital_b` —
  `hospital_c` was missing) — it flags patients with the same name at more
  than one hospital for review; it doesn't merge or delete anything, since
  there's no way to be sure from a name alone that two rows are the same
  person.
- **`gold/`** — dashboard-ready facts/dims built on silver:
  `dim_hospital`, `fact_bed_occupancy`, `fact_encounters`,
  `fact_billing`, `fact_receivables` (charged vs. paid vs. outstanding,
  per encounter), `fact_tests` (pending/completed, turnaround time).

Everything is a `CREATE OR REPLACE VIEW`, not a materialized table — zero
storage cost, always reflects live bronze data, no refresh job to manage.
Run them in order, once. Paste them into the BigQuery console by hand if
you want to read each one as you go (this is a teaching exercise, after
all) — or run a whole folder at once with `bigquery/run_sql_folder.py`,
which just executes every `.sql` file in a folder, in filename order (so
the `01_`, `02_`, ... numbering matters — `silver/05_encounters.sql`
depends on `silver/02`/`03` already existing):

```bash
# One-time: paste 00_create_datasets.sql into the BigQuery console (or
# run it with the bq CLI) to create the raw/silver/gold datasets.

python -m bigquery.run_sql_folder raw
python -m bigquery.run_sql_folder silver
python -m bigquery.run_sql_folder gold
```

Re-run any of them any time after a schema change — every file is
`CREATE OR REPLACE VIEW`, so it's always safe to re-run.

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
- **The seeded demo patients (`bigquery/seed_users.py`) have a login but
  no `patients` profile row** — they predate that table. `silver.patients`
  (an inner join to `raw.patients`) correctly excludes them, so they won't
  show up in patient-scoped gold views. Sign up a fresh patient through
  the app to get one with a full profile.
- **`SESSION_SECRET_KEY` must be a real secret** in any deployed
  environment — never commit `.env` (already gitignored).
