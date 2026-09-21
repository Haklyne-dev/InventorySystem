from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    Response,
    Cookie,
    Header,
    Request,
)
from fastapi.security import (
    OAuth2PasswordBearer,
    HTTPBearer,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, RedirectResponse
from sqlalchemy.orm import Session, sessionmaker
import models, schemas
from database import engine, get_db
import auth
from datetime import datetime, timezone
import qrcode
from PIL import Image, ImageDraw, ImageFont
import base64
from enum import Enum
import uvicorn
import colorsys
import hashlib, io
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Robotics Inventory API")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.mount("/static", StaticFiles(directory="static"), name="static")

security = HTTPBearer()

ALLOWED_ORIGINS = ["http://localhost:8000", "https://inventory.ccshambots.com"]

LoggingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Auth dependencies


def get_current_user(
    request: Request,
    access_token: str = Cookie(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    try:
        result = auth.resolve_current_user(
            db, models.Token, models.APIKey, access_token, authorization
        )
    except auth.AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message
        )

    request.state.api_key_id = result.api_key_id
    return result.user


def verify_internal_origin(request: Request):
    fetch_site = request.headers.get("Sec-Fetch-Site")
    origin = request.headers.get("Origin")

    try:
        auth.check_origin(fetch_site, origin, request.method, ALLOWED_ORIGINS)
    except (auth.UntrustedOriginError, auth.MissingOriginError) as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


def require_admin(current_user: models.User = Depends(get_current_user)):
    try:
        auth.check_admin_role(current_user)
    except auth.InsufficientRoleError as e:
        raise HTTPException(status_code=403, detail=e.message)
    return current_user


def awaiting_onboarding():
    db = next(get_db())
    users = db.query(models.User).all()
    if not users:
        return True
    return False


# API Logging Middleware


@app.middleware("http")
async def log_api_key_usage(request: Request, call_next):
    response = await call_next(request)
 
    api_key_id = getattr(request.state, "api_key_id", None)
    if api_key_id is not None:
        endpoint = request.url.path
 
        db = LoggingSessionLocal()
        try:
            db.add(
                models.APIEvent(
                    api_key_id=api_key_id,
                    endpoint=endpoint,
                    method=request.method,
                    status_code=response.status_code,
                    origin_ip=request.client.host if request.client else "unknown",
                )
            )
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()
 
    return response


# CSS endpoint
@app.get("/styles.css", include_in_schema=False)
def get_css():
    return FileResponse("static/styles.css")


# Javascript endpoints
@app.get("/auth.js", include_in_schema=False)
def get_auth_js():
    return FileResponse("static/scripts/auth.js")


@app.get("/app.js", include_in_schema=False)
def get_main_js():
    return FileResponse("static/scripts/app.js")


@app.get("/search.js", include_in_schema=False)
def get_search_js():
    return FileResponse("static/scripts/search.js")


@app.get("/list_parts.js", include_in_schema=False)
def get_list_parts_js():
    return FileResponse("static/scripts/list_parts.js")


@app.get("/create_part.js", include_in_schema=False)
def get_create_part_js():
    return FileResponse("static/scripts/create_part.js")


@app.get("/profile.js", include_in_schema=False)
def get_profile_js():
    return FileResponse("static/scripts/profile.js")


@app.get("/part.js", include_in_schema=False)
def get_part_js():
    return FileResponse("static/scripts/part.js")


@app.get("/admin.js", include_in_schema=False)
def get_admin_js():
    return FileResponse("static/scripts/admin.js")


@app.get("/onboarding.js", include_in_schema=False)
def get_onboarding_js():
    return FileResponse("static/scripts/onboarding.js")


# Pages


@app.get("/", include_in_schema=False)
def get_index():
    return FileResponse("static/index.html")


@app.get("/login", include_in_schema=False)
def get_login():
    if awaiting_onboarding():
        return RedirectResponse("/onboarding")
    return FileResponse("static/login.html")


@app.get("/logout", include_in_schema=False)
def get_logout():
    return FileResponse("static/logout.html")


@app.get("/register", include_in_schema=False)
def get_register():
    return FileResponse("static/register.html")


@app.get("/admin", include_in_schema=False)
def get_admin():
    return FileResponse("static/admin.html")


@app.get("/parts/{part_id}", include_in_schema=False)
def get_part(part_id: int):
    return FileResponse("static/part.html")


@app.get("/search", include_in_schema=False)
def get_search():
    return FileResponse("static/search.html")


@app.get("/create_part", include_in_schema=False)
def get_create_part():
    return FileResponse("static/create_part.html")


@app.get("/profile", include_in_schema=False)
def get_profile(user: models.User = Depends(get_current_user)):
    return RedirectResponse(f"/profile/{user.id}")


@app.get("/profile/{user_id}", include_in_schema=False)
def get_profile(user_id: int):
    return FileResponse("static/profile.html")


@app.get("/onboarding", include_in_schema=False)
def get_onboarding():
    return FileResponse("static/onboarding.html")


# Error Handler


@app.exception_handler(404)
async def custom_404_handler(request, exc):
    return FileResponse("static/404.html", status_code=404)


# API endpoints


class Tags(Enum):
    auth = "Authentication"
    user = "User Management"
    parts = "Parts Management"
    history = "History and Events"


# User registration and authentication


@app.get(
    "/api/auth/me",
    response_model=schemas.User,
    tags=[Tags.auth],
    dependencies=[Depends(verify_internal_origin)],
    include_in_schema=False,
)
def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """Returns information about the currently authenticated user."""
    return current_user


@app.post(
    "/api/auth/register",
    response_model=schemas.User,
    tags=[Tags.auth],
    dependencies=[Depends(verify_internal_origin)],
    include_in_schema=False,
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Registers a new user with an invite code."""
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    if awaiting_onboarding():
        # If this is the first user, allow registration without an invite code
        new_user = models.User(
            name=user.name,
            email=user.email,
            role="admin",
            hashed_password=auth.hash_password(user.password),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    invite_code = (
        db.query(models.InviteCode)
        .filter(models.InviteCode.code == user.invite_code)
        .first()
    )

    if not invite_code or invite_code.used or invite_code.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid invite code")
    
    invite_code.user_amount -= 1
    if invite_code.user_amount <= 0:
        invite_code.used = True

    db.add(invite_code)

    new_user = models.User(
        name=user.name,
        email=user.email,
        role=invite_code.role,
        hashed_password=auth.hash_password(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post(
    "/api/auth/login",
    response_model=schemas.LoginResponse,
    tags=[Tags.auth],
    dependencies=[Depends(verify_internal_origin)],
    include_in_schema=False,
)
def login(
    body: schemas.LoginRequest, response: Response, db: Session = Depends(get_db)
):
    """Authenticates a user, sets a secure HttpOnly cookie, and logs them in."""
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user or not auth.verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    token_str = auth.generate_token()
    expiry_time = auth.token_expiry()

    db_token = models.Token(token=token_str, user_id=user.id, expires_at=expiry_time)
    db.add(db_token)
    db.commit()

    response.set_cookie(
        key="access_token",
        value=token_str,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )

    return {"status": "success", "message": "Successfully authenticated"}


@app.post(
    "/api/auth/logout",
    tags=[Tags.auth],
    dependencies=[Depends(verify_internal_origin)],
    include_in_schema=False,
)
def logout(
    response: Response,
    access_token: str = Cookie(None),
    db: Session = Depends(get_db),
):
    """Logs out the current session by deleting the token and clearing the cookie."""
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logged in"
        )

    db_token = db.query(models.Token).filter(models.Token.token == access_token).first()
    if db_token:
        db.delete(db_token)
        db.commit()

    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,  # IMPORTANT: Toggle to False if testing on local HTTP
        samesite="lax",
    )

    return {"detail": "Logged out successfully"}


@app.post(
    "/api/auth/logout_all",
    tags=[Tags.auth],
    dependencies=[Depends(verify_internal_origin)],
    include_in_schema=False,
)
def logout_all(
    response: Response,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logs out from all active database sessions and clears the client cookie."""
    db.query(models.Token).filter(models.Token.user_id == current_user.id).delete()
    db.commit()

    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,  # IMPORTANT: Toggle to False if testing on local HTTP
        samesite="lax",
    )

    return {"detail": "Logged out from all sessions successfully"}


@app.post(
    "/api/auth/delete_account",
    tags=[Tags.auth],
    dependencies=[Depends(verify_internal_origin)],
    include_in_schema=False,
)
def delete_account(
    current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    db.query(models.Token).filter(models.Token.user_id == current_user.id).delete()
    db.delete(current_user)
    db.commit()
    return {"detail": "Account deleted successfully"}


@app.delete(
    "/api/auth/{user_id}",
    dependencies=[Depends(require_admin), Depends(verify_internal_origin)],
    tags=[Tags.auth],
    include_in_schema=False,
)
def admin_delete_user(user_id: int, db: Session = Depends(get_db)):
    """Allows an admin to delete a user account by ID."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.query(models.Token).filter(models.Token.user_id == user.id).delete()
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}


@app.post(
    "/api/auth/invite",
    response_model=schemas.InviteCode,
    dependencies=[Depends(require_admin), Depends(verify_internal_origin)],
    tags=[Tags.auth],
    include_in_schema=False,
)
def create_invite_code(invite_code: schemas.InviteCodeCreate, db: Session = Depends(get_db)):
    """Allows an admin to create a new invite code with a specified role."""
    if invite_code.role not in ["admin", "member"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    new_code = models.InviteCode(
        code=auth.generate_invite_code(), role=invite_code.role, expires_at=auth.code_expiry(), user_amount=invite_code.user_amount
    )
    db.add(new_code)
    db.commit()
    db.refresh(new_code)
    return new_code


@app.get(
    "/api/auth/invite_codes",
    response_model=list[schemas.InviteCode],
    dependencies=[Depends(require_admin)],
    tags=[Tags.auth],
    include_in_schema=False
)
def list_invite_codes(db: Session = Depends(get_db)):
    """Allows an admin to list all invite codes."""
    codes = db.query(models.InviteCode).all()
    return codes


@app.delete(
    "/api/auth/invite_codes/{code_id}",
    dependencies=[Depends(require_admin)],
    tags=[Tags.auth],
    include_in_schema=False
)
def delete_invite_code(code_id: int, db: Session = Depends(get_db)):
    """Allows an admin to delete an invite code by ID."""
    code = db.query(models.InviteCode).filter(models.InviteCode.id == code_id).first()
    if not code:
        raise HTTPException(status_code=404, detail="Invite code not found")
    db.delete(code)
    db.commit()
    return {"detail": "Invite code deleted successfully"}


@app.get(
    "/api/onboarding/status",
    response_model=schemas.OnboardingStatus,
    dependencies=[Depends(verify_internal_origin)],
    include_in_schema=False,
)   
def onboarding_status():
    """Returns the onboarding status of the system."""
    status = not awaiting_onboarding()
    return {"onboarded": status}


# User info and management endpoints


@app.get("/api/users/me", response_model=schemas.User, tags=[Tags.user])
def read_current_user(current_user: models.User = Depends(get_current_user)):
    """Returns information about the currently authenticated user."""
    return current_user


@app.get(
    "/api/users/{user_id}",
    response_model=schemas.UserSimple,
    dependencies=[Depends(get_current_user)],
    tags=[Tags.user],
)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Returns basic information about a user by ID. Requires authentication."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get(
    "/api/users",
    response_model=list[schemas.UserSimple],
    dependencies=[Depends(get_current_user)],
    tags=[Tags.user],
)
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Returns a list of all users with basic information. Requires authentication."""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@app.get(
    "/api/users_full",
    response_model=list[schemas.User],
    dependencies=[Depends(require_admin)],
    tags=[Tags.user],
)
def read_users_full(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Returns a list of all users with full information. Requires admin access."""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@app.get(
    "/api/users/{user_id}/full",
    response_model=schemas.User,
    dependencies=[Depends(require_admin)],
    tags=[Tags.user],
)
def read_user_full(user_id: int, db: Session = Depends(get_db)):
    """Returns full information about a user by ID. Requires admin access."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Part info and management


@app.get(
    "/api/parts/{part_id}",
    response_model=schemas.Part,
    dependencies=[Depends(get_current_user)],
    tags=[Tags.parts],
)
def read_part(
    part_id: int,
    db: Session = Depends(get_db),
):
    """Returns detailed information about a part by ID."""
    part = db.query(models.Part).filter(models.Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    return part


@app.get(
    "/api/parts",
    response_model=list[schemas.Part],
    dependencies=[Depends(get_current_user)],
    tags=[Tags.parts],
)
def read_parts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Returns a list of all parts with detailed information."""
    parts = db.query(models.Part).offset(skip).limit(limit).all()
    return parts


@app.get(
    "/api/parts/search",
    response_model=list[schemas.Part],
    dependencies=[Depends(get_current_user)],
    tags=[Tags.parts],
)
def search_parts(
    query: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Searches for parts by name, location, category, or description."""
    search_query = f"%{query}%"
    parts = (
        db.query(models.Part)
        .filter(
            (models.Part.name.ilike(search_query))
            | (models.Part.location.ilike(search_query))
            | (models.Part.category.ilike(search_query))
            | (models.Part.description.ilike(search_query))
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    return parts


@app.get(
    "/api/parts/{part_id}/history",
    response_model=list[schemas.PartEvent],
    dependencies=[Depends(get_current_user)],
    tags=[Tags.parts, Tags.history],
)
def read_part_history(
    part_id: int,
    db: Session = Depends(get_db),
):
    """Returns the history of events for a specific part."""
    part = db.query(models.Part).filter(models.Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    return part.history


@app.get(
    "/api/users/{user_id}/history",
    response_model=list[schemas.PartEvent],
    dependencies=[Depends(get_current_user)],
    tags=[Tags.user, Tags.history],
)
def read_user_history(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Returns the history of events for a specific user."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.history


@app.post(
    "/api/parts/create",
    response_model=schemas.Part,
    dependencies=[Depends(get_current_user)],
    tags=[Tags.parts],
)
def create_part(
    part: schemas.PartCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """Creates a new part and logs the creation event."""
    db_part = models.Part(**part.model_dump())

    if db.query(models.Part).filter(models.Part.name == db_part.name).first():
        raise HTTPException(
            status_code=400, detail="Part with this name already exists"
        )

    db.add(db_part)
    db.flush()

    # Add history event
    event = models.PartEvent(
        part_id=db_part.id,
        user_id=current_user.id,
        type=models.EventType.create,
        note=f"Part created with initial quantity {db_part.quantity}",
    )
    db.add(event)

    db.commit()
    db.refresh(db_part)
    return db_part


@app.post(
    "/api/parts/{part_id}/update",
    response_model=schemas.Part,
    dependencies=[Depends(get_current_user)],
    tags=[Tags.parts],
)
def update_part(
    part_id: int,
    part: schemas.PartUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """Updates an existing part and logs the event."""
    db_part = db.query(models.Part).filter(models.Part.id == part_id).first()
    if not db_part:
        raise HTTPException(status_code=404, detail="Part not found")

    for key, value in part.model_dump(exclude_unset=True).items():
        setattr(db_part, key, value)

    # Add history event
    event = models.PartEvent(
        part_id=db_part.id,
        user_id=current_user.id,
        type=models.EventType.update,
        note=f"Updated part details: {part.model_dump(exclude_unset=True)}",
    )
    db.add(event)

    db.commit()
    db.refresh(db_part)
    return db_part


@app.post(
    "/api/parts/{part_id}/checkout",
    response_model=schemas.Part,
    dependencies=[Depends(get_current_user)],
    tags=[Tags.parts],
)
def checkout_part(
    part_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Checks out a part and logs the event."""
    db_part = db.query(models.Part).filter(models.Part.id == part_id).first()
    if not db_part:
        raise HTTPException(status_code=404, detail="Part not found")

    if db_part.quantity < quantity:
        raise HTTPException(status_code=400, detail="Insufficient quantity")

    db_part.quantity -= quantity

    # Add history event
    event = models.PartEvent(
        part_id=db_part.id,
        user_id=current_user.id,
        type=models.EventType.checkout,
        quantity=quantity,
        note=f"Checked out {quantity} units of part {db_part.name}",
    )
    db.add(event)

    db.commit()
    db.refresh(db_part)
    return db_part


@app.post(
    "/api/parts/{part_id}/restock",
    response_model=schemas.Part,
    dependencies=[Depends(get_current_user)],
    tags=[Tags.parts],
)
def restock_part(
    part_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Restocks a part and logs the event."""
    db_part = db.query(models.Part).filter(models.Part.id == part_id).first()
    if not db_part:
        raise HTTPException(status_code=404, detail="Part not found")

    db_part.quantity += quantity

    # Add history event
    event = models.PartEvent(
        part_id=db_part.id,
        user_id=current_user.id,
        type=models.EventType.restock,
        quantity=quantity,
        note=f"Restocked {quantity} units of part {db_part.name}",
    )
    db.add(event)

    db.commit()
    db.refresh(db_part)
    return db_part


@app.delete(
    "/api/parts/{part_id}",
    dependencies=[Depends(get_current_user)],
    tags=[Tags.parts],
)
def delete_part(
    part_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """Deletes a part."""
    db_part = db.query(models.Part).filter(models.Part.id == part_id).first()
    if not db_part:
        raise HTTPException(status_code=404, detail="Part not found")

    db.delete(db_part)
    db.commit()
    return {"message": "Part deleted successfully"}


@app.post(
    "/api/api_keys/create",
    response_model=schemas.APIKeyCreateResponse,
    dependencies=[Depends(get_current_user), Depends(verify_internal_origin)],
    tags=[Tags.auth],
    include_in_schema=False
)
def create_api_key(
    key: schemas.APIKeyCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Creates a new API key."""
    raw_key = auth.generate_api_key()
    stored_key = auth.hash_api_key(raw_key)

    api_key = models.APIKey(name=key.name, key=stored_key, user_id=user.id)
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    api_key_response = schemas.APIKeyCreateResponse(
        id=api_key.id,
        name=api_key.name,
        key=raw_key,
        user_id=api_key.user_id,
        created_at=api_key.created_at,
    )
    return api_key_response


@app.get(
    "/api/api_keys",
    response_model=list[schemas.APIKey],
    dependencies=[Depends(get_current_user), Depends(verify_internal_origin)],
    tags=[Tags.auth],
    include_in_schema=False
)
def list_api_keys(
    db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    """Lists all API keys."""
    api_keys = db.query(models.APIKey).filter(models.APIKey.user_id == user.id).all()
    return api_keys


@app.get(
    "/api/api_keys/user/{user_id}",
    response_model=list[schemas.APIKey],
    dependencies=[Depends(get_current_user), Depends(verify_internal_origin)],
    tags=[Tags.auth],
    include_in_schema=False
)
def list_api_keys_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Lists all API keys for a specific user."""
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    api_keys = db.query(models.APIKey).filter(models.APIKey.user_id == user_id).all()
    return api_keys


@app.get(
    "/api/api_keys/{api_key_id}",
    response_model=schemas.APIKey,
    dependencies=[Depends(get_current_user), Depends(verify_internal_origin)],
    tags=[Tags.auth],
    include_in_schema=False
)
def get_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Gets a specific API key."""
    api_key = (
        db.query(models.APIKey)
        .filter(models.APIKey.id == api_key_id, models.APIKey.user_id == user.id)
        .first()
    )
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    return api_key


@app.delete(
    "/api/api_keys/{api_key_id}",
    dependencies=[Depends(get_current_user), Depends(verify_internal_origin)],
    tags=[Tags.auth],
    include_in_schema=False
)
def delete_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Deletes a specific API key."""
    api_key = None
    if user.role == "admin":
        api_key = db.query(models.APIKey).filter(models.APIKey.id == api_key_id).first()
    else:
        api_key = (
            db.query(models.APIKey)
            .filter(models.APIKey.id == api_key_id, models.APIKey.user_id == user.id)
            .first()
        )
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    db.delete(api_key)
    db.commit()
    return {"message": "API key deleted successfully"}


# Label generation function


def get_wrapped_text(text, font: ImageFont, max_width: int):
    lines = []
    current_line = ""

    for word in text.split():
        test_line = current_line + (" " if current_line else "") + word
        left, top, right, bottom = font.getbbox(test_line)
        width = right - left

        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    wrapped_width = max(font.getbbox(line)[2] - font.getbbox(line)[0] for line in lines)
    wrapped_height = (
        len(lines) * (font.getbbox("Ay")[3] - font.getbbox("Ay")[1])
        + (len(lines) - 1) * 5
    )

    return "\n".join(lines), wrapped_width, wrapped_height


@app.get(
    "/parts/{part_id}/label",
    include_in_schema=False,
    dependencies=[Depends(get_current_user)],
)
def get_part_label(part_id: int, db: Session = Depends(get_db)):
    SCALE = 3
    part = db.query(models.Part).filter(models.Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    url = f"http://your-server-ip:8000/parts/{part_id}"

    qr = qrcode.make(url, box_size=5 * SCALE).convert("RGB")

    width, height = qr.size
    new_image = Image.new("RGB", (width * 3, height), color="white")

    draw = ImageDraw.Draw(new_image)

    new_image.paste(qr, (0, 0))

    draw.rounded_rectangle(
        [(0, 0), (width * 3 - 1, height - 1)],
        radius=20 * SCALE,
        outline="black",
        width=2 * SCALE,
    )

    title_font = ImageFont.truetype("arialbd.ttf", size=30 * SCALE)
    id_font = ImageFont.truetype("arial.ttf", size=20 * SCALE)

    name_wrapped, wrapped_width, wrapped_height = get_wrapped_text(
        part.name, title_font, max_width=width * 2 - 20 * SCALE
    )

    draw.text(
        (width + 10 * SCALE, 20 * SCALE), name_wrapped, fill="black", font=title_font
    )
    draw.text(
        (width + 10, 40 + wrapped_height),
        f"{part.location}   ID: {part.id}",
        fill="black",
        font=id_font,
    )

    buffer = io.BytesIO()
    new_image.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")


@app.get(
    "/api/parts/{part_id}/qr",
    include_in_schema=False,
    dependencies=[Depends(get_current_user)],
)
def get_part_qr(part_id: int, db: Session = Depends(get_db)):
    part = db.query(models.Part).filter(models.Part.id == part_id).first()
    print(f"Generating QR code for part ID: {part_id}")
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    url = f"http://your-server-ip:8000/parts/{part_id}"

    qr = qrcode.make(url, box_size=10).convert("RGB")

    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    return {"image": base64.b64encode(buffer.getvalue()).decode("utf-8")}


# Dynamic image generation for other purposes


@app.get(
    "/images/avatar/{user_id}",
    include_in_schema=False,
    dependencies=[Depends(get_current_user)],
)
def get_user_avatar(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    hash_int = abs(int(hashlib.md5(user.email.encode()).hexdigest(), 16))
    h = hash_int % 360
    min_s, max_s = 55, 85
    s = min_s + ((hash_int >> 4) % (max_s - min_s + 1))
    l = 50

    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    color = (int(r * 255), int(g * 255), int(b * 255))

    image = Image.new("RGB", (200, 200), color=color)
    draw = ImageDraw.Draw(image)
    padding = 20
    font_size = 200 - (padding * 2)
    try:
        font = ImageFont.truetype("arialbd.ttf", size=font_size)
    except:
        font = ImageFont.load_default()

    letter = user.name[0].upper() if user.name else "?"

    left, top, right, bottom = draw.textbbox((0, 0), letter, font=font)
    text_width = right - left
    text_height = bottom - top

    x = (200 - text_width) / 2 - left
    y = (200 - text_height) / 2 - top

    draw.text((x, y), letter, fill="white", font=font)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")


@app.get(
    "/images/avatar",
    include_in_schema=False,
    dependencies=[Depends(get_current_user)],
)
def get_current_user_avatar(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_avatar(current_user.id, db)


@app.get(
    "/api/downloads/label_sheet",
    include_in_schema=False,
)
def generate_label_sheet(db: Session = Depends(get_db)):
    part_ids_list = [part.id for part in db.query(models.Part).all()]

    output_pdf_path = "label_sheet.pdf"
    generate_label_pdf(part_ids_list, output_pdf_path, db)

    return FileResponse(output_pdf_path, media_type="application/pdf")


def generate_label_pdf(part_ids, output_pdf_path, db):
    # Avery 5160 layout
    COLUMNS_COUNT = 3
    ROWS_COUNT = 10
    LABELS_PER_PAGE = COLUMNS_COUNT * ROWS_COUNT
    PAGE_SIZE = letter

    LABEL_W = 2.625 * inch
    LABEL_H = 1.0 * inch
    MARGIN_LEFT = 0.1875 * inch
    MARGIN_TOP = 0.5 * inch
    PITCH_X = 2.75 * inch
    PITCH_Y = 1.0 * inch

    DPI = 300
    LABEL_PX_W = round(LABEL_W / inch * DPI)
    LABEL_PX_H = round(LABEL_H / inch * DPI)

    def pt_to_px(pt):
        return round(pt / 72 * DPI)

    PAD = pt_to_px(6)
    QR_SIZE = LABEL_PX_H - 2 * PAD
    TEXT_X = PAD + QR_SIZE + PAD
    TEXT_W = LABEL_PX_W - TEXT_X - PAD
    TEXT_H = LABEL_PX_H - 2 * PAD

    id_font = ImageFont.truetype("arial.ttf", size=pt_to_px(9))
    id_line_height = round(pt_to_px(9) * 1.2)

    def render_label(part):
        url = f"http://your-server-ip:8000/parts/{part.id}"
        qr = qrcode.make(url, box_size=5, border=1).convert("RGB")
        qr = qr.resize((QR_SIZE, QR_SIZE), Image.NEAREST)

        label = Image.new("RGB", (LABEL_PX_W, LABEL_PX_H), color="white")
        draw = ImageDraw.Draw(label)
        label.paste(qr, (PAD, PAD))

        title_pt = 14
        while True:
            title_font = ImageFont.truetype("arialbd.ttf", size=pt_to_px(title_pt))
            name_wrapped, _, wrapped_height = get_wrapped_text(
                part.name, title_font, max_width=TEXT_W
            )
            if wrapped_height + PAD + id_line_height <= TEXT_H or title_pt <= 8:
                break
            title_pt -= 1

        draw.text((TEXT_X, PAD), name_wrapped, fill="black", font=title_font)
        draw.text(
            (TEXT_X, PAD + wrapped_height + PAD // 2),
            f"{part.location}   ID: {part.id}",
            fill="black",
            font=id_font,
        )

        draw.rounded_rectangle(
            [(2, 2), (LABEL_PX_W - 3, LABEL_PX_H - 3)],
            radius=25,
            outline="black",
            width=3,
        )
        return label

    page_w, page_h = PAGE_SIZE
    c = canvas.Canvas(output_pdf_path, pagesize=PAGE_SIZE)
    c.setTitle("Part Labels")

    c.setAuthor("Inventory Management System")
    c.setSubject("Avery 5160 Label Sheet")

    slot = 0
    for part_id in part_ids:
        part = db.query(models.Part).filter(models.Part.id == part_id).first()
        if not part:
            continue

        if slot == LABELS_PER_PAGE:
            c.showPage()
            slot = 0

        row, col = divmod(slot, COLUMNS_COUNT)
        x = MARGIN_LEFT + col * PITCH_X
        y = page_h - MARGIN_TOP - (row + 1) * PITCH_Y

        c.drawImage(ImageReader(render_label(part)), x, y, width=LABEL_W, height=LABEL_H)
        slot += 1
        

    c.save()


uvicorn.run(app, host="0.0.0.0", port=8000)
