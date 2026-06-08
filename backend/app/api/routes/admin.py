from fastapi import APIRouter, Depends

from backend.app.security.dependencies import require_roles


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/health")
def admin_health(_context: tuple = Depends(require_roles("admin"))) -> dict[str, str]:
    return {"status": "ok", "scope": "admin"}
