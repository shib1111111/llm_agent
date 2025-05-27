# server/config.py
import os
import logging
from dotenv import load_dotenv

# Dynamically find the root directory containing 'llm_agent'
def get_root_dir(target_folder="llm_agent"):
    path = os.path.abspath(__file__)
    while os.path.basename(path) != target_folder:
        path = os.path.dirname(path)
        if path == os.path.dirname(path):  # Reached root of filesystem
            raise RuntimeError(f"Could not find root folder '{target_folder}'")
    return path

ROOT_DIR = get_root_dir()

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
        'SECRET_KEY': os.getenv("SECRET_KEY", os.urandom(32).hex()),
        "ALLOWED_ORIGINS": os.getenv("ALLOWED_ORIGINS", "*").split(","),
        'SQLITE_DB':"sqlite:///users.db",
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "PROCESSED_DOCS_DIR": os.path.join(ROOT_DIR, "processed_docs"),
        "ROLES": ["admin", "planning", "finance", "operations"],
        "ROOT_DIR": ROOT_DIR,
        "DB_URI": os.getenv("DB_URI"),
        'ROLE_PDFS' : {
                    "admin": [
                        "Anti-Counterfeit and Product Authenticity Policy.pdf",
                        "Circular Economy.pdf",
                        "COC.pdf",
                        "Communication and Crisis Management Policy for DataCo Global.pdf",
                        "Continuous Improvement.pdf",
                        "Cost Reduction.pdf",
                        "Data Security.pdf",
                        "DataCo Global Capacity Planning Policy.pdf",
                        "Dataco Global Change Management Policy for Supply Chain Processes.pdf",
                        "DataCo Global Contract Management and Negotiation Policy.pdf",
                        "DataCo Global Order Management Policy.pdf",
                        "Dataco Global Transportation and Logistics Policy.pdf",
                        "DataCo Global Warehouse and Storage Policy.pdf",
                        "Dataco Global_ Demand Forecasting and Planning Policy.pdf",
                        "Diversity and Inclusion in Supplier Base Policy for DataCo Global.pdf",
                        "Environmental Sustainability.pdf",
                        "Global Business Continuity.pdf",
                        "Global Returns.pdf",
                        "Health Safety and Environment (HSE) Policy for Supply Chain Management.pdf",
                        "Inventory.pdf",
                        "IOT.pdf",
                        "KPI.pdf",
                        "Labor Standards.pdf",
                        "Obsolete Inventory Handling Policy for Dataco Global.pdf",
                        "QA.pdf",
                        "Risk Management.pdf",
                        "Sourcing and Procurement Policy for DataCo Global.pdf",
                        "SRM.pdf",
                        "Supplier Selection.pdf",
                        "Trade Compliance.pdf"
                    ],
                    "planning": [
                        "Inventory.pdf",
                        "Dataco Global Transportation and Logistics Policy.pdf",
                        "Dataco Global_ Demand Forecasting and Planning Policy.pdf",
                        "DataCo Global Capacity Planning Policy.pdf",
                        "Continuous Improvement.pdf",
                        "Obsolete Inventory Handling Policy for Dataco Global.pdf"
                    ],
                    "finance": [
                        "Cost Reduction.pdf",
                        "DataCo Global Contract Management and Negotiation Policy.pdf",
                        "Sourcing and Procurement Policy for DataCo Global.pdf",
                        "Risk Management.pdf"
                    ],
                    "operations": [
                        "DataCo Global Warehouse and Storage Policy.pdf",
                        "QA.pdf",
                        "SRM.pdf",
                        "Supplier Selection.pdf",
                        "Health Safety and Environment (HSE) Policy for Supply Chain Management.pdf",
                        "Global Returns.pdf"
                    ]
                },
    }
    if not config["GROQ_API_KEY"]:
        logger.error("GROQ_API_KEY not found")
        raise ValueError("Missing GROQ_API_KEY")
    if not config["ANTHROPIC_API_KEY"]:
        logger.error("ANTHROPIC_API_KEY not found")
        raise ValueError("Missing ANTHROPIC_API_KEY")
    logger.info("Configuration loaded")
    return config

CONFIG = load_config()
logger = setup_logging()
