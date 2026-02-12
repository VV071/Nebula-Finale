import httpx
import asyncio

async def test_gdelt():
    print("Testing GDELT...")
    async with httpx.AsyncClient() as client:
        url = "https://api.gdeltproject.org/api/v2/doc/doc"
        params = {
            "query": "financial markets",
            "mode": "artlist",
            "maxrecords": 5,
            "format": "json"
        }
        
        response = await client.get(url, params=params)
        print(f"Status: {response.status_code}")
        try:
            data = response.json()
            articles = data.get("articles", [])
            print(f"Found {len(articles)} articles")
            for a in articles:
                print(f"- {a['title']}")
        except:
            print(f"Raw response: {response.text[:200]}")

if __name__ == "__main__":
    asyncio.run(test_gdelt())
