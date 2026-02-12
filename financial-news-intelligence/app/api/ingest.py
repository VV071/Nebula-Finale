from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.news_input import BatchIngestRequest
from app.services.ingestion.newsapi_client import NewsAPIClient
from app.services.ingestion.gdelt_client import GDELTClient
from app.services.ingestion.rss_parser import RSSParser
from app.services.analysis.analyzer import NewsAnalyzer
from app.repositories.article_repository import ArticleRepository
import uuid

router = APIRouter(prefix="/api/ingest", tags=["Ingestion"])

# Job status tracking (in-memory for now)
job_status = {}


@router.post("/batch")
async def trigger_batch_ingest(
    request: BatchIngestRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger batch ingestion from configured news sources.
    
    Starts a background job to fetch and analyze articles from the specified source(s).
    Returns a job ID for status tracking.
    """
    job_id = str(uuid.uuid4())
    job_status[job_id] = {
        "status": "pending",
        "total_articles": 0,
        "processed": 0,
        "failed": 0
    }
    
    # Add background task
    background_tasks.add_task(
        process_batch_ingestion,
        job_id,
        request,
        db
    )
    
    return {
        "job_id": job_id,
        "status": "started",
        "message": f"Batch ingestion started for source: {request.source_type}"
    }


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Get the status of a batch ingestion job.
    """
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job_status[job_id]


async def process_batch_ingestion(
    job_id: str,
    request: BatchIngestRequest,
    db: AsyncSession
):
    """Background task to process batch ingestion."""
    try:
        job_status[job_id]["status"] = "processing"
        
        # Initialize clients
        clients = []
        if request.source_type == "newsapi" or request.source_type == "all":
            clients.append(("newsapi", NewsAPIClient()))
        if request.source_type == "gdelt" or request.source_type == "all":
            clients.append(("gdelt", GDELTClient()))
        if request.source_type == "rss" or request.source_type == "all":
            clients.append(("rss", RSSParser()))
        
        # Initialize analyzer and repository
        analyzer = NewsAnalyzer()
        repo = ArticleRepository(db)
        
        total_articles = 0
        processed = 0
        failed = 0
        
        # Fetch and process articles from each source
        for source_type, client in clients:
            try:
                articles = await client.fetch_articles(
                    keywords=request.keywords,
                    date_from=request.date_from,
                    date_to=request.date_to,
                    max_articles=request.max_articles or 100
                )
                
                total_articles += len(articles)
                job_status[job_id]["total_articles"] = total_articles
                
                for article in articles:
                    try:
                        # Check for duplicates
                        if article.get("url"):
                            existing = await repo.get_by_url(article["url"])
                            if existing:
                                continue
                        
                        # Analyze article
                        intelligence = analyzer.analyze(
                            headline=article["headline"],
                            content=article["content"],
                            source=article["source"],
                            published_at=article["published_at"]
                        )
                        
                        # Store in database
                        await repo.create(
                            headline=article["headline"],
                            content=article["content"],
                            source=article["source"],
                            url=article.get("url"),
                            published_at=article["published_at"],
                            source_type=source_type,
                            intelligence=intelligence
                        )
                        
                        processed += 1
                        job_status[job_id]["processed"] = processed
                        
                    except Exception as e:
                        print(f"Failed to process article: {e}")
                        failed += 1
                        job_status[job_id]["failed"] = failed
                        continue
                
                await db.commit()
                
            except Exception as e:
                print(f"Failed to fetch from {source_type}: {e}")
                continue
        
        job_status[job_id]["status"] = "completed"
        
    except Exception as e:
        job_status[job_id]["status"] = "failed"
        job_status[job_id]["error"] = str(e)
