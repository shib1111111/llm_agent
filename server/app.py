from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from api_utils import create_standard_response
from apis.api import api_router
from apis.auth import auth_router
from config import CONFIG, logger
from document_processor import DocumentProcessor
from models import Documents, get_db_session, UserSession
from datetime import datetime
from zoneinfo import ZoneInfo
import os
from contextlib import asynccontextmanager
from api_utils import migrate_sessions
app = FastAPI(title="SCM Chatbot API")

# Configure CORS with specific origins for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=CONFIG.get("ALLOWED_ORIGINS", ["http://localhost:3000"]),  # Update with specific frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Include API and auth routers
app.include_router(auth_router)
app.include_router(api_router)

@asynccontextmanager
async def startup_event():
    """Initialize the application by cleaning up expired sessions and processing default documents."""
    db = get_db_session()
    migrate_sessions()
    try:
        # Clean up expired sessions
        expired_count = db.query(UserSession).filter(
            UserSession.expires_at < datetime.now(ZoneInfo("Asia/Kolkata"))
        ).update({"status": "expired"})
        db.commit()
        logger.info(f"Cleaned up {expired_count} expired sessions during startup.")

        # Process default documents for all roles
        failed_roles = []
        for role, pdfs in CONFIG["ROLE_PDFS"].items():
            try:
                for pdf in pdfs:
                    db.merge(Documents(
                        role=role,
                        filename=pdf,
                        doc_type="default",
                        timestamp=datetime.now(ZoneInfo("Asia/Kolkata"))
                    ))
                db.commit()
                doc_processor = DocumentProcessor(os.path.join(CONFIG["ROOT_DIR"], "dataset", "pdfs"), role)
                doc_processor.process_documents()
                logger.info(f"Processed default documents for role: {role}")
            except Exception as e:
                logger.error(f"Failed to process documents for role {role}: {str(e)}", exc_info=True)
                failed_roles.append(role)
        
        if failed_roles:
            logger.warning(f"Document processing failed for roles: {', '.join(failed_roles)}. Application started with partial success.")
        else:
            logger.info("Successfully processed all default documents for all roles.")

        # Log non-sensitive configuration
        safe_config = {k: v for k, v in CONFIG.items() if k not in ["JWT_SECRET_KEY", "GROQ_API_KEY", "ANTHROPIC_API_KEY"]}
        logger.info(f"Application started with configuration: {safe_config}")
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}", exc_info=True)
        raise RuntimeError("Application startup failed")
    finally:
        try:
            db.close()
        except Exception as e:
            logger.error(f"Failed to close database session: {str(e)}", exc_info=True)

app.lifespan = startup_event