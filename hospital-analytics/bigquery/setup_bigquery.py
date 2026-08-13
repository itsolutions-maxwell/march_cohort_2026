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
    bigquery.SchemaField("notes", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("administered_at", "TIMESTAMP", mode="REQUIRED"),
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

TABLES = (
    ("users", USERS_SCHEMA),
    ("patients", PATIENTS_SCHEMA),
    ("staff_profiles", STAFF_PROFILES_SCHEMA),
    ("hospital_info", HOSPITAL_INFO_SCHEMA),
    ("rooms", ROOMS_SCHEMA),
    ("encounters", ENCOUNTERS_SCHEMA),
    ("room_assignments", ROOM_ASSIGNMENTS_SCHEMA),
    ("treatments", TREATMENTS_SCHEMA),
    ("discharges", DISCHARGES_SCHEMA),
    ("billing_charges", BILLING_CHARGES_SCHEMA),
)


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


if __name__ == "__main__":
    main()
