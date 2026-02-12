from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from app.database import Base


class NewsArticle(Base):
    """Database model for storing news articles and their analysis."""
    
    __tablename__ = "news_articles"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Raw article data
    headline = Column(String(500), nullable=False, index=True)
    source = Column(String(100), nullable=False, index=True)
    url = Column(String(1000), unique=True, nullable=True)
    published_at = Column(String(50), nullable=True)
    content = Column(Text, nullable=True)
    
    # Source metadata
    source_type = Column(String(50), nullable=False)  # newsapi, gdelt, rss, manual
    
    # Analysis results
    scope = Column(String(50), nullable=True, index=True)  # Global, Country, Sector, Company
    news_type = Column(String(50), nullable=True, index=True)  # Macro, Earnings, etc.
    
    # JSON fields for complex data
    entities = Column(JSON, nullable=True)  # {countries: [], sectors: [], companies: [], indices: []}
    impact = Column(JSON, nullable=True)  # {direction: str, confidence: float, time_horizon: str}
    facts = Column(JSON, nullable=True)  # List of extracted facts
    
    # Summary
    summary = Column(Text, nullable=True)
    
    # Processing metadata
    processing_status = Column(String(50), default="pending")  # pending, processed, failed
    analysis_version = Column(String(20), default="1.0")
    
    # Audit timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<NewsArticle(id={self.id}, headline='{self.headline[:50]}...', source='{self.source}')>"
