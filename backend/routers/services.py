from fastapi import APIRouter, Request, HTTPException

from backend.core.auth import COOKIE_NAME, read_session
from backend.services.system import list_services, service_action

router = APIRouter(prefix="/api", tags=["services"])


def require_session(request: Request) -> dict:
    token = request.cookies.get(COOKIE_NAME)
    session = read_session(token) if token else None
    if not session:
        raise HTTPException(status_code=401, detail="unauthorized")
    return session


@router.get("/services")
def api_services(request: Request):
    require_session(request)
    return list_services()


@router.post("/services/{name}/{action}")
def api_service_action(name: str, action: str, request: Request):
    require_session(request)

    result = service_action(name, action)
    if not result.get("ok"):
        # esto lo verá como JSON en fetch(), y como HTML si abres en navegador
        raise HTTPException(status_code=400, detail=result.get("error") or "service_action_failed")
    return result
