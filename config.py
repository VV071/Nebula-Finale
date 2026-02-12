"""
Configuration module for Stock Knowledge & Fundamentals Engine
Loads environment variables and provides configuration constants
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Technical Indicator Parameters
RSI_PERIOD = int(os.getenv("RSI_PERIOD", "14"))
MACD_FAST = int(os.getenv("MACD_FAST", "12"))
MACD_SLOW = int(os.getenv("MACD_SLOW", "26"))
MACD_SIGNAL = int(os.getenv("MACD_SIGNAL", "9"))
MA_SHORT = int(os.getenv("MA_SHORT", "20"))
MA_MEDIUM = int(os.getenv("MA_MEDIUM", "50"))
MA_LONG = int(os.getenv("MA_LONG", "200"))

# Signal Thresholds
RSI_OVERSOLD = float(os.getenv("RSI_OVERSOLD", "30"))
RSI_OVERBOUGHT = float(os.getenv("RSI_OVERBOUGHT", "70"))
VOLATILITY_LOW_THRESHOLD = float(os.getenv("VOLATILITY_LOW_THRESHOLD", "15"))
VOLATILITY_HIGH_THRESHOLD = float(os.getenv("VOLATILITY_HIGH_THRESHOLD", "30"))
PE_UNDERVALUED_MULTIPLIER = float(os.getenv("PE_UNDERVALUED_MULTIPLIER", "0.8"))
PE_OVERVALUED_MULTIPLIER = float(os.getenv("PE_OVERVALUED_MULTIPLIER", "1.2"))

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Data fetch periods
HISTORICAL_PERIODS = {
    "1D": "1d",
    "14D": "14d",
    "1Y": "1y"
}
