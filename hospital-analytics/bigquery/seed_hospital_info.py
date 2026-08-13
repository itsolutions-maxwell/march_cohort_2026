"""
Seeds a single descriptive row per hospital (name/address/phone) into that
hospital's own dataset. Safe to re-run — skips a hospital that already has
a row.

Usage (from the hospital-analytics/ directory, after setup_bigquery.py):

    python -m bigquery.seed_hospital_info
"""

from app.bigquery_client import hospital_info_exists, insert_hospital_info
from app.config import HOSPITALS

# (address, phone) — synthetic demo data
DEMO_INFO = {
    "hospital_a": ("100 Main St, Springfield", "555-0100"),
    "hospital_b": ("200 Oak Ave, Springfield", "555-0200"),
    "hospital_c": ("300 Pine Rd, Springfield", "555-0300"),
}


def main() -> None:
    for hospital, name in HOSPITALS.items():
        if hospital_info_exists(hospital):
            print(f"Already exists: {name} ({hospital})")
            continue

        address, phone = DEMO_INFO[hospital]
        insert_hospital_info(hospital, hospital_id=hospital, name=name, address=address, phone=phone)
        print(f"Seeded: {name} ({hospital})")


if __name__ == "__main__":
    main()
