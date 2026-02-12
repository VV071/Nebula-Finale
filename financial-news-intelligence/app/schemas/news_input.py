from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime


class ManualArticleInput(BaseModel):
    """Schema for manually submitted articles."""
    
    headline: str = Field(..., min_length=10, max_length=500, description="Article headline")
    content: str = Field(..., min_length=50, description="Full article content")
    source: str = Field(..., min_length=2, max_length=100, description="News source name")
    url: Optional[str] = Field(None, description="Article URL")
    published_at: Optional[str] = Field(None, description="Publication timestamp (ISO format)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "headline": "Federal Reserve raises interest rates by 0.25%",
                "content": "The Federal Reserve announced today that it is raising interest rates by 25 basis points...",
                "source": "Reuters",
                "url": "https://reuters.com/article/...",
                "published_at": "2026-02-08T10:30:00Z"
            }
        }


class BatchIngestRequest(BaseModel):
    """Schema for batch ingestion requests."""
    
    source_type: str = Field(..., description="Source type: newsapi, gdelt, rss, or all")
    keywords: Optional[list[str]] = Field(None, description="Keywords to filter articles")
    date_from: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    date_to: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    max_articles: Optional[int] = Field(100, ge=1, le=1000, description="Maximum articles to fetch")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_type": "newsapi",
                "keywords": ["earnings", "GDP"],
                "date_from": "2026-02-01",
                "date_to": "2026-02-08",
                "max_articles": 50
            }
        }
