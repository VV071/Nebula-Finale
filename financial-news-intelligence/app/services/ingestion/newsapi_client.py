import httpx
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.services.ingestion.base_client import BaseNewsClient
from app.config import settings


class NewsAPIClient(BaseNewsClient):
    """Client for NewsAPI.org integration."""
    
    def __init__(self):
        self.api_key = settings.newsapi_key
        self.base_url = "https://newsapi.org/v2"
        self.rate_limit = settings.newsapi_rate_limit
    
    async def fetch_articles(
        self,
        keywords: List[str] = None,
        date_from: str = None,
        date_to: str = None,
        max_articles: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch financial news articles from NewsAPI.
        
        Args:
            keywords: Keywords to search for
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            max_articles: Maximum articles to fetch
            
        Returns:
            List of formatted article dictionaries
        """
        if not self.api_key:
            raise ValueError("NewsAPI key is not configured")
        
        articles = []
        
        # Default to last 7 days if no date range specified
        if not date_from:
            date_from = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
        if not date_to:
            date_to = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Build query
        if keywords:
            query = " OR ".join(keywords)
        else:
            # Default financial keywords
            query = "stock OR market OR economy OR earnings OR GDP"
        
        # Fetch from /everything endpoint
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/everything",
                    params={
                        "q": query,
                        "from": date_from,
                        "to": date_to,
                        "language": "en",
                        "sortBy": "publishedAt",
                        "pageSize": min(max_articles, 100),
                        "apiKey": self.api_key
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "ok":
                    for article in data.get("articles", [])[:max_articles]:
                        # Extract and format article
                        formatted = self._format_newsapi_article(article)
                        if formatted:
                            articles.append(formatted)
                
            except httpx.HTTPError as e:
                print(f"NewsAPI error: {e}")
                # Return empty list on error
                pass
        
        return articles
    
    def _format_newsapi_article(self, article: dict) -> Dict[str, Any]:
        """Format NewsAPI article response."""
        # Skip if no content
        if not article.get("content") or article.get("content") == "[Removed]":
            return None
        
        # Parse published date
        published_at = None
        if article.get("publishedAt"):
            try:
                published_at = datetime.fromisoformat(article["publishedAt"].replace("Z", "+00:00"))
            except Exception:
                published_at = datetime.utcnow()
        
        return self._format_article(
            headline=article.get("title", ""),
            content=article.get("description", "") + " " + article.get("content", ""),
            source=article.get("source", {}).get("name", "Unknown"),
            url=article.get("url", ""),
            published_at=published_at
        )
