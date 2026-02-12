from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.ingest import process_batch_ingestion, job_status
from app.schemas.news_input import BatchIngestRequest
from datetime import datetime, timedelta
import uuid

router = APIRouter(prefix="/api/stocks", tags=["Stock News"])


@router.post("/fetch-news")
async def fetch_stock_news(
    background_tasks: BackgroundTasks,
    days_back: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    max_articles: int = Query(200, ge=1, le=1000, description="Max articles to fetch"),
    db: AsyncSession = Depends(get_db)
):
    """
    Dedicated endpoint to fetch comprehensive stock market news.
    
    This endpoint automatically uses stock-specific keywords and fetches from
    all available sources (NewsAPI, GDELT, RSS feeds).
    
    Args:
        days_back: Number of days to look back (default: 7)
        max_articles: Maximum articles to fetch (default: 200)
    
    Returns:
        Job ID for tracking ingestion progress
    """
    # Stock-specific keywords
    stock_keywords = [
        "stock market", "stocks", "NYSE", "NASDAQ", "DOW", "S&P 500",
        "earnings report", "quarterly earnings", "IPO", "stock price",
        "share price", "market rally", "dividend", "stock buyback",
        "market crash", "bull market", "bear market"
    ]
    
    # Calculate date range
    date_to = datetime.now().strftime("%Y-%m-%d")
    date_from = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    # Create batch request
    request = BatchIngestRequest(
        source_type="all",  # Fetch from all sources
        keywords=stock_keywords,
        date_from=date_from,
        date_to=date_to,
        max_articles=max_articles
    )
    
    # Create job
    job_id = str(uuid.uuid4())
    job_status[job_id] = {
        "status": "pending",
        "total_articles": 0,
        "processed": 0,
        "failed": 0,
        "type": "stock_news",
        "date_range": f"{date_from} to {date_to}"
    }
    
    # Add background task
    background_tasks.add_task(
        process_batch_ingestion,
        job_id,
        request,
        db
    )
    
    return {
        "job_id": job_id,
        "status": "started",
        "message": f"Stock news ingestion started for last {days_back} days",
        "date_range": f"{date_from} to {date_to}",
        "keywords_count": len(stock_keywords),
        "check_status": f"/api/ingest/status/{job_id}"
    }


@router.get("/latest")
async def get_latest_stock_news(
    limit: int = Query(20, ge=1, le=100, description="Number of articles"),
    news_type: str = Query(None, description="Filter by type: Earnings, Corporate, etc."),
    impact_direction: str = Query(None, description="Filter by impact: Positive, Negative, Neutral"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get latest analyzed stock news articles.
    
    This is a convenience endpoint that filters for stock-related news
    (Company and Sector scope).
    """
    from app.repositories.article_repository import ArticleRepository
    from app.schemas.news_output import NewsIntelligence, Entities, ImpactAnalysis, ArticleResponse
    
    repo = ArticleRepository(db)
    
    # Get articles with Company or Sector scope (stock-related)
    articles, total = await repo.list_articles(
        scope=None,  # We'll filter both Company and Sector
        news_type=news_type,
        limit=limit,
        offset=0
    )
    
    # Filter for stock-related scopes
    stock_articles = [a for a in articles if a.scope in ["Company", "Sector"]]
    
    # Further filter by impact direction if specified
    if impact_direction:
        stock_articles = [
            a for a in stock_articles 
            if a.impact.get("direction") == impact_direction
        ]
    
    # Convert to response format
    article_responses = []
    for article in stock_articles[:limit]:
        intelligence = NewsIntelligence(
            headline=article.headline,
            source=article.source,
            published_at=article.published_at,
            scope=article.scope,
            news_type=article.news_type,
            entities=Entities(**article.entities),
            impact=ImpactAnalysis(**article.impact),
            facts=article.facts,
            summary=article.summary
        )
        
        article_responses.append(
            ArticleResponse(
                id=article.id,
                intelligence=intelligence,
                processing_status=article.processing_status,
                created_at=article.created_at
            )
        )
    
    return {
        "total": len(stock_articles),
        "returned": len(article_responses),
        "articles": article_responses
    }
