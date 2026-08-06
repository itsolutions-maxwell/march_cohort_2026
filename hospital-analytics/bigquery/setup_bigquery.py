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

RECORDS_SCHEMA = [
    bigquery.SchemaField("record_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("patient_user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("staff_user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("record_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("note", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]


def main() -> None:
    client = bigquery.Client(project=settings.gcp_project_id)

    for hospital in HOSPITALS:
        dataset_id = f"{settings.gcp_project_id}.{hospital}"
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"
        client.create_dataset(dataset, exists_ok=True)
        print(f"Dataset ready: {dataset_id}")

        for table_name, schema in (("users", USERS_SCHEMA), ("records", RECORDS_SCHEMA)):
            table_id = f"{dataset_id}.{table_name}"
            table = bigquery.Table(table_id, schema=schema)
            client.create_table(table, exists_ok=True)
            print(f"  Table ready: {table_id}")


if __name__ == "__main__":
    main()
