import pytest
import asyncio
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database import db

# Creating a test client.
@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    # Connecting to test database
    try:
        await db.connect()
    except Exception:
        pass  
    
    yield
    
    try:
        collection = db.get_collection()
        await collection.delete_many({})
    except Exception:
        pass

#sample url for testing
@pytest.fixture
def sample_url():
    return "https://httpbin.org/html"


# sample metadata for testing.
@pytest.fixture
def sample_metadata():
    return {
        "url": "https://example.com",
        "headers": {"content-type": "text/html"},
        "cookies": {"session": "abc123"},
        "page_source": "<html><body>Test</body></html>",
        "status": "completed"
    }