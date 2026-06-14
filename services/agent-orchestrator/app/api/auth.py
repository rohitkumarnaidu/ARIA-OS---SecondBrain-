from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.core.supabase import get_supabase_client
from config.core.config import settings

router = APIRouter()
security = HTTPBearer()

@router.post("/signup")
async def signup(email: str, password: str):
    supabase = get_supabase_client()
    try:
        user = supabase.auth.sign_up({"email": email, "password": password})
        return {"user": user.user, "session": user.session}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(email: str, password: str):
    supabase = get_supabase_client()
    try:
        session = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return {"user": session.user, "session": session.session}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/logout")
async def logout(token: str = Depends(security)):
    supabase = get_supabase_client()
    supabase.auth.sign_out()
    return {"message": "Logged out"}

@router.get("/me")
async def get_current_user_route(token: HTTPAuthorizationCredentials = Depends(security)):
    from config.core.auth import get_current_user as supabase_get_user
    try:
        user = await supabase_get_user(token.credentials)
        return {"user": user.user}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication")