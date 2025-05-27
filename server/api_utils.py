from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from jose import jwt, JWTError
from passlib.context import CryptContext
from typing import Dict, Any, List
import psutil
import subprocess
import re
import platform
import os
from user_agents import parse
from config import CONFIG, logger
from models import get_db_session, User, UserSession

SECRET_KEY = CONFIG.get("JWT_SECRET_KEY", os.urandom(32).hex())  # Use random key if not set
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_standard_response(status_str: str, message: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    try:
        return {"status": status_str, "message": message, "data": data or {}}
    except Exception as e:
        logger.error(f"Failed to create standard response: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process the request. Please try again later."
        )

def create_access_token(data: dict) -> tuple[str, datetime]:
    try:
        to_encode = {
            "sub": str(data["id"]),
            "role": data["role"],
        }
        expire = datetime.now(ZoneInfo("Asia/Kolkata")) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt, expire
    except Exception as e:
        logger.error(f"Token creation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process the request. Please try again later."
        )

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_session)) -> dict:
    logger.info(f"Validating token: {token[:10]}...")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired credentials. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token or token.count('.') != 2:
        logger.error(f"Invalid token format: {token if token else 'None'}")
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        role: str = payload.get("role")
        if user_id is None or role is None:
            logger.error("Invalid token: Missing user_id or role in payload")
            raise credentials_exception
    except JWTError as e:
        logger.error(f"Token decoding failed: {e}")
        raise credentials_exception
    try:
        session = db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.token == token,
            UserSession.status == "active"
        ).first()
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        if not session:
            logger.error(f"No active session found for user_id: {user_id}")
            raise credentials_exception
        # Handle potential offset-naive expires_at for existing data
        expires_at = session.expires_at
        if expires_at.tzinfo is None:
            logger.warning(f"Offset-naive expires_at detected for user_id: {user_id}, expires_at: {expires_at}, converting to Asia/Kolkata")
            expires_at = expires_at.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
        if expires_at < now:
            logger.error(f"Session expired for user_id: {user_id}, expires_at: {expires_at}")
            session.status = "expired"
            db.commit()
            raise credentials_exception
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User not found for user_id: {user_id}")
            raise credentials_exception
        logger.info(f"User authenticated: {user.username}, role: {user.role}")
        return {"id": user.id, "username": user.username, "role": user.role}
    except Exception as e:
        logger.error(f"User authentication failed for user_id {user_id}: {e}", exc_info=True)
        raise credentials_exception

def get_db():
    db = get_db_session()
    try:
        yield db
    finally:
        try:
            db.close()
            logger.info("Database session closed successfully")
        except Exception as e:
            logger.error(f"Failed to close database session: {e}", exc_info=True)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification failed: {e}", exc_info=True)
        return False

def get_password_hash(password: str) -> str:
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process the request. Please try again later."
        )

def get_mac_from_ip(ip: str) -> str:
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"ARP command failed with return code {result.returncode}")
                return None
            output = result.stdout
            pattern = re.compile(r'\s+' + re.escape(ip) + r'\s+([0-9a-fA-F-]{17})\s+')
            match = pattern.search(output)
            if match:
                return match.group(1).replace('-', ':')
            else:
                logger.info(f"No MAC address found for IP {ip}")
                return None
        else:
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"ARP command failed with return code {result.returncode}")
                return None
            output = result.stdout
            pattern = re.compile(r'\? \(' + re.escape(ip) + r'\) at ([0-9a-fA-F:]+)')
            match = pattern.search(output)
            if match:
                return match.group(1)
            else:
                logger.info(f"No MAC address found for IP {ip}")
                return None
    except Exception as e:
        logger.error(f"Failed to get MAC from IP {ip}: {e}", exc_info=True)
        return None

def get_mac_address() -> List[str]:
    try:
        interfaces = psutil.net_if_addrs()
        mac_addresses = []
        for interface, addrs in interfaces.items():
            for addr in addrs:
                if addr.family == psutil.AF_LINK:
                    mac_addresses.append(addr.address)
        if not mac_addresses:
            logger.info("No MAC addresses found on the server")
        return mac_addresses
    except Exception as e:
        logger.error(f"Failed to get MAC addresses: {e}", exc_info=True)
        return []

def get_system_info(request: Request) -> Dict[str, Any]:
    try:
        user_agent_string = request.headers.get("user-agent", "")
        user_agent = parse(user_agent_string)
        client_ip = request.client.host
        client_mac = get_mac_from_ip(client_ip)
        mac_addresses = get_mac_address()
        os_info = f"{user_agent.os.family} {user_agent.os.version_string}"
        browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
        device = user_agent.device.family
        memory_gb = psutil.virtual_memory().total / (1024 ** 3)
        cpu_cores = psutil.cpu_count(logical=True)
        return {
            "client_ip": client_ip,
            "client_mac": client_mac,
            "mac_addresses": mac_addresses,
            "os_info": os_info,
            "browser": browser,
            "device": device,
            "user_agent": user_agent_string,
            "memory_gb": memory_gb,
            "cpu_cores": cpu_cores,
        }
    except Exception as e:
        logger.error(f"Failed to retrieve system info: {e}", exc_info=True)
        return {
            "client_ip": "Unknown",
            "client_mac": None,
            "mac_addresses": [],
            "os_info": "Unknown",
            "browser": "Unknown",
            "device": "Unknown",
            "user_agent": "Unknown",
            "memory_gb": 0.0,
            "cpu_cores": 0,
        }

def migrate_sessions():
    """
    Migrate existing UserSession records to ensure expires_at is timezone-aware.
    Converts offset-naive expires_at values to offset-aware with Asia/Kolkata timezone.
    """
    try:
        db = get_db_session()
        sessions = db.query(UserSession).all()
        updated_count = 0
        for session in sessions:
            if session.expires_at and session.expires_at.tzinfo is None:
                session.expires_at = session.expires_at.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
                updated_count += 1
        db.commit()
        logger.info(f"Successfully migrated {updated_count} UserSession expires_at to timezone-aware")
    except Exception as e:
        logger.error(f"Failed to migrate sessions: {e}", exc_info=True)
        db.rollback()
        raise RuntimeError("Session migration failed")
    finally:
        try:
            db.close()
            logger.info("Database session closed successfully after migration")
        except Exception as e:
            logger.error(f"Failed to close database session after migration: {e}", exc_info=True)