"""
MongoDB connection using Motor (async driver).
"""

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

client: AsyncIOMotorClient = None


async def connect_db():
    global client
    logger.info("Connecting to MongoDB...")
    try:
        client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=10000,
        )
        # Force an actual connection to verify credentials
        await client.admin.command("ping")
        logger.info("MongoDB connected successfully.")
        print("INFO:     MongoDB connected successfully.")
    except Exception as e:
        logger.error("MongoDB connection failed: %s", e)
        print(f"ERROR:    MongoDB connection failed: {e}")
        print("ERROR:    Check your MONGODB_URL and password in backend/.env")
        # Don't crash the server — endpoints will show errors when DB is needed
        client = None


async def close_db():
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed.")


def get_database():
    if client is None:
        raise RuntimeError("MongoDB is not connected. Check your MONGODB_URL in .env")
    return client[settings.MONGODB_DB_NAME]


# Collection accessors
def get_users_collection():
    return get_database()["users"]


def get_resumes_collection():
    return get_database()["resumes"]


def get_sessions_collection():
    return get_database()["sessions"]


def get_questions_collection():
    return get_database()["questions"]


def get_performance_collection():
    return get_database()["performance"]


def get_plans_collection():
    return get_database()["preparation_plans"]


def get_interviews_collection():
    return get_database()["mock_interviews"]


def get_rag_docs_collection():
    return get_database()["rag_documents"]
