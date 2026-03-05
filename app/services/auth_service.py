from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.auth import verify_password


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def authenticate(self, email: str, password: str) -> tuple[User | None, str]:
        """Returns (user, error). error is '' on success."""
        if not email or not password:
            return None, "Email and password are required."
        user = self.repo.get_by_email(email)
        if user is None:
            return None, "Invalid email or password."
        if not user.is_active:
            return None, "Account is deactivated."
        if not verify_password(password, user.password_hash):
            return None, "Invalid email or password."
        return user, ""
