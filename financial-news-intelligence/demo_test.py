"""
Simple demo script to test the Financial News Intelligence Engine.
Run this after starting the server with: uvicorn app.main:app
"""
import httpx
import json
import asyncio


async def test_analyze_article():
    """Test the article analysis endpoint."""
    
    # Sample article about Federal Reserve
    test_article = {
        "headline": "Federal Reserve raises interest rates by 0.25% to combat inflation",
        "content": """
        The Federal Reserve announced today that it is raising interest rates by 25 basis points,
        bringing the federal funds rate to 5.25%-5.50%, the highest level in 22 years.
        The decision was unanimous among FOMC members and signals continued commitment to
        fighting inflation. Fed Chair Jerome Powell stated that the central bank will remain
        data-dependent in future decisions. Economists expect this move to slow economic growth
        in the coming quarters while helping to ease price pressures.
        """,
        "source": "Reuters",
        "url": "https://example.com/fed-rate-hike",
        "published_at": "2026-02-08T14:00:00Z"
    }
    
    async with httpx.AsyncClient() as client:
        print("🔄 Analyzing article...")
        print(f"📰 Headline: {test_article['headline']}\n")
        
        try:
            response = await client.post(
                "http://127.0.0.1:8000/api/analyze/article",
                json=test_article,
                timeout=30.0
            )
            response.raise_for_status()
            
            result = response.json()
            
            print("✅ Analysis Complete!\n")
            print("📊 STRUCTURED INTELLIGENCE OUTPUT:")
            print("=" * 70)
            print(json.dumps(result, indent=2))
            print("=" * 70)
            
            print("\n🎯 Key Insights:")
            print(f"  • Scope: {result['scope']}")
            print(f"  • News Type: {result['news_type']}")
            print(f"  • Impact Direction: {result['impact']['direction']}")
            print(f"  • Confidence: {result['impact']['confidence']:.2f}")
            print(f"  • Time Horizon: {result['impact']['time_horizon']}")
            
            if result['entities']['countries']:
                print(f"  • Affected Countries: {', '.join(result['entities']['countries'])}")
            if result['entities']['sectors']:
                print(f"  • Affected Sectors: {', '.join(result['entities']['sectors'])}")
            
            print(f"\n📝 Summary: {result['summary']}")
            
            print(f"\n✓ Facts Extracted: {len(result['facts'])}")
            for i, fact in enumerate(result['facts'][:3], 1):
                print(f"  {i}. {fact}")
            
            # Verify compliance
            output_text = json.dumps(result).lower()
            forbidden = ["buy", "sell", "recommend", "invest in", "purchase"]
            violations = [word for word in forbidden if word in output_text]
            
            if violations:
                print(f"\n⚠️  WARNING: Found potential investment advice: {violations}")
            else:
                print("\n✅ COMPLIANCE CHECK: No investment advice detected")
            
            return result
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None


async def test_health_check():
    """Test the health check endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8000/health")
        print(f"🏥 Health Check: {response.json()}")


async def main():
    print("🚀 Financial News Intelligence Engine - Demo Test\n")
    
    # Check if server is running
    try:
        await test_health_check()
        print()
    except Exception as e:
        print(f"❌ Server not running. Please start with: uvicorn app.main:app")
        print(f"   Error: {e}\n")
        return
    
    # Test article analysis
    await test_analyze_article()
    
    print("\n✨ Demo complete!")


if __name__ == "__main__":
    asyncio.run(main())
