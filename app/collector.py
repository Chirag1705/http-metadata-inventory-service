import httpx
import logging
from typing import Dict, Tuple
from datetime import datetime

from app.config import settings
from app.models import MetadataStatus

logger = logging.getLogger(__name__)


class MetadataCollector:
    # Service for extracting metadata from URLs with error handling.
    
    @staticmethod
    async def collect_metadata(url: str) -> Tuple[Dict, MetadataStatus]:
        # Gather headers, cookies, and HTML content from the provided URL.
        # Handles network, HTTP, SSL, and invalid URL errors.

        metadata = {
            "url": url, 
            "headers": None,
            "cookies": None,
            "page_source": None,
            "status": MetadataStatus.FAILED,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "error_message": None
        }
        
        try:
            async with httpx.AsyncClient(
                timeout=settings.request_timeout,
                follow_redirects=True,
                verify=True  # SSL verification
            ) as client:
                response = await client.get(url)
                
                # Raise exception for HTTP error responses
                response.raise_for_status()
                
                # Collecting metadata
                metadata["headers"] = dict(response.headers)
                metadata["cookies"] = dict(response.cookies)
                metadata["page_source"] = response.text
                metadata["status"] = MetadataStatus.COMPLETED
                metadata.pop("error_message", None)  # Remove error message if successful
                
                logger.info(f"Successfully collected metadata for {url}")
            
        except Exception as e:
            error_msg = f"Unexpected error: {type(e).__name__}"
            logger.error(f"{error_msg} collecting metadata for {url}: {e}")
            metadata["status"] = MetadataStatus.FAILED
            metadata["error_message"] = error_msg
        
        return metadata, metadata["status"]