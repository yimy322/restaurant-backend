import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.security import create_access_token, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")

print("DEBUG HASH:", repr(ADMIN_PASSWORD_HASH))

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    valid_user = form_data.username == ADMIN_USERNAME
    valid_password = bool(ADMIN_PASSWORD_HASH) and verify_password(form_data.password, ADMIN_PASSWORD_HASH)

    if not (valid_user and valid_password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    access_token = create_access_token(data={"sub": form_data.username})
    return Token(access_token=access_token)