"""
Live news monitoring and auto-fetching scheduler.
Automatically fetches news every N minutes and provides live updates.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from app.services.ingestion.newsapi_client import NewsAPIClient
from app.services.ingestion.gdelt_client import GDELTClient
from app.services.ingestion.rss_parser import RSSParser
from app.services.analysis.analyzer import NewsAnalyzer
from app.repositories.article_repository import ArticleRepository
from app.database import AsyncSessionLocal
import logging

logger = logging.getLogger(__name__)


class LiveNewsMonitor:
    """Monitors and fetches live news on a schedule."""
    
    def __init__(self, interval_minutes: int = 5):
        self.scheduler = AsyncIOScheduler()
        self.interval_minutes = interval_minutes
        self.analyzer = NewsAnalyzer()
        self.last_fetch_time = None
        self.total_processed = 0
        self.live_subscribers = []  # WebSocket connections
        
    async def fetch_latest_news(self):
        """Fetch and analyze latest news from all sources."""
        try:
            logger.info("🔄 Fetching latest live news...")
            
            # Stock and financial keywords
            keywords = [
                "stock market", "breaking news", "earnings",
                "market", "stocks", "economy", "Federal Reserve"
            ]
            
            new_articles = []
            
            # Fetch from NewsAPI (most recent)
            try:
                newsapi = NewsAPIClient()
                articles = await newsapi.fetch_articles(
                    keywords=keywords,
                    date_from=(datetime.utcnow() - timedelta(hours=2)).strftime("%Y-%m-%d"),
                    max_articles=20
                )
                new_articles.extend(articles)
                logger.info(f"  NewsAPI: {len(articles)} articles")
            except Exception as e:
                logger.error(f"  NewsAPI error: {e}")
            
            # Fetch from GDELT (real-time)
            try:
                gdelt = GDELTClient()
                articles = await gdelt.fetch_articles(keywords=keywords, max_articles=20)
                new_articles.extend(articles)
                logger.info(f"  GDELT: {len(articles)} articles")
            except Exception as e:
                logger.error(f"  GDELT error: {e}")
            
            # Process articles
            processed_count = 0
            async with AsyncSessionLocal() as db:
                repo = ArticleRepository(db)
                
                for article in new_articles:
                    try:
                        # Check for duplicates
                        if article.get("url"):
                            existing = await repo.get_by_url(article["url"])
                            if existing:
                                continue
                        
                        # Analyze
                        intelligence = self.analyzer.analyze(
                            headline=article["headline"],
                            content=article["content"],
                            source=article["source"],
                            published_at=article["published_at"]
                        )
                        
                        # Store
                        new_article = await repo.create(
                            headline=article["headline"],
                            content=article["content"],
                            source=article["source"],
                            url=article.get("url"),
                            published_at=article["published_at"],
                            source_type="live_monitor",
                            intelligence=intelligence
                        )
                        
                        processed_count += 1
                        self.total_processed += 1
                        
                        # Notify WebSocket subscribers
                        await self._notify_subscribers({
                            "type": "new_article",
                            "article": {
                                "id": new_article.id,
                                "headline": intelligence.headline,
                                "source": intelligence.source,
                                "scope": intelligence.scope,
                                "news_type": intelligence.news_type,
                                "impact": intelligence.impact.model_dump(),
                                "published_at": intelligence.published_at
                            }
                        })
                        
                    except Exception as e:
                        logger.error(f"  Error processing article: {e}")
                        continue
                
                await db.commit()
            
            self.last_fetch_time = datetime.now()
            logger.info(f"✅ Processed {processed_count} new articles (Total: {self.total_processed})")
            
            # Notify stats update
            await self._notify_subscribers({
                "type": "stats_update",
                "stats": {
                    "last_fetch": self.last_fetch_time.isoformat(),
                    "new_articles": processed_count,
                    "total_processed": self.total_processed
                }
            })
            
        except Exception as e:
            logger.error(f"❌ Live fetch error: {e}")
    
    async def _notify_subscribers(self, message: dict):
        """Notify all WebSocket subscribers."""
        if not self.live_subscribers:
            return
        
        # Remove disconnected clients
        disconnected = []
        for websocket in self.live_subscribers:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)
        
        for ws in disconnected:
            self.live_subscribers.remove(ws)
    
    def add_subscriber(self, websocket):
        """Add a WebSocket subscriber."""
        self.live_subscribers.append(websocket)
        logger.info(f"📡 New subscriber added. Total: {len(self.live_subscribers)}")
    
    def remove_subscriber(self, websocket):
        """Remove a WebSocket subscriber."""
        if websocket in self.live_subscribers:
            self.live_subscribers.remove(websocket)
            logger.info(f"📡 Subscriber removed. Total: {len(self.live_subscribers)}")
    
    def start(self):
        """Start the live news monitor."""
        logger.info(f"🚀 Starting live news monitor (interval: {self.interval_minutes} minutes)")
        
        # Schedule periodic fetching
        self.scheduler.add_job(
            self.fetch_latest_news,
            trigger=IntervalTrigger(minutes=self.interval_minutes),
            id="live_news_fetch",
            name="Fetch Latest News",
            replace_existing=True
        )
        
        # Fetch immediately on start
        self.scheduler.add_job(
            self.fetch_latest_news,
            id="initial_fetch",
            name="Initial Fetch"
        )
        
        self.scheduler.start()
        logger.info("✅ Live news monitor started")
    
    def stop(self):
        """Stop the live news monitor."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("🛑 Live news monitor stopped")


# Global instance
live_monitor = LiveNewsMonitor(interval_minutes=1)
