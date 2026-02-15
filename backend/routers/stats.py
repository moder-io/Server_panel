from fastapi import APIRouter, Request, HTTPException

from backend.core.auth import COOKIE_NAME, read_session
from backend.services.system import get_stats

router = APIRouter(prefix="/api", tags=["stats"])


def require_session(request: Request) -> dict:
    token = request.cookies.get(COOKIE_NAME)
    session = read_session(token) if token else None
    if not session:
        raise HTTPException(status_code=401, detail="unauthorized")
    return session


@router.get("/stats")
def api_stats(request: Request):
    require_session(request)
    return get_stats()
