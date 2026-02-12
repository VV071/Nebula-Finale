from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # API Keys
    newsapi_key: str = ""
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./news_intelligence.db"
    
    # RSS Feeds
    rss_feeds: str = ""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    
    # Rate Limiting (requests per minute)
    newsapi_rate_limit: int = 100
    gdelt_rate_limit: int = 300
    rss_rate_limit: int = 60
    
    # Analysis Settings
    confidence_threshold: float = 0.5
    sentiment_threshold: float = 0.6
    
    # Batch Processing
    batch_schedule_interval: int = 3600  # seconds
    max_articles_per_batch: int = 100
    
    # Logging
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    @property
    def rss_feed_list(self) -> list[str]:
        """Parse RSS feeds from comma-separated string."""
        if not self.rss_feeds:
            return []
        return [url.strip() for url in self.rss_feeds.split(",") if url.strip()]


# Global settings instance
settings = Settings()
