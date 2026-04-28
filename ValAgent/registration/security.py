from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt
from config import settings
import unicodedata

# ✅ Use PBKDF2-SHA256 (no 72-byte limit, safe for training & prod)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def normalize_pw(p: str) -> str:
    return unicodedata.normalize("NFKC", p).strip()

def hash_password(p: str) -> str:
    return pwd_context.hash(normalize_pw(p))

def verify_password(p: str, hashed: str) -> bool:
    return pwd_context.verify(normalize_pw(p), hashed)

def create_access_token(sub: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.JWT_EXPIRES_MIN)
    payload = {"sub": sub, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
