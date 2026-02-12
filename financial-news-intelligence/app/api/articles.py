from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.repositories.article_repository import ArticleRepository
from app.schemas.news_output import (
    NewsIntelligence,
    Entities,
    ImpactAnalysis,
    ArticleResponse,
    ArticleListResponse
)
from typing import Optional

router = APIRouter(prefix="/api/articles", tags=["Articles"])


@router.get("", response_model=ArticleListResponse)
async def list_articles(
    scope: Optional[str] = Query(None, description="Filter by scope"),
    news_type: Optional[str] = Query(None, description="Filter by news type"),
    source: Optional[str] = Query(None, description="Filter by source"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    Query analyzed articles with filters and pagination.
    
    Returns a paginated list of previously analyzed articles.
    """
    repo = ArticleRepository(db)
    
    offset = (page - 1) * page_size
    articles, total = await repo.list_articles(
        scope=scope,
        news_type=news_type,
        source=source,
        limit=page_size,
        offset=offset
    )
    
    # Convert to response format
    article_responses = []
    for article in articles:
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
    
    return ArticleListResponse(
        total=total,
        page=page,
        page_size=page_size,
        articles=article_responses
    )


@router.get("/{article_id}", response_model=NewsIntelligence)
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific article analysis by ID.
    """
    repo = ArticleRepository(db)
    article = await repo.get_by_id(article_id)
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return NewsIntelligence(
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
