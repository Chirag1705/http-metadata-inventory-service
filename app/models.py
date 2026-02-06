from pydantic import BaseModel, HttpUrl, Field
from typing import Dict, Optional
from datetime import datetime
from enum import Enum


class MetadataStatus(str, Enum):
    # Status of metadata collection.
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class URLRequest(BaseModel):
    # Request model for URL input.
    url: HttpUrl = Field(..., description="The URL to collect metadata from")


class MetadataResponse(BaseModel):
    # Response model for metadata retrieval.
    url: str
    headers: Optional[Dict[str, str]] = None
    cookies: Optional[Dict[str, str]] = None
    page_source: Optional[str] = None
    status: MetadataStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MetadataCreateResponse(BaseModel):
    # Response model for metadata creation.
    message: str
    url: str
    status: MetadataStatus


class MetadataAcceptedResponse(BaseModel):
    # Response model for accepted (202) requests.
    message: str
    url: str
    status: MetadataStatus = MetadataStatus.PENDING
