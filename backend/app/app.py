from fastapi import FastAPI
from api.v1 import patients, auth

app = FastAPI(
    title="Privacy Gateway API",
    description="Role-aware Privacy-as-a-Service Gateway for hospital data",
    version="1.0.0"
)

# Health check
@app.get("/")
def health_check():
    return {"status": "ok", "message": "Privacy Gateway is running 🚀"}

# Include API router
app.include_router(auth.router, prefix="", tags=["Auth"])
app.include_router(patients.router, prefix="/patients", tags=["Patients"])
