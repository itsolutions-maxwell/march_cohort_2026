"""
Inserts one demo staff account and one demo patient account into every
hospital dataset, so there's something to log in with right after setup.
Safe to re-run — it checks for an existing email+role before inserting.

Usage (from the hospital-analytics/ directory, after setup_bigquery.py):

    python -m bigquery.seed_users
"""

import uuid

from app.bigquery_client import get_user, insert_user
from app.config import HOSPITALS
from app.security import hash_password

DEMO_PASSWORD = "changeme123"


def seed_user(hospital: str, email: str, role: str, full_name: str) -> None:
    if get_user(hospital, email, role):
        print(f"  Already exists: {email} ({role}) in {hospital}")
        return

    insert_user(
        hospital,
        user_id=str(uuid.uuid4()),
        email=email,
        password_hash=hash_password(DEMO_PASSWORD),
        role=role,
        full_name=full_name,
    )
    print(f"  Seeded: {email} ({role}) in {hospital} — password: {DEMO_PASSWORD}")


def main() -> None:
    for hospital, name in HOSPITALS.items():
        print(f"{name} ({hospital}):")
        seed_user(hospital, f"staff@{hospital}.demo", "staff", f"{name} Staff Demo")
        seed_user(hospital, f"patient@{hospital}.demo", "patient", f"{name} Patient Demo")


if __name__ == "__main__":
    main()
