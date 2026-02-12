import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_newsapi():
    api_key = os.getenv("NEWSAPI_KEY")
    print(f"Testing with key: {api_key[:5]}...")
    
    async with httpx.AsyncClient() as client:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": "stocks",
            "language": "en",
            "pageSize": 5,
            "apiKey": api_key
        }
        
        response = await client.get(url, params=params)
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if data.get("status") == "ok":
            articles = data.get("articles", [])
            print(f"Found {len(articles)} articles")
            for a in articles:
                print(f"- {a['title']}")
        else:
            print(f"Error: {data.get('message')}")

if __name__ == "__main__":
    asyncio.run(test_newsapi())
