import pytest
from httpx import AsyncClient
import asyncio

# Testing the performance and concurrent operations.
@pytest.mark.asyncio
class TestPerformance:
    
    async def test_concurrent_post_requests(self, client: AsyncClient):
        # This is the test to handle multiple concurrent POST requests.
        urls = [f"https://httpbin.org/html?id={i}" for i in range(5)]
        
        # Send concurrent requests
        tasks = [
            client.post("/metadata", json={"url": url})
            for url in urls
        ]
        responses = await asyncio.gather(*tasks)
        
        for response in responses:
            assert response.status_code == 201
    
    async def test_concurrent_get_requests(self, client: AsyncClient):
        # This is the test to handle multiple concurrent GET requests.

        url = "https://httpbin.org/html"
        await client.post("/metadata", json={"url": url})
        
        # Send concurrent GET requests
        tasks = [client.get(f"/metadata?url={url}") for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["url"] == url