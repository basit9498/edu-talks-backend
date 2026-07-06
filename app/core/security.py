
# from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha256
import jwt
from datetime import datetime, timedelta, timezone
from app.config import settings

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pbkdf2_sha256.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    print(to_encode)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def decode_token(token: str):
    return jwt.decode(
        token,
        settings.JWT_KEY,
        algorithms=[ALGORITHM]
    )
