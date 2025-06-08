import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security.oauth2 import OAuth2PasswordBearer
from passlib.hash import bcrypt
from typing import Annotated
from fastapi import Depends, HTTPException, status
from core import conf
from datetime import timedelta, datetime, timezone

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")
secret_key = conf.SECRET_KEY
algorithm = conf.ALGORITHM

def get_password_hash(password: str) -> str:
    hash_password = bcrypt.hash(password)
    return hash_password


def verify(plain_password: str, password_hash: str) -> bool:
    return bcrypt.verify(plain_password, password_hash)

def create_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta if expires_delta else datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm)

def get_user_from_token(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print(50 * '-', 'IN TOKEN: ', token,  50 * '-', sep='\n')
        payload = jwt.decode(token, secret_key, algorithms=algorithm)
        print(payload)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    return user_id

getUserFromTokenDep = Annotated[str, Depends(get_user_from_token)]