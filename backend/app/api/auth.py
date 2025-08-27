from fastapi import APIRouter, HTTPException
from core.security import create_token
from .schemas import TokenRequest, TokenResponse

router = APIRouter()

@router.post("/token", response_model=TokenResponse, tags=["Auth"])
def generate_token(req: TokenRequest):
    """
    Generate a JWT token for testing purposes.
    """
    try:
        token = create_token(req.role)
        return {"access_token": token}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token generation failed: {str(e)}")
