import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security.oauth2 import OAuth2PasswordBearer
from passlib.hash import bcrypt
from typing import Annotated
from fastapi import Depends, HTTPException, status
from core import conf
from datetime import timedelta, datetime, timezone
from web.api.schemas.user import UserInput

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")
secret_key = conf.SECRET_KEY
algorithm = conf.ALGORITHM

def get_password_hash(user: UserInput) -> str:
    hash_password = bcrypt.hash(user.password)
    return hash_password

def verify(plain_password: str, password_hash: Annotated[str, Depends(get_password_hash)]) -> bool:
    return bcrypt.verify(plain_password, password_hash)

def create_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    token = jwt.encode(key=secret_key, algorithm=algorithm, payload=to_encode)
    return token

def get_user_from_token(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithm)
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    return username

getUserFromToken = Annotated[str, Depends(get_user_from_token)]