import uuid

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.bigquery_client import email_exists_in_hospital, get_user, insert_user
from app.config import HOSPITALS
from app.security import hash_password, verify_password
from app.templating import templates

router = APIRouter()

MIN_PASSWORD_LENGTH = 8


def _session_user(user_id: str, email: str, role: str, hospital: str, full_name: str) -> dict:
    return {
        "user_id": user_id,
        "email": email,
        "role": role,
        "hospital": hospital,
        "full_name": full_name,
    }


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

    request.session["user"] = _session_user(
        user["user_id"], user["email"], user["role"], hospital, user["full_name"]
    )
    return RedirectResponse(f"/{hospital}/{role}/dashboard", status_code=303)


@router.get("/{hospital}/signup")
def signup_page(request: Request, hospital: str):
    if hospital not in HOSPITALS:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        request,
        "signup.html",
        {"hospital": hospital, "hospital_name": HOSPITALS[hospital], "error": None},
    )


@router.post("/{hospital}/signup")
def signup(
    request: Request,
    hospital: str,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
):
    if hospital not in HOSPITALS or role not in ("staff", "patient"):
        return RedirectResponse("/", status_code=303)

    error = None
    if len(password) < MIN_PASSWORD_LENGTH:
        error = f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    elif email_exists_in_hospital(hospital, email):
        error = f"An account with {email} already exists at {HOSPITALS[hospital]}."

    if error:
        return templates.TemplateResponse(
            request,
            "signup.html",
            {"hospital": hospital, "hospital_name": HOSPITALS[hospital], "error": error},
            status_code=400,
        )

    user_id = str(uuid.uuid4())
    insert_user(
        hospital,
        user_id=user_id,
        email=email,
        password_hash=hash_password(password),
        role=role,
        full_name=full_name,
    )

    request.session["user"] = _session_user(user_id, email, role, hospital, full_name)
    return RedirectResponse(f"/{hospital}/{role}/dashboard", status_code=303)


@router.post("/logout")
def logout(request: Request):
    hospital = (request.session.get("user") or {}).get("hospital", "")
    request.session.clear()
    return RedirectResponse(f"/{hospital}/login" if hospital else "/", status_code=303)
