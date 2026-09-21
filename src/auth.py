from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
import secrets, random, string, hashlib

pwd_context = CryptContext(
    schemes=["bcrypt_sha256"],
    default="bcrypt_sha256",
)

TOKEN_EXPIRY_DAYS = 30
INVITE_CODE_EXPIRY_HOURS = 24


# Errors


class AuthError(Exception):

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotAuthenticatedError(AuthError):
    """No credentials were supplied at all."""


class InvalidTokenError(AuthError):
    """Session token does not correspond to a known token."""


class SessionExpiredError(AuthError):
    """Session token exists but has expired."""


class UserNotFoundError(AuthError):
    """Token/key resolved, but no associated user exists."""


class InvalidAuthHeaderError(AuthError):
    """Authorization header was present but malformed."""


class InvalidAPIKeyError(AuthError):
    """Authorization header contained a key that isn't recognized."""


class InsufficientRoleError(AuthError):
    """Authenticated user does not have the required role."""


class UntrustedOriginError(AuthError):
    """Request originated from a site that isn't on the allow-list."""


class MissingOriginError(AuthError):
    """State-changing request had no origin metadata at all."""


# Password hashing


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Session tokens


def generate_token() -> str:
    return secrets.token_hex(32)


def token_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRY_DAYS)


def resolve_user_from_session_token(db, token_model, access_token: str):
    db_token = db.query(token_model).filter(token_model.token == access_token).first()
    if not db_token:
        raise InvalidTokenError("Invalid session token")

    now = datetime.now(timezone.utc)
    expires_at = db_token.expires_at
    if expires_at.tzinfo is None:
        now = now.replace(tzinfo=None)

    if expires_at < now:
        raise SessionExpiredError("Session expired")

    if not db_token.user:
        raise UserNotFoundError("User not found")

    return db_token.user


# API keys


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


def generate_api_key() -> str:
    return secrets.token_urlsafe(32)


def resolve_api_key_record(db, api_key_model, authorization_header: str):
    if not authorization_header.startswith("Bearer "):
        raise InvalidAuthHeaderError(
            "Invalid authorization header format. Use 'Bearer <key>'"
        )

    raw_key = authorization_header[7:]
    hashed_key = hash_api_key(raw_key)

    db_api_key = db.query(api_key_model).filter(api_key_model.key == hashed_key).first()
    if not db_api_key:
        raise InvalidAPIKeyError("Invalid API key")

    return db_api_key


def resolve_user_from_api_key(db, api_key_model, authorization_header: str):
    return resolve_api_key_record(db, api_key_model, authorization_header).user


class AuthResult:
    __slots__ = ("user", "api_key_id")

    def __init__(self, user, api_key_id=None):
        self.user = user
        self.api_key_id = api_key_id


def resolve_current_user(db, token_model, api_key_model, access_token, authorization):
    if access_token:
        user = resolve_user_from_session_token(db, token_model, access_token)
        return AuthResult(user=user, api_key_id=None)
    elif authorization:
        api_key_record = resolve_api_key_record(db, api_key_model, authorization)
        return AuthResult(user=api_key_record.user, api_key_id=api_key_record.id)
    else:
        raise NotAuthenticatedError("Not authenticated")


# Roles


def check_admin_role(user) -> None:
    if user.role != "admin":
        raise InsufficientRoleError("Admin access required")


# Invite codes


def generate_invite_code(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def code_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=INVITE_CODE_EXPIRY_HOURS)


# Request origin checking


def check_origin(fetch_site, origin, method, allowed_origins) -> None:
    if fetch_site:
        if fetch_site not in ("same-origin", "same-site"):
            raise UntrustedOriginError(
                "Access denied: External API requests are blocked for this endpoint."
            )
        return

    if origin:
        if origin not in allowed_origins:
            raise UntrustedOriginError("Access denied: Untrusted origin.")
        return

    if method in ("POST", "PUT", "DELETE"):
        raise MissingOriginError("Access denied: Missing origin security metadata.")
