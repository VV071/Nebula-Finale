import feedparser
import httpx
from typing import List, Dict, Any
from datetime import datetime
from app.services.ingestion.base_client import BaseNewsClient
from app.config import settings


class RSSParser(BaseNewsClient):
    """Client for parsing RSS feeds from financial news outlets."""
    
    def __init__(self):
        self.feed_urls = settings.rss_feed_list
    
    async def fetch_articles(
        self,
        keywords: List[str] = None,
        date_from: str = None,
        date_to: str = None,
        max_articles: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch articles from configured RSS feeds.
        
        Args:
            keywords: Keywords to filter (applied as post-filter)
            date_from: Start date (YYYY-MM-DD) 
            date_to: End date (YYYY-MM-DD)
            max_articles: Maximum articles to fetch
            
        Returns:
            List of formatted article dictionaries
        """
        articles = []
        
        for feed_url in self.feed_urls[:5]:  # Limit to 5 feeds
            try:
                feed_articles = await self._parse_feed(feed_url, keywords, max_articles)
                articles.extend(feed_articles)
                
                if len(articles) >= max_articles:
                    break
            except Exception as e:
                print(f"RSS feed error for {feed_url}: {e}")
                continue
        
        return articles[:max_articles]
    
    async def _parse_feed(
        self,
        feed_url: str,
        keywords: List[str] = None,
        max_articles: int = 100
    ) -> List[Dict[str, Any]]:
        """Parse a single RSS feed."""
        articles = []
        
        try:
            # Fetch feed
            async with httpx.AsyncClient() as client:
                response = await client.get(feed_url, timeout=15.0)
                response.raise_for_status()
                feed_content = response.text
            
            # Parse with feedparser
            feed = feedparser.parse(feed_content)
            
            for entry in feed.entries[:max_articles]:
                # Apply keyword filter if specified
                if keywords:
                    title_lower = entry.get("title", "").lower()
                    summary_lower = entry.get("summary", "").lower()
                    text = title_lower + " " + summary_lower
                    
                    if not any(kw.lower() in text for kw in keywords):
                        continue
                
                formatted = self._format_rss_entry(entry, feed.feed.get("title", "RSS"))
                if formatted:
                    articles.append(formatted)
            
        except Exception as e:
            print(f"Feed parsing error: {e}")
            pass
        
        return articles
    
    def _format_rss_entry(self, entry: dict, feed_title: str) -> Dict[str, Any]:
        """Format RSS feed entry."""
        # Parse published date
        published_at = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                published_at = datetime(*entry.published_parsed[:6])
            except Exception:
                published_at = datetime.utcnow()
        
        return self._format_article(
            headline=entry.get("title", ""),
            content=entry.get("summary", "") or entry.get("description", ""),
            source=feed_title,
            url=entry.get("link", ""),
            published_at=published_at
        )
