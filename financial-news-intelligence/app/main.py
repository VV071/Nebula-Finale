from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import init_db
from app.api import analyze, ingest, articles, stocks, live
from app.workers.live_monitor import live_monitor

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Financial News Intelligence Engine...")
    await init_db()
    logger.info("Database initialized")
    
    # Start live news monitor
    live_monitor.start()
    logger.info("Live news monitor started (fetching every 5 minutes)")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    live_monitor.stop()


# Create FastAPI application
app = FastAPI(
    title="Financial News Intelligence Engine",
    description="""
    ## Convert financial news into structured, machine-readable intelligence
    
    This API analyzes global and local financial news articles and produces
    structured JSON intelligence **WITHOUT providing investment advice**.
    
    ### Features:
    - **On-demand analysis**: Analyze individual articles via `/api/analyze/article`
    - **Batch ingestion**: Fetch and analyze news from multiple sources
    - **Query interface**: Search analyzed articles with filters
    - **Conservative approach**: Factual analysis only, no speculation
    
    ### Strict Compliance:
    - ❌ No buy/sell/hold recommendations
    - ❌ No price predictions
    - ❌ No speculation beyond article content
    - ✅ Verifiable facts only
    - ✅ "Unclear" impact when insufficient information
    - ✅ Neutral, conservative summaries
    
    ### Data Sources:
    - NewsAPI.org
    - GDELT Project
    - RSS feeds from major financial outlets
    - Manual article input
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(analyze.router)
app.include_router(ingest.router)
app.include_router(articles.router)
app.include_router(stocks.router)
app.include_router(live.router)


@app.get("/", tags=["Root"])
async def root():
    """API root endpoint."""
    return {
        "name": "Financial News Intelligence Engine",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "analyze": "/api/analyze/article",
            "batch_ingest": "/api/ingest/batch",
            "list_articles": "/api/articles",
            "get_article": "/api/articles/{id}"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
