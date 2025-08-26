from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils.auth import create_token
from routes.patients import router as patients_router

app = FastAPI(
    title="Privacy Gateway API",
    description="Role-aware Privacy-as-a-Service Gateway for hospital data",
    version="1.0.0"
)

# Health check
@app.get("/")
def health_check():
    return {"status": "ok", "message": "Privacy Gateway is running 🚀"}

# Register the router
app.include_router(patients_router, prefix="/patients", tags=["Patients"])

# ------------------------------
# Token generation endpoint (dev/testing only)
# ------------------------------
class TokenRequest(BaseModel):
    role: str  # Expected: "clinician", "researcher", or "developer"

@app.post("/token")
def generate_token(req: TokenRequest):
    """
    Generate a JWT token for testing purposes.
    """
    valid_roles = ["clinician", "researcher", "developer"]
    if req.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of {valid_roles}")

    try:
        token = create_token(req.role)
        return {"access_token": token, "token_type": "Bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token generation failed: {str(e)}")
