import pytest
from httpx import AsyncClient

# It tests error handling scenarios.
@pytest.mark.asyncio
class TestErrorHandling:    
    async def test_invalid_url_format(self, client: AsyncClient):
        # Invalid URL format.
        response = await client.post(
            "/metadata",
            json={"url": "not-a-url"}
        )
        assert response.status_code == 422
    
    async def test_malformed_request_body(self, client: AsyncClient):
        # Test handling of faulty request.
        response = await client.post(
            "/metadata",
            json={"wrong_field": "value"}
        )
        assert response.status_code == 422
    
    async def test_unreachable_url(self, client: AsyncClient):
        # Unreachable URL.
        response = await client.post(
            "/metadata",
            json={"url": "https://this-domain-does-not-exist-12345.com"}
        )
        
        # It should still return 201 but mark as failed
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "failed"