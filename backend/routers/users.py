from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse

from backend.core.auth import COOKIE_NAME, read_session
from backend.services.users import (
    list_users,
    get_user_by_username,
    create_user,
    set_active,
    set_role,
    set_password,
    delete_user,
)

router = APIRouter(prefix="/api", tags=["users"])


def get_session(request: Request) -> dict | None:
    token = request.cookies.get(COOKIE_NAME)
    return read_session(token) if token else None


def require_session(request: Request) -> dict:
    s = get_session(request)
    if not s:
        raise HTTPException(status_code=401, detail="unauthorized")
    return s


def require_admin(request: Request) -> dict:
    s = require_session(request)
    if s.get("r") != "admin":
        raise HTTPException(status_code=403, detail="forbidden")
    return s


@router.get("/me")
def api_me(request: Request):
    s = require_session(request)
    return {"username": s["u"], "role": s["r"]}


@router.get("/users")
def api_list_users(request: Request):
    require_admin(request)
    return {"users": list_users()}


@router.post("/users")
def api_create_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form("viewer"),
):
    require_admin(request)

    username = username.strip()
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="username_too_short")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="password_too_short")
    if role not in {"admin", "viewer"}:
        raise HTTPException(status_code=400, detail="invalid_role")

    if get_user_by_username(username):
        raise HTTPException(status_code=400, detail="user_exists")

    create_user(username, password, role)
    return RedirectResponse("/users", status_code=302)


@router.post("/users/{username}/active")
def api_set_user_active(request: Request, username: str, active: int = Form(...)):
    admin = require_admin(request)

    if admin["u"] == username and active == 0:
        raise HTTPException(status_code=400, detail="cannot_disable_self")

    set_active(username, active == 1)
    return RedirectResponse("/users", status_code=302)


@router.post("/users/{username}/role")
def api_set_user_role(request: Request, username: str, role: str = Form(...)):
    admin = require_admin(request)

    if role not in {"admin", "viewer"}:
        raise HTTPException(status_code=400, detail="invalid_role")

    if admin["u"] == username and role != "admin":
        raise HTTPException(status_code=400, detail="cannot_demote_self")

    set_role(username, role)
    return RedirectResponse("/users", status_code=302)


@router.post("/users/{username}/password")
def api_reset_password(request: Request, username: str, password: str = Form(...)):
    require_admin(request)

    if len(password) < 6:
        raise HTTPException(status_code=400, detail="password_too_short")

    set_password(username, password)
    return RedirectResponse("/users", status_code=302)


@router.post("/users/{username}/delete")
def api_delete_user(request: Request, username: str):
    admin = require_admin(request)

    if admin["u"] == username:
        raise HTTPException(status_code=400, detail="cannot_delete_self")

    admins = [u for u in list_users() if u["role"] == "admin"]
    if len(admins) <= 1 and admins[0]["username"] == username:
        raise HTTPException(status_code=400, detail="cannot_delete_last_admin")

    delete_user(username)
    return RedirectResponse("/users", status_code=302)
