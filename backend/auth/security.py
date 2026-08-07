from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from backend.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Converts a plain-text password into a secure hash for storage."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks a login attempt's password against the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)



def create_access_token(user_id: int) -> str:
    """Creates a JWT token containing the user's id, valid for 24 hours."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int:
    """
    Verifies a JWT token and returns the user_id inside it.
    Raises JWTError if the token is invalid or expired.
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return int(payload["sub"])