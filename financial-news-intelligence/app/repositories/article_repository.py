from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.models.news_article import NewsArticle
from app.schemas.news_output import NewsIntelligence


class ArticleRepository:
    """Repository for news article data access."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        headline: str,
        content: str,
        source: str,
        url: Optional[str],
        published_at: str,
        source_type: str,
        intelligence: NewsIntelligence
    ) -> NewsArticle:
        """
        Create a new news article with analysis.
        
        Args:
            headline: Article headline
            content: Article content
            source: News source
            url: Article URL
            published_at: Publication timestamp
            source_type: Type of source (newsapi, gdelt, rss, manual)
            intelligence: Analyzed intelligence data
            
        Returns:
            Created NewsArticle instance
        """
        article = NewsArticle(
            headline=headline,
            content=content,
            source=source,
            url=url,
            published_at=published_at,
            source_type=source_type,
            scope=intelligence.scope,
            news_type=intelligence.news_type,
            entities=intelligence.entities.model_dump(),
            impact=intelligence.impact.model_dump(),
            facts=intelligence.facts,
            summary=intelligence.summary,
            processing_status="processed"
        )
        
        self.db.add(article)
        await self.db.flush()
        await self.db.refresh(article)
        
        return article
    
    async def get_by_id(self, article_id: int) -> Optional[NewsArticle]:
        """Get article by ID."""
        result = await self.db.execute(
            select(NewsArticle).where(NewsArticle.id == article_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_url(self, url: str) -> Optional[NewsArticle]:
        """Get article by URL (for deduplication)."""
        result = await self.db.execute(
            select(NewsArticle).where(NewsArticle.url == url)
        )
        return result.scalar_one_or_none()
    
    async def list_articles(
        self,
        scope: Optional[str] = None,
        news_type: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[NewsArticle], int]:
        """
        List articles with optional filters.
        
        Returns:
            Tuple of (articles, total_count)
        """
        # Build filter conditions
        conditions = [NewsArticle.processing_status == "processed"]
        
        if scope:
            conditions.append(NewsArticle.scope == scope)
        if news_type:
            conditions.append(NewsArticle.news_type == news_type)
        if source:
            conditions.append(NewsArticle.source == source)
        
        # Get total count
        count_query = select(NewsArticle).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = len(count_result.all())
        
        # Get paginated results
        query = (
            select(NewsArticle)
            .where(and_(*conditions))
            .order_by(NewsArticle.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.db.execute(query)
        articles = result.scalars().all()
        
        return list(articles), total
