from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.database import db
from app.models import (
    URLRequest, 
    MetadataResponse, 
    MetadataCreateResponse,
    MetadataAcceptedResponse,
    MetadataStatus
)
from app.repository import MetadataRepository
from app.collector import MetadataCollector

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Handles startup and shutdown events for the application

    logger.info("Starting up application...")
    await db.connect()
    yield

    logger.info("Shutting down application...")
    await db.disconnect()


app = FastAPI(
    title="HTTP Metadata Inventory Service",
    description="Service to collect and retrieve HTTP metadata (headers, cookies, page source) for URLs",
    version="1.0.0",
    lifespan=lifespan
)


async def background_collect_metadata(url: str):
        # Collect metadata for a URL in the background

    logger.info(f"Starting background collection for {url}")
    
    metadata, status = await MetadataCollector.collect_metadata(url)
    
    await MetadataRepository.create_or_update(metadata)
    
    logger.info(f"Completed background collection for {url} with status {status}")


@app.get("/", tags=["Health"])
async def root():
    # Basic health check endpoint
    return {
        "status": "healthy",
        "service": "HTTP Metadata Inventory Service"
    }


@app.post(
    "/metadata",
    response_model=MetadataCreateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Metadata"],
    summary="Create metadata record for a URL",
    description="Collects headers, cookies, and page source for the given URL and stores in database"
)
async def create_metadata(request: URLRequest):
        # Endpoint to create a metadata record for a given URL

    url = str(request.url)
    
    try:
        # Synchronously collect metadata for the POST request
        metadata, collect_status = await MetadataCollector.collect_metadata(url)
        
        # Store in database
        success = await MetadataRepository.create_or_update(metadata)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store metadata"
            )
        
        return MetadataCreateResponse(
            message="Metadata collected and stored successfully",
            url=url,
            status=collect_status
        )
        
    except Exception as e:
        logger.error(f"Error creating metadata for {url}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create metadata: {str(e)}"
        )


@app.get(
    "/metadata",
    response_model=MetadataResponse,
    tags=["Metadata"],
    summary="Retrieve metadata for a URL",
    description="Returns cached metadata if available, otherwise triggers background collection and returns 202 Accepted"
)
async def get_metadata(url: str, background_tasks: BackgroundTasks):
        # Endpoint to retrieve metadata for a given URL

    if not url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL parameter is required"
        )
    
    try:
        # Check if metadata exists in the db
        existing_metadata = await MetadataRepository.get_by_url(url)
        
        if existing_metadata:
            return MetadataResponse(**existing_metadata)
        
        else:
            # Record doesn't exist - create pending and trigger background collection
            logger.info(f"Cache miss for {url}, triggering background collection")
            
            await MetadataRepository.create_pending(url)
            
            background_tasks.add_task(background_collect_metadata, url)
            
            response_data = MetadataAcceptedResponse(
                message="Request accepted. Metadata collection in progress.",
                url=url,
                status=MetadataStatus.PENDING
            )
            
            return JSONResponse(
                status_code=status.HTTP_202_ACCEPTED,
                content=response_data.model_dump()
            )
            
    except Exception as e:
        logger.error(f"Error retrieving metadata for {url}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve metadata: {str(e)}"
        )

@app.get("/health", tags=["Health"])
async def health_check():
        # Endpoint for a full health check of the API and database

    health_status = {
        "status": "healthy",
        "service": "HTTP Metadata Inventory Service",
        "database": "disconnected"
    }
    
    # Check db connection health
    try:
        db_healthy = await db.health_check()
        health_status["database"] = "connected" if db_healthy else "disconnected"
        
        if not db_healthy:
            health_status["status"] = "unhealthy"
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=health_status
            )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        health_status["status"] = "unhealthy"
        health_status["database"] = "error"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )
    
    return health_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
