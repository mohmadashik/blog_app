from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
import jwt

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
MAX_PASSWORD_BYTES = 72


def _truncate_for_bcrypt(password: str) -> bytes:
    """
    Bcrypt has a maximum password length of 72 BYTES.
    We enforce that at the byte level.
    """
    if password is None:
        return b""
    pw_bytes = password.encode("utf-8")
    if len(pw_bytes) > MAX_PASSWORD_BYTES:
        pw_bytes = pw_bytes[:MAX_PASSWORD_BYTES]
    return pw_bytes


def hash_password(password: str) -> str:
    # Passlib is fine with bytes here, it will pass them through to bcrypt
    return pwd_context.hash(_truncate_for_bcrypt(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(_truncate_for_bcrypt(plain_password), hashed_password)


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
