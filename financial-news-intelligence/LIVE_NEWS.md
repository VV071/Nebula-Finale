# Live News Streaming - Quick Start Guide

## 🔴 LIVE NEWS IS NOW ENABLED!

Your system now automatically fetches and analyzes news **every 5 minutes** in the background.

## 3 Ways to Monitor Live News

### 1️⃣ Live Terminal Monitor (Recommended)

```bash
# Activate environment
venv\Scripts\activate

# Start live monitor
python live_monitor.py
```

**What you'll see:**
- Real-time article notifications
- Color-coded impact (🟢 Positive / 🔴 Negative / 🟡 Neutral)
- Stats updates every 5 minutes
- WebSocket connection status

### 2️⃣ WebSocket Connection (For Your Apps)

```javascript
// Connect from JavaScript
const ws = new WebSocket('ws://localhost:8000/api/live/stream');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'new_article') {
    console.log('New article:', data.article.headline);
    console.log('Impact:', data.article.impact.direction);
  }
  
  if (data.type === 'stats_update') {
    console.log('Stats:', data.stats);
  }
};
```

### 3️⃣ Check Live Status via API

```bash
# Get current status
curl http://localhost:8000/api/live/status

# Manually trigger immediate fetch
curl -X POST http://localhost:8000/api/live/trigger
```

## How It Works

📡 **Auto-Fetch Schedule:**
- Runs every **5 minutes** automatically
- Fetches from NewsAPI, GDELT, RSS feeds
- Analyzes and stores new articles
- Broadcasts via WebSocket to all connected clients

🎯 **Smart Filtering:**
- Stock market keywords
- Breaking financial news
- Earnings reports
- Economic indicators
- Market movements

⚡ **Real-Time Updates:**
- New articles pushed instantly to subscribers
- Stats updates after each fetch
- Duplicate detection (no repeats)

## Quick Test

1. **Start the server:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

2. **Open another terminal and run:**
   ```bash
   python live_monitor.py
   ```

3. **Watch live news arrive every 5 minutes!** 📰

## Configuration

Edit `app/workers/live_monitor.py`:

```python
# Change fetch interval (default: 5 minutes)
live_monitor = LiveNewsMonitor(interval_minutes=10)  # Every 10 minutes

# Change keywords in fetch_latest_news() method
keywords = ["your", "custom", "keywords"]
```

## WebSocket Message Types

**From Server:**
- `connected`: Initial connection confirmation
- `new_article`: New article analyzed
- `stats_update`: Batch processing stats

**From Client:**
- `ping`: Keep connection alive
- `stats`: Request current statistics

---

**Status:** ✅ Live monitoring is ACTIVE when server is running!
