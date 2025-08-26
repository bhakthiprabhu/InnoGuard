import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import jwt

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXP_MINUTES = int(os.getenv("JWT_EXP_MINUTES", 60))

security = HTTPBearer()

def get_current_role(credentials=Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
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
    payload = {"role": role, "exp": datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
