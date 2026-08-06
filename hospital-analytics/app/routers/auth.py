from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.bigquery_client import get_user
from app.config import HOSPITALS
from app.security import verify_password
from app.templating import templates

router = APIRouter()


@router.post("/{hospital}/login")
def login(
    request: Request,
    hospital: str,
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
):
    if hospital not in HOSPITALS or role not in ("staff", "patient"):
        return RedirectResponse("/", status_code=303)

    user = get_user(hospital, email, role)
    if not user or not verify_password(password, user["password_hash"]):
        return templates.TemplateResponse(
            request,
            "login.html",
            {
                "hospital": hospital,
                "hospital_name": HOSPITALS[hospital],
                "error": "Invalid email or password.",
            },
            status_code=401,
        )

    request.session["user"] = {
        "user_id": user["user_id"],
        "email": user["email"],
        "role": user["role"],
        "hospital": hospital,
        "full_name": user["full_name"],
    }
    return RedirectResponse(f"/{hospital}/{role}/dashboard", status_code=303)


@router.post("/logout")
def logout(request: Request):
    hospital = (request.session.get("user") or {}).get("hospital", "")
    request.session.clear()
    return RedirectResponse(f"/{hospital}/login" if hospital else "/", status_code=303)
