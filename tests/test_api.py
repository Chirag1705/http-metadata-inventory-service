import pytest
from httpx import AsyncClient
import asyncio

# Testing health check and root endpoints.
@pytest.mark.asyncio
class TestHealthEndpoints:
    
    async def test_root_endpoint(self, client: AsyncClient):
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data

# Testing POST metadata endpoint.
@pytest.mark.asyncio
class TestPostMetadataEndpoint:
    
    
    async def test_create_metadata_success(self, client: AsyncClient):
        response = await client.post(
            "/metadata",
            json={"url": "https://httpbin.org/html"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "url" in data
        assert data["status"] in ["completed", "failed"]
        assert "message" in data
    
    # This func is testing creating metadata with invalid URL.
    async def test_create_metadata_invalid_url(self, client: AsyncClient):
        
        response = await client.post(
            "/metadata",
            json={"url": "not-a-valid-url"}
        )
        
        assert response.status_code == 422
    
    # This func is testing creating metadata without URL.
    async def test_create_metadata_missing_url(self, client: AsyncClient):
        response = await client.post(
            "/metadata",
            json={}
        )
        
        assert response.status_code == 422  # error
    
    # This func is to test creating metadata for same URL twice.
    async def test_create_metadata_duplicate(self, client: AsyncClient):
        
        url = "https://httpbin.org/html"
        
        # First request
        response1 = await client.post(
            "/metadata",
            json={"url": url}
        )
        assert response1.status_code == 201
        
        # Second request - it should update, not fail
        response2 = await client.post(
            "/metadata",
            json={"url": url}
        )
        assert response2.status_code == 201

# Test GET metadata endpoint.
@pytest.mark.asyncio
class TestGetMetadataEndpoint:
    
    # Test GET endpoint when metadata doesn't exist - it should return 202.
    async def test_get_metadata_not_found_returns_202(self, client: AsyncClient):
        response = await client.get("/metadata?url=https://new-url-12345.com")
        
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "pending"
        assert "message" in data
        assert "in progress" in data["message"].lower()
    
    # Test GET endpoint when metadata exists. It should return 200 with metadata.
    async def test_get_metadata_found_returns_200(self, client: AsyncClient):
        url = "https://httpbin.org/html"
        
        create_response = await client.post(
            "/metadata",
            json={"url": url}
        )
        assert create_response.status_code == 201
        
        get_response = await client.get(f"/metadata?url={url}")
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["url"] == url
        assert "headers" in data
        assert "status" in data
    
    async def test_get_metadata_missing_url_parameter(self, client: AsyncClient):
        """Test GET endpoint without URL parameter."""
        response = await client.get("/metadata")
        
        assert response.status_code == 422  # error
    
    # This func is the test that background collection eventually completes.
    async def test_get_metadata_background_collection(self, client: AsyncClient):
        url = "https://httpbin.org/html"
        
        response1 = await client.get(f"/metadata?url={url}")
        assert response1.status_code == 202
        
        await asyncio.sleep(3)
        
        response2 = await client.get(f"/metadata?url={url}")
        assert response2.status_code == 200
        data = response2.json()
        assert data["status"] in ["completed", "failed"]

# This test complete workflows.
@pytest.mark.asyncio
class TestWorkflowIntegration:
    
    async def test_post_then_get_workflow(self, client: AsyncClient):
        url = "https://httpbin.org/html"
        
        post_response = await client.post(
            "/metadata",
            json={"url": url}
        )
        assert post_response.status_code == 201
        post_data = post_response.json()
        
        get_response = await client.get(f"/metadata?url={url}")
        assert get_response.status_code == 200
        get_data = get_response.json()
        
        assert get_data["url"] == url
        assert get_data["status"] == post_data["status"]
        assert "headers" in get_data
        assert "created_at" in get_data
        assert "updated_at" in get_data
    
    async def test_get_then_get_workflow(self, client: AsyncClient):
        url = "https://httpbin.org/html"
        
        response1 = await client.get(f"/metadata?url={url}")
        assert response1.status_code == 202
        
        await asyncio.sleep(3)
        
        response2 = await client.get(f"/metadata?url={url}")
        assert response2.status_code == 200
        
        data = response2.json()
        assert data["url"] == url
        assert data["status"] in ["completed", "failed"]