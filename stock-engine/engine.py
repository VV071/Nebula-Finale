"""
Stock Knowledge & Fundamentals Engine
Main orchestrator that coordinates data fetching, indicator calculation, and signal derivation
"""

from datetime import datetime
from typing import Dict, Any
from data_fetcher import DataFetcher
from indicators import TechnicalIndicators
from signals import SignalDerivation


class StockEngine:
    """
    Deterministic stock analysis engine
    NO PREDICTIONS, NO RECOMMENDATIONS - ONLY FACTUAL DATA PROCESSING
    """
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
    
    def analyze_stock(self, symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
        """
        Complete stock analysis pipeline
        
        Steps:
        1. Fetch all data (price, history, fundamentals)
        2. Calculate technical indicators
        3. Derive categorical signals
        4. Format and return structured JSON
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE", "AAPL")
            exchange: Exchange name (e.g., "NSE", "BSE", "NASDAQ")
        
        Returns:
            Structured JSON with all stock data
        """
        # Step 1: Fetch all raw data
        raw_data = self.data_fetcher.fetch_all_data(symbol, exchange)
        
        # Extract price data
        current_price = raw_data["price"]["current"]
        change_percent = raw_data["price"]["change_percent"]
        history = raw_data["price"]["history"]
        
        # Extract fundamentals
        fundamentals = raw_data["fundamentals"]
        
        # Step 2: Calculate technical indicators
        prices_1y = history.get("1Y", [])
        
        technicals = TechnicalIndicators.calculate_all_indicators(
            prices_1y, 
            current_price if current_price != "Unavailable" else 0
        )
        
        # Step 3: Derive signals
        signals = SignalDerivation.derive_all_signals(technicals, fundamentals)
        
        # Step 4: Format output
        output = {
            "symbol": symbol,
            "exchange": exchange,
            "price": {
                "current": current_price,
                "change_percent": change_percent,
                "history": history
            },
            "fundamentals": fundamentals,
            "technicals": technicals,
            "signals": signals,
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }
        
        return output
    
    def get_stock_snapshot(self, symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
        """
        Get a quick snapshot without full historical data
        Useful for faster queries when only current data is needed
        """
        # This is the same as analyze_stock for now
        # Can be optimized later to skip historical data fetching if needed
        return self.analyze_stock(symbol, exchange)


def main():
    """CLI entry point for testing"""
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python engine.py <SYMBOL> [EXCHANGE]")
        print("Example: python engine.py RELIANCE NSE")
        print("Example: python engine.py AAPL NASDAQ")
        sys.exit(1)
    
    symbol = sys.argv[1]
    exchange = sys.argv[2] if len(sys.argv) > 2 else "NSE"
    
    engine = StockEngine()
    result = engine.analyze_stock(symbol, exchange)
    
    # Output pure JSON
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
