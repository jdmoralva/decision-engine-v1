from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.security.dependencies import require_permission


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/health")
def admin_health(_context: tuple = Depends(require_permission("administrar_usuarios"))) -> dict[str, str]:
    return {"status": "ok", "scope": "admin"}


@router.get("/rules")
def list_rules(_context: tuple = Depends(require_permission("administrar_reglas"))) -> dict[str, str]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Rule administration is not implemented yet.",
    )
