from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime


class BaseNewsClient(ABC):
    """Abstract base class for news source clients."""
    
    @abstractmethod
    async def fetch_articles(
        self,
        keywords: List[str] = None,
        date_from: str = None,
        date_to: str = None,
        max_articles: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch articles from the news source.
        
        Args:
            keywords: List of keywords to filter articles
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            max_articles: Maximum number of articles to fetch
            
        Returns:
            List of article dictionaries with keys:
                - headline: str
                - content: str
                - source: str
                - url: str
                - published_at: str
        """
        pass
    
    def _format_article(
        self,
        headline: str,
        content: str,
        source: str,
        url: str = None,
        published_at: datetime = None
    ) -> Dict[str, Any]:
        """Format article data into standard structure."""
        return {
            "headline": headline,
            "content": content or "",
            "source": source,
            "url": url or "",
            "published_at": published_at.isoformat() if published_at else datetime.utcnow().isoformat()
        }
