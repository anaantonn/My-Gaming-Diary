import os

from dotenv import load_dotenv

from logger import get_logger

logger = get_logger(__name__)


def load_config():
    load_dotenv()
    key = os.getenv("STEAM_API_KEY")
    steam_id = os.getenv("STEAM_ACCOUNT_ID")
    if not key or not steam_id:
        logger.error("Missing STEAM_API_KEY or STEAM_ACCOUNT_ID in .env")
        raise ValueError("Missing STEAM_API_KEY or STEAM_ACCOUNT_ID in .env")
    return key, steam_id

def load_db_config():
    load_dotenv()
    db_url = os.getenv("DB_PATH")
    if not db_url:
        logger.error("Missing DB_PATH in .env")
        raise ValueError("Missing DB_PATH in .env")
    return db_url
