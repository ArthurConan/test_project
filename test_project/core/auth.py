from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from typing import Union, Any

from test_project.core.settings import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token/")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_oauth_token(subject: Union[str, Any], expired_miutes: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expired_miutes)
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, get_settings().auth.secret_key, algorithm=get_settings().auth.algorithm)


def encode_token(token: str) -> Union[str, dict, HTTPException]:
    return jwt.decode(token, get_settings().auth.secret_key, algorithms=get_settings().auth.algorithm)
