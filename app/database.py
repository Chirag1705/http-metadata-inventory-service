from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging
import asyncio

from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    # Manages MongoDB connections with retry support
    
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect(cls, max_retries: int = 5, retry_delay: int = 2):
       # Connect to MongoDB with multiple retry attempts
        for attempt in range(max_retries):
            try:
                cls.client = AsyncIOMotorClient(
                    settings.mongodb_url,
                    serverSelectionTimeoutMS=5000,
                    maxPoolSize=50,  # Connection pool size
                    minPoolSize=10,
                    maxIdleTimeMS=30000
                )
                cls.db = cls.client[settings.database_name]
                
                # Test connection
                await cls.client.admin.command('ping')
                logger.info("Successfully connected to MongoDB")
                
                # Ensuring a unique index exists on the url field
                await cls.db[settings.collection_name].create_index(
                    "url", 
                    unique=True
                )
                logger.info("Created index on 'url' field")
                
                return
                
            except Exception as e:
                logger.warning(
                    f"MongoDB connection attempt {attempt + 1}/{max_retries} failed: {e}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error("Failed to connect to MongoDB after all retries")
                    raise
    
    @classmethod
    async def disconnect(cls):
        # Close the MongoDB client connection
        if cls.client:
            cls.client.close()
            logger.info("Disconnected from MongoDB")
    
    @classmethod
    def get_collection(cls):
        # Retrieve the metadata collection object
        if cls.db is None:
            raise RuntimeError("Database not connected")
        return cls.db[settings.collection_name]
    
    @classmethod
    async def health_check(cls) -> bool:
        # Perform a health check on the MongoDB connection
        try:
            await cls.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Singleton db instance
db = Database()