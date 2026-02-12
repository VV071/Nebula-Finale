"""
Dedicated script to fetch all stock-related news from multiple sources.
Runs batch ingestion with stock-specific keywords.
"""
import httpx
import asyncio
from datetime import datetime, timedelta


async def fetch_stock_news():
    """Fetch comprehensive stock market news."""
    
    print("🔍 Fetching stock-related news from all sources...\n")
    
    # Stock-specific keywords
    stock_keywords = [
        "stock market",
        "stocks",
        "NYSE",
        "NASDAQ",
        "DOW",
        "S&P 500",
        "earnings report",
        "quarterly earnings",
        "IPO",
        "stock price",
        "share price",
        "market rally",
        "market crash",
        "bull market",
        "bear market",
        "dividend",
        "stock buyback"
    ]
    
    # Date range: last 7 days
    date_to = datetime.now().strftime("%Y-%m-%d")
    date_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    async with httpx.AsyncClient() as client:
        # Trigger batch ingestion
        request_data = {
            "source_type": "all",  # NewsAPI, GDELT, RSS
            "keywords": stock_keywords,
            "date_from": date_from,
            "date_to": date_to,
            "max_articles": 200
        }
        
        print(f"📅 Date Range: {date_from} to {date_to}")
        print(f"🔑 Keywords: {', '.join(stock_keywords[:5])}...")
        print(f"📰 Max Articles: 200\n")
        
        try:
            response = await client.post(
                "http://127.0.0.1:8000/api/ingest/batch",
                json=request_data,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            job_id = result.get("job_id")
            print(f"✅ Batch job started: {job_id}")
            print(f"📊 Status: {result.get('status')}\n")
            
            # Poll job status
            print("⏳ Monitoring progress...\n")
            
            while True:
                await asyncio.sleep(3)
                
                status_response = await client.get(
                    f"http://127.0.0.1:8000/api/ingest/status/{job_id}",
                    timeout=10.0
                )
                status_response.raise_for_status()
                status = status_response.json()
                
                current_status = status.get("status")
                total = status.get("total_articles", 0)
                processed = status.get("processed", 0)
                failed = status.get("failed", 0)
                
                print(f"\r📈 Progress: {processed}/{total} processed, {failed} failed ({current_status})", end="", flush=True)
                
                if current_status in ["completed", "failed"]:
                    print()
                    break
            
            if current_status == "completed":
                print(f"\n✅ Successfully processed {processed} stock news articles!")
                print(f"\n📊 View results at: http://127.0.0.1:8000/api/articles")
                
                # Fetch and display sample results
                articles_response = await client.get(
                    "http://127.0.0.1:8000/api/articles?page=1&page_size=5",
                    timeout=10.0
                )
                
                if articles_response.status_code == 200:
                    articles_data = articles_response.json()
                    articles = articles_data.get("articles", [])
                    
                    print(f"\n📰 Sample Articles (showing 5 of {articles_data.get('total', 0)}):\n")
                    
                    for i, article in enumerate(articles[:5], 1):
                        intel = article.get("intelligence", {})
                        print(f"{i}. {intel.get('headline', 'No headline')}")
                        print(f"   Source: {intel.get('source', 'Unknown')}")
                        print(f"   Type: {intel.get('news_type', 'Unknown')} | Scope: {intel.get('scope', 'Unknown')}")
                        print(f"   Impact: {intel.get('impact', {}).get('direction', 'Unknown')} "
                              f"(confidence: {intel.get('impact', {}).get('confidence', 0):.2f})")
                        print()
            else:
                print(f"\n❌ Job failed: {status.get('error', 'Unknown error')}")
                
        except httpx.HTTPError as e:
            print(f"❌ HTTP Error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("=" * 70)
    print("  STOCK NEWS FETCHER - Financial News Intelligence Engine")
    print("=" * 70)
    print()
    
    asyncio.run(fetch_stock_news())
    
    print("\n" + "=" * 70)
    print("✨ Done! Use the API to query specific articles:")
    print("   GET /api/articles?scope=Company&news_type=Earnings")
    print("=" * 70)
