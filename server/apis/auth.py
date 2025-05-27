from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo
import os
from config import CONFIG, logger
from models import User, UserSession, UserLog
from api_utils import (
    create_access_token,
    create_standard_response,
    get_db,
    get_password_hash,
    get_current_user,
    verify_password,
    get_system_info
)
from schema import StandardResponse, Token, UserModel

auth_router = APIRouter(prefix="/api", tags=["auth"])

@auth_router.post("/signup", response_model=StandardResponse)
async def signup(user: UserModel, db: Session = Depends(get_db)):
    """Register a new user with a unique username and email."""
    try:
        if user.role not in CONFIG.get("ROLES", []):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid role: {user.role}. Allowed roles: {', '.join(CONFIG['ROLES'])}."
            )
        if db.query(User).filter(User.username == user.username).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This username is already taken. Please choose a different one."
            )
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This email is already registered. Please use a different email or log in."
            )
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            name=user.name,
            username=user.username,
            password=hashed_password,
            role=user.role,
            signup_timestamp=datetime.now(ZoneInfo("Asia/Kolkata"))
        )
        db.add(db_user)
        db.commit()
        logger.info(f"User created successfully: {user.username}, role: {user.role}")
        return create_standard_response("success", "Account created successfully! You can now log in.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create user {user.username}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during signup. Please try again later."
        )

@auth_router.post("/login", response_model=StandardResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Authenticate a user and create a session with system information."""
    try:
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user or not verify_password(form_data.password, user.password):
            logger.error(f"Login attempt failed for username: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password. Please try again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        session_id = os.urandom(16).hex()
        access_token, expires_at = create_access_token({"id": user.id, "role": user.role})
        db_session = UserSession(
            session_id=session_id,
            user_id=user.id,
            token=access_token,
            created_at=datetime.now(ZoneInfo("Asia/Kolkata")),
            expires_at=expires_at,
            status="active",
        )
        db.add(db_session)
        system_info = get_system_info(request)
        user_log = UserLog(
            user_id=user.id,
            client_ip=system_info["client_ip"],
            mac_address=system_info["client_mac"],
            os_info=system_info["os_info"],
            browser=system_info["browser"],
            device=system_info["device"],
            user_agent=system_info["user_agent"],
            memory_gb=system_info["memory_gb"],
            cpu_cores=system_info["cpu_cores"],
            login_timestamp=datetime.now(ZoneInfo("Asia/Kolkata"))
        )
        db.add(user_log)
        db.commit()
        logger.info(f"User logged in: {user.username}, token: {access_token[:10]}...")
        return create_standard_response(
            "success",
            "Login successful. Use the provided token for authenticated requests.",
            Token(access_token=access_token, token_type="bearer").dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed for username {form_data.username}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login. Please try again later."
        )

@auth_router.post("/logout", response_model=StandardResponse)
async def logout(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Log out the current user by expiring their active sessions."""
    try:
        updated_count = db.query(UserSession).filter(
            UserSession.user_id == current_user["id"],
            UserSession.status == "active"
        ).update({"status": "expired"})
        db.commit()
        logger.info(f"User logged out: {current_user['username']}, {updated_count} sessions expired")
        return create_standard_response("success", "You have been logged out successfully.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout failed for user {current_user['username']}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during logout. Please try again later."
        )