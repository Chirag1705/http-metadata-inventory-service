import pytest
from datetime import datetime

from app.repository import MetadataRepository
from app.models import MetadataStatus


@pytest.mark.asyncio
class TestMetadataRepository:
    
    # This is the tests for MetadataRepository.
    async def test_create_or_update_new_record(self, setup_database):
        # Creating a new metadata record.
        metadata = {
            "url": "https://test-create.com",
            "headers": {"content-type": "text/html"},
            "cookies": {"session": "abc"},
            "page_source": "<html>Test</html>",
            "status": MetadataStatus.COMPLETED,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        success = await MetadataRepository.create_or_update(metadata)
        assert success is True
        
        retrieved = await MetadataRepository.get_by_url("https://test-create.com")
        assert retrieved is not None
        assert retrieved["url"] == "https://test-create.com"
        assert retrieved["status"] == "completed"
    
    async def test_get_by_url_not_found(self):
        # This is the test to retrieve non-existent metadata.
        result = await MetadataRepository.get_by_url("https://nonexistent-xyz.com")
        assert result is None
    
    async def test_create_pending(self):
        # Test to create a pending record.
        url = "https://pending-test.com"
        
        success = await MetadataRepository.create_pending(url)
        assert success is True
        
        retrieved = await MetadataRepository.get_by_url(url)
        assert retrieved is not None
        assert retrieved["status"] == "pending"
        assert retrieved["headers"] is None
    
    async def test_update_existing_record(self):
        # Test updating an existing record.
        url = "https://update-test.com"
        
        metadata1 = {
            "url": url,
            "headers": {"old": "header"},
            "cookies": {},
            "page_source": "old content",
            "status": MetadataStatus.COMPLETED,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await MetadataRepository.create_or_update(metadata1)
        
        metadata2 = {
            "url": url,
            "headers": {"new": "header"},
            "cookies": {},
            "page_source": "new content",
            "status": MetadataStatus.COMPLETED,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        success = await MetadataRepository.create_or_update(metadata2)
        assert success is True
        
        retrieved = await MetadataRepository.get_by_url(url)
        assert "new content" in retrieved["page_source"]
        assert retrieved["headers"]["new"] == "header"