from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.news_input import ManualArticleInput
from app.schemas.news_output import NewsIntelligence
from app.services.analysis.analyzer import NewsAnalyzer
from app.repositories.article_repository import ArticleRepository

router = APIRouter(prefix="/api/analyze", tags=["Analysis"])

# Initialize analyzer
analyzer = NewsAnalyzer()


@router.post("/article", response_model=NewsIntelligence)
async def analyze_article(
    article: ManualArticleInput,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze a single news article and return structured intelligence.
    
    This endpoint accepts a manually submitted article, performs comprehensive
    analysis, and returns structured JSON intelligence WITHOUT investment advice.
    
    **STRICT COMPLIANCE:**
    - No buy/sell/hold recommendations
    - No price predictions
    - Conservative and factual analysis only
    - Returns "Unclear" when information is insufficient
    """
    try:
        # Perform analysis
        intelligence = analyzer.analyze(
            headline=article.headline,
            content=article.content,
            source=article.source,
            published_at=article.published_at or ""
        )
        
        # Store in database
        repo = ArticleRepository(db)
        
        # Check for duplicates by URL
        if article.url:
            existing = await repo.get_by_url(article.url)
            if existing:
                # Return existing analysis
                from app.schemas.news_output import Entities, ImpactAnalysis
                return NewsIntelligence(
                    headline=existing.headline,
                    source=existing.source,
                    published_at=existing.published_at,
                    scope=existing.scope,
                    news_type=existing.news_type,
                    entities=Entities(**existing.entities),
                    impact=ImpactAnalysis(**existing.impact),
                    facts=existing.facts,
                    summary=existing.summary
                )
        
        # Create new  article record
        await repo.create(
            headline=article.headline,
            content=article.content,
            source=article.source,
            url=article.url,
            published_at=article.published_at or "",
            source_type="manual",
            intelligence=intelligence
        )
        
        await db.commit()
        
        return intelligence
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
