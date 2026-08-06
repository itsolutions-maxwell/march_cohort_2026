"""
Inserts one demo staff account and one demo patient account into every
hospital dataset, so there's something to log in with right after setup.
Safe to re-run — it checks for an existing email+role before inserting.

Usage (from the hospital-analytics/ directory, after setup_bigquery.py):

    python -m bigquery.seed_users
"""

import uuid
from datetime import datetime, timezone

from app.bigquery_client import get_user, get_client
from app.config import HOSPITALS, settings
from app.security import hash_password

DEMO_PASSWORD = "changeme123"


def seed_user(hospital: str, email: str, role: str, full_name: str) -> None:
    if get_user(hospital, email, role):
        print(f"  Already exists: {email} ({role}) in {hospital}")
        return

    client = get_client()
    table = f"{settings.gcp_project_id}.{hospital}.users"
    row = {
        "user_id": str(uuid.uuid4()),
        "email": email,
        "password_hash": hash_password(DEMO_PASSWORD),
        "role": role,
        "full_name": full_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    errors = client.insert_rows_json(table, [row])
    if errors:
        raise RuntimeError(f"Failed to seed {email}: {errors}")
    print(f"  Seeded: {email} ({role}) in {hospital} — password: {DEMO_PASSWORD}")


def main() -> None:
    for hospital, name in HOSPITALS.items():
        print(f"{name} ({hospital}):")
        seed_user(hospital, f"staff@{hospital}.demo", "staff", f"{name} Staff Demo")
        seed_user(hospital, f"patient@{hospital}.demo", "patient", f"{name} Patient Demo")


if __name__ == "__main__":
    main()
