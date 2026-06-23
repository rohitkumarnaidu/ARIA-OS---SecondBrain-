from fastapi import APIRouter, Depends, HTTPException, Body
from config.core.auth import get_current_user, rotate_api_key, refresh_jwt_token
from shared.utils.logger import logger

router = APIRouter()


@router.post("/rotate-key", summary="Rotate API key")
async def rotate_key(current_user=Depends(get_current_user)):
    user_id = getattr(current_user, "id", None) or getattr(current_user.user, "id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Could not identify user")

    try:
        result = rotate_api_key(user_id)
        logger.info("API key rotated", user_id=user_id)
        return result
    except Exception as e:
        logger.error("API key rotation failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to rotate API key")


@router.post("/refresh", summary="Refresh JWT token")
async def refresh_token(refresh_token: str = Body(..., embed=True)):
    try:
        return refresh_jwt_token(refresh_token)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to refresh token")
