from fastapi import FastAPI
from api import patients, auth, download
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Privacy Gateway API",
    description="Role-aware Privacy-as-a-Service Gateway for hospital data",
    version="1.0.0"
)

# allow frontend
origins = [
    "http://localhost:3000",   # Next.js dev server
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],            # allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],            # allow Content-Type, Authorization, etc.
)

# Include API router
app.include_router(auth.router, prefix="", tags=["Auth"])
app.include_router(patients.router, prefix="/patients", tags=["Patients"])
app.include_router(download.router, prefix="/download", tags=["download"])
