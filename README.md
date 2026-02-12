# Stock Knowledge & Fundamentals Engine

A deterministic, auditable stock data processing engine that serves as a neutral source of truth for stock market data.

## Philosophy

**This engine does NOT:**
- Think, predict, or speculate
- Give Buy/Sell/Hold recommendations
- Use emotional or speculative language
- Invent missing data

**This engine DOES:**
- Collect factual stock data
- Compute technical indicators using standard formulas
- Normalize data into interpretable signals
- Output consistent, machine-readable JSON

## Features

### Data Sources
- **Yahoo Finance**: Real-time and historical price data, company fundamentals
- **NSE India**: Indian stock market data (via Yahoo Finance)

### Price Data
- Current price and percentage change
- Historical prices (1D, 14D, 1Y intervals)

### Fundamentals
- Revenue, Net Profit, Debt
- PE Ratio, Market Capitalization
- Sector/Industry classification

### Technical Indicators (Rule-Based)
- **RSI** (Relative Strength Index)
- **MACD** (Moving Average Convergence Divergence) - Positive/Negative/Neutral
- **Moving Averages** (20, 50, 200) - Above/Below price
- **Volatility** - Low/Moderate/High

### Derived Signals (Factual Categorization)
- **Trend**: Bullish / Bearish / Sideways
- **Valuation**: Undervalued / Fair / Overvalued
- **Risk**: Low / Medium / High
- **Momentum**: Strong / Moderate / Weak

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Clone or navigate to the project directory**
   ```bash
   cd f:\P2\stock-engine
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Copy environment configuration (optional)**
   ```bash
   copy .env.example .env
   ```

## Usage

### CLI Mode

Analyze a stock from the command line:

```bash
# Indian stock (NSE)
python engine.py RELIANCE NSE

# US stock
python engine.py AAPL NASDAQ

# Default to NSE if no exchange specified
python engine.py TCS
```

### Batch Mode

Process multiple stocks at once with rate-limiting:

```bash
# Process specific symbols
python batch_engine.py --symbols RELIANCE,TCS,INFY --exchange NSE

# Process all NSE symbols (Warning: This takes time)
python batch_engine.py --all-nse --limit 10

# Customize delay and output
python batch_engine.py --symbols AAPL,MSFT --exchange NASDAQ --delay 2.0 --output us_stocks.json
```

Options:
- `--symbols`: Comma-separated list of symbols
- `--all-nse`: Fetch all stocks from NSE
- `--limit`: Max number of stocks to process
- `--delay`: Seconds between requests (default 1.0)
- `--output`: Result file name (default batch_results.json)

### REST API Mode

Access the API:
- **Interactive docs**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health
- **Analyze stock**: http://localhost:8000/analyze/RELIANCE?exchange=NSE

### API Endpoints

#### GET /analyze/{symbol}
Complete stock analysis with full data

**Parameters:**
- `symbol` (path): Stock symbol (e.g., RELIANCE, AAPL)
- `exchange` (query, optional): Exchange name (default: NSE)

**Example:**
```bash
curl "http://localhost:8000/analyze/RELIANCE?exchange=NSE"
```

#### GET /snapshot/{symbol}
Quick snapshot (currently same as analyze)

#### POST /analyze
POST endpoint for programmatic access

**Request body:**
```json
{
  "symbol": "RELIANCE",
  "exchange": "NSE"
}
```

## Output Format

All endpoints return JSON in this exact structure:

```json
{
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "price": {
    "current": 2456.75,
    "change_percent": 1.23,
    "history": {
      "1D": [...],
      "14D": [...],
      "1Y": [...]
    }
  },
  "fundamentals": {
    "revenue": 792000000000,
    "net_profit": 72000000000,
    "debt": 150000000000,
    "pe_ratio": 28.5,
    "market_cap": 16600000000000,
    "sector": "Energy"
  },
  "technicals": {
    "rsi": 58.23,
    "macd": "Positive",
    "ma_20": "Above",
    "ma_50": "Above",
    "ma_200": "Below",
    "volatility": "Moderate"
  },
  "signals": {
    "trend": "Sideways",
    "valuation": "Fair",
    "risk": "Medium",
    "momentum": "Moderate"
  },
  "last_updated": "2026-02-08T10:00:00Z"
}
```

### Unavailable Data

If any data is unavailable, it will be explicitly marked as `"Unavailable"`:

```json
{
  "fundamentals": {
    "revenue": "Unavailable",
    "pe_ratio": "Unavailable"
  }
}
```

## Configuration

Edit `.env` file to customize parameters:

```env
# Technical Indicator Parameters
RSI_PERIOD=14
MACD_FAST=12
MACD_SLOW=26
MA_SHORT=20
MA_MEDIUM=50
MA_LONG=200

# Signal Thresholds
RSI_OVERSOLD=30
RSI_OVERBOUGHT=70
VOLATILITY_LOW_THRESHOLD=15
VOLATILITY_HIGH_THRESHOLD=30
```

## Architecture

```
stock-engine/
├── app.py              # FastAPI REST API
├── engine.py           # Main orchestrator + CLI
├── data_fetcher.py     # Yahoo Finance & NSE API integration
├── indicators.py       # Technical indicator calculations
├── signals.py          # Signal derivation logic
├── config.py           # Configuration loader
├── requirements.txt    # Python dependencies
└── .env.example        # Configuration template
```

## Signal Derivation Rules

### Trend Detection
- **Bullish**: Price above all MAs (20, 50, 200)
- **Bearish**: Price below all MAs
- **Sideways**: Mixed MA positions

### Valuation Assessment
- **Undervalued**: PE ratio < 15
- **Overvalued**: PE ratio > 30
- **Fair**: PE ratio between 15-30

### Risk Categorization
- **High**: High volatility
- **Low**: Low volatility
- **Medium**: Moderate volatility

### Momentum Classification
- **Strong**: RSI > 60 AND MACD Positive
- **Weak**: RSI < 40 AND MACD Negative
- **Moderate**: All other conditions

## Examples

### Indian Stocks (NSE)
```bash
python engine.py RELIANCE NSE
python engine.py TCS NSE
python engine.py INFY NSE
```

### US Stocks
```bash
python engine.py AAPL NASDAQ
python engine.py MSFT NASDAQ
python engine.py GOOGL NASDAQ
```

## Limitations

1. **Free data sources**: Using free APIs which may have rate limits
2. **No real-time data**: Prices may be delayed by 15-20 minutes
3. **Limited fundamental data**: Some companies may have incomplete data
4. **Simplified signals**: Production systems should use sector-specific PE comparisons

## License

This is a demonstration project for educational purposes.

## Support

For issues or questions, refer to the source code comments or modify the configuration as needed.
