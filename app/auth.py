import uuid
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from .constants import SHREYA_UUID, ADITI_UUID

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
EXPIRY    = 60  # minutes

# sample users
fake_users = {
    "shreya@example.com": {
        "name": "Shreya",
        "email": "shreya@example.com",
        "author_uuid": SHREYA_UUID,
        "password": "shreyapass"
    },
    "aditi@example.com": {
        "name": "Aditi",
        "email": "aditi@example.com",
        "author_uuid": ADITI_UUID,
        "password": "aditipass"
    }
}
# --- Pydantic schemas ---
class LoginIn(BaseModel):
    email:    EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type:   str

# --- FastAPI router & security ---
router  = APIRouter(tags=["auth"])
bearer  = HTTPBearer()


def authenticate_user(email: str, pwd: str) -> Optional[dict]:
    u = fake_users.get(email)
    if u and u["password"] == pwd:
        return u
    return None

def create_access_token(sub: str) -> str:
    to_encode = {"sub": sub, "exp": datetime.utcnow() + timedelta(minutes=EXPIRY)}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login", response_model=TokenOut)
def login(data: LoginIn):
    user = authenticate_user(data.email, data.password)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    token = create_access_token(sub=user["author_uuid"])
    return {"access_token": token, "token_type": "bearer"}

async def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(bearer),
):
    token = cred.credentials
    try:
        payload     = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        author_uuid = payload.get("sub")
        if not author_uuid:
            raise JWTError()
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    # find in our fake db
    user = next((u for u in fake_users.values() if u["author_uuid"] == author_uuid), None)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unknown user")
    return user