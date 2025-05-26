import os
import shutil
from config import CONFIG, logger

DOC_FOLDER = r"C:\Users\shib kumar saraf\Documents\llm_agent\dataset\pdfs"

ROLE_PDFS = {
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
        "Dataco Global Order Management Policy.pdf",
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
}

def setup_role_folders():
    try:
        os.makedirs(DOC_FOLDER, exist_ok=True)
        for role, pdfs in ROLE_PDFS.items():
            role_folder = os.path.join(DOC_FOLDER, role)
            os.makedirs(role_folder, exist_ok=True)
            for pdf in pdfs:
                src_path = os.path.join(DOC_FOLDER, pdf)
                dst_path = os.path.join(role_folder, pdf)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, dst_path)
                    logger.info(f"Copied {pdf} to {role_folder}")
                else:
                    logger.warning(f"PDF {pdf} not found in {DOC_FOLDER}")
        logger.info("Role-based folder setup completed")
    except Exception as e:
        logger.error(f"Error setting up role folders: {e}")
        raise

if __name__ == "__main__":
    try:
        setup_role_folders()
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        raise