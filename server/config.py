import os
import logging
from dotenv import load_dotenv

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger(__name__)

def load_config():
    logger = setup_logging()
    load_dotenv()
    config = {
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "PROCESSED_DOCS_DIR": "processed_docs"
    }
    if not config["GROQ_API_KEY"]:
        logger.error("GROQ_API_KEY not found")
        raise ValueError("Missing GROQ_API_KEY")
    logger.info("Configuration loaded")
    print("Step: Configuration loaded")
    return config

CONFIG = load_config()
logger = setup_logging()