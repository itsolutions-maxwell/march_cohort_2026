from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.bigquery_client import (
    get_patient_profile,
    list_charges_for_encounter,
    list_encounters_for_patient,
    list_treatments_for_encounter,
)
from app.config import HOSPITALS
from app.deps import current_user_for
from app.templating import templates

router = APIRouter()


@router.get("/{hospital}/patient/dashboard")
def patient_dashboard(request: Request, hospital: str):
    user = current_user_for(request, hospital, "patient")
    if not user:
        return RedirectResponse(f"/{hospital}/login", status_code=303)

    encounters = list_encounters_for_patient(hospital, user["user_id"])
    for encounter in encounters:
        encounter["treatments"] = list_treatments_for_encounter(hospital, encounter["encounter_id"])
        encounter["charges"] = list_charges_for_encounter(hospital, encounter["encounter_id"])

    return templates.TemplateResponse(
        request,
        "patient_dashboard.html",
        {
            "hospital": hospital,
            "hospital_name": HOSPITALS[hospital],
            "user": user,
            "profile": get_patient_profile(hospital, user["user_id"]),
            "encounters": encounters,
        },
    )
