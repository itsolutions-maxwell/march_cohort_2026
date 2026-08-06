from pydantic_settings import BaseSettings, SettingsConfigDict

HOSPITALS = {
    "hospital_a": "Hospital A",
    "hospital_b": "Hospital B",
    "hospital_c": "Hospital C",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gcp_project_id: str = "your-gcp-project-id"
    session_secret_key: str = "change-me"


settings = Settings()
