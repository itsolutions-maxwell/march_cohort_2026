"""
Creates the BigQuery datasets and tables this app needs, one dataset per
hospital. Safe to re-run — every create call skips existing datasets/tables.

Usage (from the hospital-analytics/ directory, with GCP credentials
available via `gcloud auth application-default login` or
GOOGLE_APPLICATION_CREDENTIALS):

    python -m bigquery.setup_bigquery
"""

from google.cloud import bigquery

from app.config import HOSPITALS, settings

USERS_SCHEMA = [
    bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("password_hash", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("role", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("full_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]

PATIENTS_SCHEMA = [
    bigquery.SchemaField("patient_user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("date_of_birth", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("gender", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("phone", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("blood_type", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("payer_type", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]

STAFF_PROFILES_SCHEMA = [
    bigquery.SchemaField("staff_user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("department", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]

HOSPITAL_INFO_SCHEMA = [
    bigquery.SchemaField("hospital_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("address", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("phone", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]

ROOMS_SCHEMA = [
    bigquery.SchemaField("room_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("room_number", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("room_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("floor", "INT64", mode="REQUIRED"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]

ENCOUNTERS_SCHEMA = [
    bigquery.SchemaField("encounter_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("patient_user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("attending_staff_user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("encounter_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("reason", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("department", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("expected_discharge_date", "DATE", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]

ROOM_ASSIGNMENTS_SCHEMA = [
    bigquery.SchemaField("assignment_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("encounter_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("room_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("staff_user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("assigned_at", "TIMESTAMP", mode="REQUIRED"),
]

TREATMENTS_SCHEMA = [
    bigquery.SchemaField("treatment_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("encounter_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("staff_user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("treatment_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("category", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("notes", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("administered_at", "TIMESTAMP", mode="REQUIRED"),
]

TEST_COMPLETIONS_SCHEMA = [
    bigquery.SchemaField("test_completion_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("treatment_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("staff_user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("result_notes", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("completed_at", "TIMESTAMP", mode="REQUIRED"),
]

DISCHARGES_SCHEMA = [
    bigquery.SchemaField("discharge_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("encounter_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("staff_user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("discharge_notes", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("discharged_at", "TIMESTAMP", mode="REQUIRED"),
]

BILLING_CHARGES_SCHEMA = [
    bigquery.SchemaField("charge_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("encounter_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("patient_user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("charge_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("amount", "NUMERIC", mode="REQUIRED"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]

PAYMENTS_SCHEMA = [
    bigquery.SchemaField("payment_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("encounter_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("patient_user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("amount", "NUMERIC", mode="REQUIRED"),
    bigquery.SchemaField("paid_at", "TIMESTAMP", mode="REQUIRED"),
]

TABLES = (
    ("users", USERS_SCHEMA),
    ("patients", PATIENTS_SCHEMA),
    ("staff_profiles", STAFF_PROFILES_SCHEMA),
    ("hospital_info", HOSPITAL_INFO_SCHEMA),
    ("rooms", ROOMS_SCHEMA),
    ("encounters", ENCOUNTERS_SCHEMA),
    ("room_assignments", ROOM_ASSIGNMENTS_SCHEMA),
    ("treatments", TREATMENTS_SCHEMA),
    ("test_completions", TEST_COMPLETIONS_SCHEMA),
    ("discharges", DISCHARGES_SCHEMA),
    ("billing_charges", BILLING_CHARGES_SCHEMA),
    ("payments", PAYMENTS_SCHEMA),
)

# Columns added to tables that already existed (and already have data) before
# this revision. create_table(exists_ok=True) won't add columns to a table
# that's already there, so these run as an explicit ALTER TABLE migration —
# DDL, unaffected by the free-tier block on DML/streaming inserts.
COLUMN_MIGRATIONS = {
    "encounters": [("department", "STRING"), ("expected_discharge_date", "DATE")],
    "treatments": [("category", "STRING")],
    "patients": [("payer_type", "STRING")],
}


def ensure_columns(client: bigquery.Client) -> None:
    for hospital in HOSPITALS:
        for table_name, columns in COLUMN_MIGRATIONS.items():
            table_id = f"{settings.gcp_project_id}.{hospital}.{table_name}"
            add_clauses = ", ".join(f"ADD COLUMN IF NOT EXISTS {name} {col_type}" for name, col_type in columns)
            client.query(f"ALTER TABLE `{table_id}` {add_clauses}").result()
            print(f"  Columns ensured: {table_id}")


def main() -> None:
    client = bigquery.Client(project=settings.gcp_project_id)

    for hospital in HOSPITALS:
        dataset_id = f"{settings.gcp_project_id}.{hospital}"
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"
        client.create_dataset(dataset, exists_ok=True)
        print(f"Dataset ready: {dataset_id}")

        for table_name, schema in TABLES:
            table_id = f"{dataset_id}.{table_name}"
            table = bigquery.Table(table_id, schema=schema)
            client.create_table(table, exists_ok=True)
            print(f"  Table ready: {table_id}")

    print("Migrating existing tables to the latest columns:")
    ensure_columns(client)


if __name__ == "__main__":
    main()
