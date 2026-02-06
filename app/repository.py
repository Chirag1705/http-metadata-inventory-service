from typing import Optional, Dict
from datetime import datetime
import logging

from app.database import db
from app.models import MetadataStatus

logger = logging.getLogger(__name__)


class MetadataRepository:
    # Repository for metadata database operations.
    
    @staticmethod
    async def get_by_url(url: str) -> Optional[Dict]:
        # Retrieving metadata by URL.
        try:
            collection = db.get_collection()
            document = await collection.find_one({"url": url})
            
            if document:
                # Removing MongoDB _id field for cleaner response
                document.pop("_id", None)
                
            return document
            
        except Exception as e:
            logger.error(f"Error retrieving metadata for {url}: {e}")
            return None
    
    @staticmethod
    async def create_or_update(metadata: Dict) -> bool:
        # Inserting a new metadata record or update an existing one.

        try:
            collection = db.get_collection()
            
            # Storing the status as a string
            metadata_to_store = metadata.copy()
            if isinstance(metadata_to_store.get("status"), MetadataStatus):
                metadata_to_store["status"] = metadata_to_store["status"].value
            
            # Build the update, removing created_at
            update_data = {k: v for k, v in metadata_to_store.items() if k != "created_at"}
            update_data["updated_at"] = datetime.utcnow()
            
            result = await collection.update_one(
                {"url": metadata_to_store["url"]},
                {
                    "$set": update_data,
                    "$setOnInsert": {
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            logger.info(f"Stored metadata for {metadata_to_store['url']}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing metadata: {e}", exc_info=True)
            return False
    
    @staticmethod
    async def create_pending(url: str) -> bool:
        # Adding a new pending metadata entry for the given URL if it doesn't already exist.
        try:
            collection = db.get_collection()
            
            pending_record = {
                "url": url,
                "headers": None,
                "cookies": None,
                "page_source": None,
                "status": MetadataStatus.PENDING,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # This makes sure it only inserts if doesn't exist
            result = await collection.update_one(
                {"url": url},
                {
                    "$setOnInsert": pending_record
                },
                upsert=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating pending record: {e}")
            return False
