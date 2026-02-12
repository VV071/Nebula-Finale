"""
Data Fetcher Module
Handles fetching live and historical stock data from Yahoo Finance and NSE India
"""

import yfinance as yf
from nsepython import *
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import config


class DataFetcher:
    """Fetches stock data from Yahoo Finance and NSE India APIs"""
    
    def __init__(self):
        self.yahoo_suffix_map = {
            "NSE": ".NS",
            "BSE": ".BO"
        }
    
    def _format_symbol_for_yahoo(self, symbol: str, exchange: str) -> str:
        """Format symbol for Yahoo Finance API"""
        if exchange in ["NSE", "BSE"]:
            suffix = self.yahoo_suffix_map.get(exchange, ".NS")
            if not symbol.endswith(suffix):
                return f"{symbol}{suffix}"
        return symbol
    
    def fetch_current_price(self, symbol: str, exchange: str) -> Dict[str, Any]:
        """
        Fetch current price and percentage change
        
        Returns:
            {
                "current": float,
                "change_percent": float
            }
        """
        try:
            formatted_symbol = self._format_symbol_for_yahoo(symbol, exchange)
            ticker = yf.Ticker(formatted_symbol)
            info = ticker.info
            
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            previous_close = info.get('previousClose')
            
            if current_price is None or previous_close is None:
                return {
                    "current": "Unavailable",
                    "change_percent": "Unavailable"
                }
            
            change_percent = ((current_price - previous_close) / previous_close) * 100
            
            return {
                "current": round(current_price, 2),
                "change_percent": round(change_percent, 2)
            }
        except Exception as e:
            print(f"Error fetching current price for {symbol}: {str(e)}")
            return {
                "current": "Unavailable",
                "change_percent": "Unavailable"
            }
    
    def fetch_historical_prices(self, symbol: str, exchange: str) -> Dict[str, List[float]]:
        """
        Fetch historical prices for 1D, 14D, and 1Y periods
        
        Returns:
            {
                "1D": [prices],
                "14D": [prices],
                "1Y": [prices]
            }
        """
        try:
            formatted_symbol = self._format_symbol_for_yahoo(symbol, exchange)
            ticker = yf.Ticker(formatted_symbol)
            
            # Fetch different periods
            history_1d = ticker.history(period="1d", interval="5m")
            history_14d = ticker.history(period="14d", interval="1d")
            history_1y = ticker.history(period="1y", interval="1d")
            
            return {
                "1D": history_1d['Close'].tolist() if not history_1d.empty else [],
                "14D": history_14d['Close'].tolist() if not history_14d.empty else [],
                "1Y": history_1y['Close'].tolist() if not history_1y.empty else []
            }
        except Exception as e:
            print(f"Error fetching historical prices for {symbol}: {str(e)}")
            return {
                "1D": [],
                "14D": [],
                "1Y": []
            }
    
    def fetch_fundamentals(self, symbol: str, exchange: str) -> Dict[str, Any]:
        """
        Fetch company fundamentals
        
        Returns:
            {
                "revenue": float,
                "net_profit": float,
                "debt": float,
                "pe_ratio": float,
                "market_cap": float,
                "sector": str
            }
        """
        try:
            formatted_symbol = self._format_symbol_for_yahoo(symbol, exchange)
            ticker = yf.Ticker(formatted_symbol)
            info = ticker.info
            
            # Get financial data
            revenue = info.get('totalRevenue', 'Unavailable')
            
            # Try to get net income from financials
            net_profit = info.get('netIncomeToCommon', 'Unavailable')
            
            # Get debt
            total_debt = info.get('totalDebt', 'Unavailable')
            
            # Get PE ratio
            pe_ratio = info.get('trailingPE') or info.get('forwardPE', 'Unavailable')
            
            # Get market cap
            market_cap = info.get('marketCap', 'Unavailable')
            
            # Get sector
            sector = info.get('sector', 'Unavailable')
            
            return {
                "revenue": revenue if revenue != 'Unavailable' else "Unavailable",
                "net_profit": net_profit if net_profit != 'Unavailable' else "Unavailable",
                "debt": total_debt if total_debt != 'Unavailable' else "Unavailable",
                "pe_ratio": round(pe_ratio, 2) if isinstance(pe_ratio, (int, float)) else "Unavailable",
                "market_cap": market_cap if market_cap != 'Unavailable' else "Unavailable",
                "sector": sector
            }
        except Exception as e:
            print(f"Error fetching fundamentals for {symbol}: {str(e)}")
            return {
                "revenue": "Unavailable",
                "net_profit": "Unavailable",
                "debt": "Unavailable",
                "pe_ratio": "Unavailable",
                "market_cap": "Unavailable",
                "sector": "Unavailable"
            }
    
    def fetch_all_data(self, symbol: str, exchange: str) -> Dict[str, Any]:
        """
        Fetch all data for a stock symbol
        
        Returns complete dataset including price, history, and fundamentals
        """
        price_data = self.fetch_current_price(symbol, exchange)
        historical_data = self.fetch_historical_prices(symbol, exchange)
        fundamentals_data = self.fetch_fundamentals(symbol, exchange)
        
        return {
            "symbol": symbol,
            "exchange": exchange,
            "price": {
                "current": price_data["current"],
                "change_percent": price_data["change_percent"],
                "history": historical_data
            },
            "fundamentals": fundamentals_data
        }
