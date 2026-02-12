from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.repositories.article_repository import ArticleRepository


async def get_article_repository(db: AsyncSession = None) -> ArticleRepository:
    """Dependency for article repository."""
    if db is None:
        async for session in get_db():
            db = session
            break
    return ArticleRepository(db)
