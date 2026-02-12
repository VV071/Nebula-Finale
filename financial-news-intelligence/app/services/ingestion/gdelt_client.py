import httpx
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.services.ingestion.base_client import BaseNewsClient


class GDELTClient(BaseNewsClient):
    """Client for GDELT Project API integration."""
    
    def __init__(self):
        self.base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
    
    async def fetch_articles(
        self,
        keywords: List[str] = None,
        date_from: str = None,
        date_to: str = None,
        max_articles: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch financial news from GDELT.
        
        Args:
            keywords: Keywords to search for
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            max_articles: Maximum articles to fetch
            
        Returns:
            List of formatted article dictionaries
        """
        articles = []
        
        # Build query
        if keywords:
            query = " ".join(keywords)
        else:
            query = "financial markets economy"
        
        # GDELT uses timespan parameter (hours back)
        # Default to last 24 hours
        timespan = "24h"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.base_url,
                    params={
                        "query": query,
                        "mode": "artlist",
                        "maxrecords": min(max_articles, 250),
                        "timespan": timespan,
                        "format": "json"
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                # GDELT returns articles in 'articles' array
                for article in data.get("articles", [])[:max_articles]:
                    formatted = self._format_gdelt_article(article)
                    if formatted:
                        articles.append(formatted)
                
            except Exception as e:
                print(f"GDELT error: {e}")
                pass
        
        return articles
    
    def _format_gdelt_article(self, article: dict) -> Dict[str, Any]:
        """Format GDELT article response."""
        # GDELT provides URL, title, and seendate
        # Content needs to be fetched separately (skip for now, use title as content)
        
        published_at = None
        if article.get("seendate"):
            try:
                # GDELT date format: YYYYMMDDThhmmssZ
                date_str = article["seendate"]
                published_at = datetime.strptime(date_str, "%Y%m%dT%H%M%SZ")
            except Exception:
                published_at = datetime.utcnow()
        
        return self._format_article(
            headline=article.get("title", ""),
            content=article.get("title", ""),  # Limited without full text fetching
            source=article.get("domain", "GDELT"),
            url=article.get("url", ""),
            published_at=published_at
        )
