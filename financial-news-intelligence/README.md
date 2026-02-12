# Financial News Intelligence Engine

A production-grade **FastAPI backend service** that ingests financial news from multiple sources, analyzes content conservatively, and outputs **structured JSON intelligence** without providing investment advice.

## 🎯 Key Features

- **Multi-source ingestion**: NewsAPI, GDELT, RSS feeds, manual input
- **Conservative analysis**: Factual, neutral, no speculation
- **Structured output**: Machine-readable JSON with mandatory format
- **Batch & on-demand**: Scheduled batch processing + real-time analysis
- **Full traceability**: Database storage with audit trails

## 🚫 Strict Compliance

This engine **NEVER**:
- ❌ Provides buy/sell/hold recommendations
- ❌ Predicts prices or returns
- ❌ Speculates beyond article content

Instead, it:
- ✅ Extracts only verifiable facts
- ✅ Marks impact as "Unclear" when insufficient information
- ✅ Maintains neutral, conservative tone

## 📋 Prerequisites

- Python 3.11+
- NewsAPI key ([get one free](https://newsapi.org/register))

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd financial-news-intelligence
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your NewsAPI key:

```env
NEWSAPI_KEY=your_key_here
```

### 3. Run the Server

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at: **http://localhost:8000**

Interactive docs: **http://localhost:8000/docs**

## 📡 API Endpoints

### Analyze Single Article

```bash
POST /api/analyze/article
```

**Example request:**

```json
{
  "headline": "Federal Reserve raises interest rates by 0.25%",
  "content": "The Federal Reserve announced today that it is raising interest rates by 25 basis points to combat inflation...",
  "source": "Reuters",
  "url": "https://example.com/article",
  "published_at": "2026-02-08T10:30:00Z"
}
```

**Example response:**

```json
{
  "headline": "Federal Reserve raises interest rates by 0.25%",
  "source": "Reuters",
  "published_at": "2026-02-08T10:30:00Z",
  "scope": "Global",
  "news_type": "Policy",
  "entities": {
    "countries": ["United States"],
    "sectors": ["Finance", "Banking"],
    "companies": [],
    "indices": ["S&P 500", "NASDAQ"]
  },
  "impact": {
    "direction": "Negative",
    "confidence": 0.75,
    "time_horizon": "Short"
  },
  "facts": [
    "Federal Reserve raised rates by 25 basis points.",
    "New federal funds rate is 5.25%-5.50%."
  ],
  "summary": "The Federal Reserve increased interest rates by 0.25 percentage points to combat inflation..."
}
```

### Batch Ingestion

```bash
POST /api/ingest/batch
```

Trigger background job to fetch and analyze news from configured sources.

### Query Articles

```bash
GET /api/articles?scope=Global&news_type=Policy&page=1&page_size=20
```

Retrieve previously analyzed articles with filters.

### Get Specific Article

```bash
GET /api/articles/{id}
```

## 🗂️ Project Structure

```
financial-news-intelligence/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/
│   │   ├── ingestion/       # News source clients
│   │   └── analysis/        # Analysis modules
│   ├── repositories/        # Data access layer
│   └── api/                 # API routes
├── data/                    # Reference data
├── tests/                   # Unit tests
├── requirements.txt
├── .env
└── docker-compose.yml
```

## 🧪 Testing

Run tests:

```bash
pytest tests/ -v
```

## 🐳 Docker Deployment

```bash
docker-compose up --build
```

## 📊 Output Format

All analyses conform to this mandatory structure:

```json
{
  "headline": "string",
  "source": "string",
  "published_at": "ISO-8601 timestamp",
  "scope": "Global | Country | Sector | Company",
  "news_type": "Macro | Earnings | Policy | Geopolitical | Corporate | Sentiment",
  "entities": {
    "countries": ["array of strings"],
    "sectors": ["array of strings"],
    "companies": ["array of strings"],
    "indices": ["array of strings"]
  },
  "impact": {
    "direction": "Positive | Negative | Neutral | Unclear",
    "confidence": 0.0-1.0,
    "time_horizon": "Short | Medium | Long"
  },
  "facts": ["array of verifiable facts"],
  "summary": "concise neutral summary"
}
```

## 🔧 Configuration

Key settings in `.env`:

- `NEWSAPI_KEY`: Your NewsAPI key
- `DATABASE_URL`: Database connection string
- `RSS_FEEDS`: Comma-separated RSS feed URLs
- `CONFIDENCE_THRESHOLD`: Minimum confidence for definitive impact
- `BATCH_SCHEDULE_INTERVAL`: Seconds between batch runs

## 📝 License

MIT

## 🤝 Support

For issues or questions, please open an issue on GitHub.
