"""
Authentication utilities:
  - Password hashing / verification via passlib (bcrypt)
  - Signed session cookies via itsdangerous
  - FastAPI dependency: get_current_user / require_professor
"""

from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from config import settings

# ── Password hashing ──────────────────────────────────────────────────────────
_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_ctx.verify(plain, hashed)


# ── Signed session cookie ─────────────────────────────────────────────────────
_signer = URLSafeTimedSerializer(settings.SECRET_KEY, salt="session")


def create_session_token(user_id: int) -> str:
    return _signer.dumps(user_id)


def decode_session_token(token: str) -> int | None:
    try:
        return _signer.loads(token, max_age=settings.SESSION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None


# ── FastAPI dependencies ──────────────────────────────────────────────────────
def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """Dependency: returns the logged-in User or raises 401/redirect."""
    token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"},
        )
    user_id = decode_session_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"},
        )
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"},
        )
    return user


def require_professor(current_user: User = Depends(get_current_user)) -> User:
    """Dependency: only professors pass through."""
    if not current_user.is_professor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Professors only.")
    return current_user
