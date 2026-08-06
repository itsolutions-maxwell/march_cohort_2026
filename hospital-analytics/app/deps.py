from fastapi import Request


def current_user_for(request: Request, hospital: str, role: str) -> dict | None:
    """Returns the logged-in user only if their session matches this hospital + role."""
    user = request.session.get("user")
    if not user or user.get("hospital") != hospital or user.get("role") != role:
        return None
    return user
