from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class ImpactAnalysis(BaseModel):
    """Market impact analysis."""
    
    direction: Literal["Positive", "Negative", "Neutral", "Unclear"] = Field(
        ..., 
        description="Impact direction on markets"
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence score between 0 and 1"
    )
    time_horizon: Literal["Short", "Medium", "Long"] = Field(
        ..., 
        description="Expected time horizon of impact"
    )


class Entities(BaseModel):
    """Affected entities extracted from news."""
    
    countries: list[str] = Field(default_factory=list, description="Affected countries")
    sectors: list[str] = Field(default_factory=list, description="Affected sectors")
    companies: list[str] = Field(default_factory=list, description="Mentioned companies")
    indices: list[str] = Field(default_factory=list, description="Mentioned market indices")


class NewsIntelligence(BaseModel):
    """Complete structured news intelligence output (MANDATORY FORMAT)."""
    
    headline: str = Field(..., description="Article headline")
    source: str = Field(..., description="News source")
    published_at: str = Field(..., description="Publication timestamp")
    scope: Literal["Global", "Country", "Sector", "Company"] = Field(
        ..., 
        description="News scope"
    )
    news_type: Literal["Macro", "Earnings", "Policy", "Geopolitical", "Corporate", "Sentiment"] = Field(
        ..., 
        description="Type of news"
    )
    entities: Entities = Field(..., description="Affected entities")
    impact: ImpactAnalysis = Field(..., description="Market impact assessment")
    facts: list[str] = Field(default_factory=list, description="Verifiable facts extracted")
    summary: str = Field(..., description="Concise neutral summary")
    
    class Config:
        json_schema_extra = {
            "example": {
                "headline": "Federal Reserve raises interest rates by 0.25%",
                "source": "Reuters",
                "published_at": "2026-02-08T10:30:00Z",
                "scope": "Global",
                "news_type": "Policy",
                "entities": {
                    "countries": ["United States"],
                    "sectors": ["Finance", "Banking"],
                    "companies": [],
                    "indices": ["S&P 500", "NASDAQ"]
                },
                "impact": {
                    "direction": "Negative",
                    "confidence": 0.75,
                    "time_horizon": "Short"
                },
                "facts": [
                    "Federal Reserve raised rates by 25 basis points",
                    "New federal funds rate is 5.25%-5.50%",
                    "Decision was unanimous among FOMC members"
                ],
                "summary": "The Federal Reserve increased interest rates by 0.25 percentage points to combat inflation, bringing the target range to 5.25%-5.50%. The decision was unanimous and signals continued tightening monetary policy."
            }
        }


class ArticleResponse(BaseModel):
    """Response for a single article with analysis."""
    
    id: int
    intelligence: NewsIntelligence
    processing_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """Paginated list of articles."""
    
    total: int
    page: int
    page_size: int
    articles: list[ArticleResponse]
