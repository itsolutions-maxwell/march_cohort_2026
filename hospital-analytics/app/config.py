from pydantic_settings import BaseSettings, SettingsConfigDict

HOSPITALS = {
    "hospital_a": "Hospital A",
    "hospital_b": "Hospital B",
    "hospital_c": "Hospital C",
}

ENCOUNTER_TYPES = ["outpatient", "inpatient", "emergency"]
GENDER_OPTIONS = ["female", "male", "other", "prefer not to say"]
BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "unknown"]
DEPARTMENTS = [
    "General Medicine",
    "Emergency",
    "Cardiology",
    "Pediatrics",
    "Surgery",
    "Radiology",
]

# Flat demo billing rates — real pricing is out of scope, this just makes
# sure every capture action produces a billing line item to query later.
ADMISSION_FEES = {"outpatient": 150.00, "inpatient": 500.00, "emergency": 750.00}
ROOM_ASSIGNMENT_FEE = 200.00
TREATMENT_FEE = 75.00

# Lab/imaging categories get pending -> result tracking (test_completions);
# procedure/medication/other are logged as already-done when entered.
TEST_CATEGORIES = ["blood_work", "x_ray", "ct", "mri", "ultrasound", "pathology"]
TREATMENT_CATEGORIES = TEST_CATEGORIES + ["procedure", "medication", "other"]

PAYER_TYPES = ["insurance", "self_pay"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gcp_project_id: str = "your-gcp-project-id"
    session_secret_key: str = "change-me"


settings = Settings()
