from pydantic import BaseModel
from typing import Literal

class TokenRequest(BaseModel):
    role: Literal["clinician", "researcher", "developer"]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
