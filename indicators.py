"""
Technical Indicators Module
Rule-based calculations for RSI, MACD, Moving Averages, and Volatility
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
import config


class TechnicalIndicators:
    """Calculates technical indicators using deterministic formulas"""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = None) -> float:
        """
        Calculate Relative Strength Index (RSI)
        
        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss
        
        Returns: RSI value (0-100) or "Unavailable"
        """
        if period is None:
            period = config.RSI_PERIOD
        
        if not prices or len(prices) < period + 1:
            return "Unavailable"
        
        try:
            prices_array = np.array(prices)
            deltas = np.diff(prices_array)
            
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[:period])
            avg_loss = np.mean(losses[:period])
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return round(rsi, 2)
        except Exception as e:
            print(f"Error calculating RSI: {str(e)}")
            return "Unavailable"
    
    @staticmethod
    def calculate_macd(prices: List[float], 
                      fast: int = None, 
                      slow: int = None, 
                      signal: int = None) -> str:
        """
        Calculate MACD and return signal: Positive, Negative, or Neutral
        
        MACD = EMA(fast) - EMA(slow)
        Signal Line = EMA(MACD, signal_period)
        
        Returns: "Positive", "Negative", "Neutral", or "Unavailable"
        """
        if fast is None:
            fast = config.MACD_FAST
        if slow is None:
            slow = config.MACD_SLOW
        if signal is None:
            signal = config.MACD_SIGNAL
        
        if not prices or len(prices) < slow + signal:
            return "Unavailable"
        
        try:
            prices_series = pd.Series(prices)
            
            ema_fast = prices_series.ewm(span=fast, adjust=False).mean()
            ema_slow = prices_series.ewm(span=slow, adjust=False).mean()
            
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal, adjust=False).mean()
            
            macd_value = macd_line.iloc[-1]
            signal_value = signal_line.iloc[-1]
            
            if macd_value > signal_value:
                return "Positive"
            elif macd_value < signal_value:
                return "Negative"
            else:
                return "Neutral"
        except Exception as e:
            print(f"Error calculating MACD: {str(e)}")
            return "Unavailable"
    
    @staticmethod
    def calculate_moving_average(prices: List[float], period: int) -> Optional[float]:
        """
        Calculate Simple Moving Average (SMA)
        
        Returns: MA value or None
        """
        if not prices or len(prices) < period:
            return None
        
        try:
            prices_array = np.array(prices)
            ma = np.mean(prices_array[-period:])
            return round(ma, 2)
        except Exception as e:
            print(f"Error calculating MA: {str(e)}")
            return None
    
    @staticmethod
    def calculate_ma_position(current_price: float, ma_value: Optional[float]) -> str:
        """
        Determine if price is Above or Below moving average
        
        Returns: "Above", "Below", or "Unavailable"
        """
        if current_price == "Unavailable" or ma_value is None:
            return "Unavailable"
        
        return "Above" if current_price > ma_value else "Below"
    
    @staticmethod
    def calculate_volatility(prices: List[float]) -> str:
        """
        Calculate volatility and categorize as Low, Moderate, or High
        Based on standard deviation and coefficient of variation
        
        Returns: "Low", "Moderate", "High", or "Unavailable"
        """
        if not prices or len(prices) < 14:
            return "Unavailable"
        
        try:
            prices_array = np.array(prices)
            returns = np.diff(prices_array) / prices_array[:-1] * 100
            
            # Calculate annualized volatility
            std_dev = np.std(returns)
            volatility = std_dev * np.sqrt(252)  # Annualized
            
            if volatility < config.VOLATILITY_LOW_THRESHOLD:
                return "Low"
            elif volatility < config.VOLATILITY_HIGH_THRESHOLD:
                return "Moderate"
            else:
                return "High"
        except Exception as e:
            print(f"Error calculating volatility: {str(e)}")
            return "Unavailable"
    
    @staticmethod
    def calculate_all_indicators(prices_1y: List[float], current_price: float) -> Dict[str, Any]:
        """
        Calculate all technical indicators
        
        Returns complete technical indicators dict
        """
        # Calculate RSI
        rsi = TechnicalIndicators.calculate_rsi(prices_1y)
        
        # Calculate MACD
        macd = TechnicalIndicators.calculate_macd(prices_1y)
        
        # Calculate Moving Averages
        ma_20 = TechnicalIndicators.calculate_moving_average(prices_1y, config.MA_SHORT)
        ma_50 = TechnicalIndicators.calculate_moving_average(prices_1y, config.MA_MEDIUM)
        ma_200 = TechnicalIndicators.calculate_moving_average(prices_1y, config.MA_LONG)
        
        # Determine MA positions
        ma_20_position = TechnicalIndicators.calculate_ma_position(current_price, ma_20)
        ma_50_position = TechnicalIndicators.calculate_ma_position(current_price, ma_50)
        ma_200_position = TechnicalIndicators.calculate_ma_position(current_price, ma_200)
        
        # Calculate Volatility
        volatility = TechnicalIndicators.calculate_volatility(prices_1y)
        
        return {
            "rsi": rsi,
            "macd": macd,
            "ma_20": ma_20_position,
            "ma_50": ma_50_position,
            "ma_200": ma_200_position,
            "volatility": volatility
        }
