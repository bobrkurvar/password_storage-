import jwt
from fastapi.security.oauth2 import OAuth2PasswordBearer
from fastapi import APIRouter, Body
from passlib.hash import bcrypt
from typing import Annotated
from fastapi import Depends, HTTPException, status
from core import conf
from datetime import timedelta, datetime, timezone

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")
secret_key = conf.secret_key
algorithm = conf.algorithm
router = APIRouter(prefix='/security')

def get_password_hash(password: str) -> str:
    hash_password = bcrypt.hash(password)
    return hash_password

def verify(plain_password: str, password_hash: str) -> bool:
    return bcrypt.verify(plain_password, password_hash)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta if expires_delta else datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm)

def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta if expires_delta else datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm)

def get_user_from_token(token: Annotated[str, Depends(oauth2_scheme)]):
    invalid_credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    expire_credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Access token expired. Please refresh your token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithm)
        user_id = payload.get("sub")
        if user_id is None:
            raise invalid_credentials_exception
    except jwt.InvalidTokenError:
        raise invalid_credentials_exception
    except jwt.ExpiredSignatureError:
        raise expire_credentials_exception
    return user_id

@router.post("/refresh")
def refresh_token(refresh_token: Annotated[str, Body()]):
    try:
        payload = jwt.decode(refresh_token, secret_key, algorithms=algorithm)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

getUserFromTokenDep = Annotated[str, Depends(get_user_from_token)]