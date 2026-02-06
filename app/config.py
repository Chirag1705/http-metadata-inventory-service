from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # Application config getting loaded from environment variables
    
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "metadata_db"
    collection_name: str = "url_metadata"
    request_timeout: int = 10
    
    @field_validator('request_timeout')
    @classmethod
    def validate_timeout(cls, v):
        if v < 1 or v > 60:
            raise ValueError('request_timeout must be between 1 and 60 seconds')
        return v
    
    @field_validator('mongodb_url')
    @classmethod
    def validate_mongodb_url(cls, v):
        # Check that the MongoDB URL uses the correct scheme
        if not v.startswith('mongodb://'):
            raise ValueError('mongodb_url must start with mongodb://')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()