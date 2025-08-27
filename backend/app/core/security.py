from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import jwt
from datetime import datetime, timedelta
from core.config import settings

security = HTTPBearer()

def get_current_role(credentials=Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        role = payload.get("role")
        if not role:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Role missing")
        return role
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def create_token(role: str):
    if role not in ["clinician", "researcher", "developer"]:
        raise ValueError("Invalid role")
    payload = {"role": role, "exp": datetime.utcnow() + timedelta(minutes=settings.JWT_EXP_MINUTES)}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
