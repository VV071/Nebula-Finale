import httpx
import json

def display_latest():
    try:
        response = httpx.get("http://127.0.0.1:8000/api/articles?page_size=5")
        data = response.json()
        articles = data.get("articles", [])
        
        print("\n" + "="*80)
        print(" 📊 LATEST FINANCIAL INTELLIGENCE")
        print("="*80 + "\n")
        
        for article in articles:
            intel = article["intelligence"]
            impact = intel["impact"]
            
            print(f"📰 {intel['headline']}")
            print(f"📍 Scope: {intel['scope']} | Type: {intel['news_type']}")
            print(f"⚡ Impact: {impact['direction']} (Confidence: {impact['confidence']})")
            print(f"📝 {intel['summary'][:200]}...")
            print("-" * 40 + "\n")
            
        if not articles:
            print("No articles found in database. Run 'python fetch_stock_news.py' first!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    display_latest()
