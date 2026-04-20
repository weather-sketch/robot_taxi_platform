from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.models import UserAccount, UserRole

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


async def authenticate_user(db: AsyncSession, username: str, password: str) -> UserAccount | None:
    stmt = select(UserAccount).where(UserAccount.username == username, UserAccount.is_active == True)  # noqa: E712
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user and verify_password(password, user.hashed_password):
        return user
    return None


# --- Role-based permission checks ---

# Which roles can access which features (keyed by string for SQLite compatibility)
ROLE_PERMISSIONS: dict[str, set[str]] = {
    "operator": {
        "feedback:read", "feedback:create",
        "ticket:read", "ticket:create", "ticket:update",
        "dashboard:read",
        "ai:analyze",
    },
    "supervisor": {
        "feedback:read", "feedback:create",
        "ticket:read", "ticket:create", "ticket:update", "ticket:batch",
        "dashboard:read", "dashboard:export",
        "ai:analyze",
        "user:read",
    },
    "analyst": {
        "feedback:read",
        "ticket:read",
        "dashboard:read", "dashboard:export",
        "ai:analyze",
    },
    "admin": {
        "feedback:read", "feedback:create",
        "ticket:read", "ticket:create", "ticket:update", "ticket:batch",
        "dashboard:read", "dashboard:export",
        "ai:analyze",
        "user:read", "user:manage",
        "config:manage",
    },
}


def has_permission(role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())
