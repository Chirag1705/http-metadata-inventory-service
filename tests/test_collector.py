import pytest
from unittest.mock import MagicMock, patch
import httpx

from app.collector import MetadataCollector
from app.models import MetadataStatus

# tests for MetadataCollector.
@pytest.mark.asyncio
class TestMetadataCollector:
    
    async def test_collect_metadata_success(self):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.headers = {"content-type": "text/html", "server": "nginx"}
        mock_response.cookies = {"session": "test123"}
        mock_response.text = "<html><body>Test Page</body></html>"
        mock_response.raise_for_status = MagicMock()
        
        with patch("httpx.AsyncClient.get", return_value=mock_response):
            metadata, status = await MetadataCollector.collect_metadata("https://example.com")
            
            assert status == MetadataStatus.COMPLETED
            assert metadata["url"] == "https://example.com"
            assert metadata["headers"]["content-type"] == "text/html"
            assert metadata["cookies"]["session"] == "test123"
            assert "Test Page" in metadata["page_source"]
            assert metadata.get("error_message") is None
    
        # This tests metadata collection with timeout.
    async def test_collect_metadata_timeout(self):
        
        with patch("httpx.AsyncClient.get", side_effect=httpx.TimeoutException("Timeout")):
            metadata, status = await MetadataCollector.collect_metadata("https://slow-site.com")
            
            assert status == MetadataStatus.FAILED
            assert metadata["headers"] is None
            assert metadata["cookies"] is None
            assert metadata["page_source"] is None
            assert "timeout" in metadata["error_message"].lower()
    
        # Test metadata collection with HTTP error.
    async def test_collect_metadata_http_error(self):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError("Not Found", request=None, response=mock_response)
        )
        
        with patch("httpx.AsyncClient.get", return_value=mock_response):
            metadata, status = await MetadataCollector.collect_metadata("https://notfound.com")
            
            assert status == MetadataStatus.FAILED
            assert "404" in metadata["error_message"]

        # This tests metadata collection with connection error.
    async def test_collect_metadata_connection_error(self):      
        with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("Connection failed")):
            metadata, status = await MetadataCollector.collect_metadata("https://invalid-url.com")
            
            assert status == MetadataStatus.FAILED
            assert metadata["url"] == "https://invalid-url.com"
            assert "connection" in metadata["error_message"].lower()