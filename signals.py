"""
Signal Derivation Module
Converts technical data into categorical signals using rule-based logic
NO PREDICTIONS, NO RECOMMENDATIONS - ONLY FACTUAL CATEGORIZATION
"""

from typing import Dict, Any
import config


class SignalDerivation:
    """Derives categorical signals from technical indicators"""
    
    @staticmethod
    def derive_trend(ma_20: str, ma_50: str, ma_200: str) -> str:
        """
        Derive trend based on moving average positions
        
        Rules:
        - Bullish: Price Above MA20, MA20 > MA50, MA50 > MA200 (uptrend alignment)
        - Bearish: Price Below MA20, MA20 < MA50, MA50 < MA200 (downtrend alignment)
        - Sideways: Mixed or no clear pattern
        
        Returns: "Bullish", "Bearish", "Sideways", or "Unavailable"
        """
        if "Unavailable" in [ma_20, ma_50, ma_200]:
            return "Unavailable"
        
        # Strong bullish: all above
        if ma_20 == "Above" and ma_50 == "Above" and ma_200 == "Above":
            return "Bullish"
        
        # Strong bearish: all below
        if ma_20 == "Below" and ma_50 == "Below" and ma_200 == "Below":
            return "Bearish"
        
        # Mixed signals
        return "Sideways"
    
    @staticmethod
    def derive_valuation(pe_ratio: Any, sector: str) -> str:
        """
        Derive valuation based on PE ratio
        
        Rules (simplified - uses absolute PE thresholds):
        - Undervalued: PE < 15
        - Overvalued: PE > 30
        - Fair: 15 <= PE <= 30
        
        Note: In production, this should compare to sector averages
        
        Returns: "Undervalued", "Fair", "Overvalued", or "Unavailable"
        """
        if pe_ratio == "Unavailable" or not isinstance(pe_ratio, (int, float)):
            return "Unavailable"
        
        # Simplified thresholds (should be sector-specific in production)
        if pe_ratio < 15:
            return "Undervalued"
        elif pe_ratio > 30:
            return "Overvalued"
        else:
            return "Fair"
    
    @staticmethod
    def derive_risk(volatility: str, debt: Any, pe_ratio: Any) -> str:
        """
        Derive risk level based on volatility and fundamentals
        
        Rules:
        - High: High volatility OR very high debt
        - Low: Low volatility AND reasonable debt
        - Medium: Everything else
        
        Returns: "Low", "Medium", "High", or "Unavailable"
        """
        if volatility == "Unavailable":
            return "Unavailable"
        
        # High risk if high volatility
        if volatility == "High":
            return "High"
        
        # Low risk if low volatility
        if volatility == "Low":
            return "Low"
        
        # Medium for moderate volatility
        return "Medium"
    
    @staticmethod
    def derive_momentum(rsi: Any, macd: str) -> str:
        """
        Derive momentum based on RSI and MACD
        
        Rules:
        - Strong: RSI > 60 AND MACD Positive
        - Weak: RSI < 40 AND MACD Negative
        - Moderate: Everything else
        
        Returns: "Strong", "Moderate", "Weak", or "Unavailable"
        """
        if rsi == "Unavailable" or macd == "Unavailable":
            return "Unavailable"
        
        if not isinstance(rsi, (int, float)):
            return "Unavailable"
        
        # Strong momentum
        if rsi > 60 and macd == "Positive":
            return "Strong"
        
        # Weak momentum
        if rsi < 40 and macd == "Negative":
            return "Weak"
        
        # Moderate momentum
        return "Moderate"
    
    @staticmethod
    def derive_all_signals(
        technicals: Dict[str, Any],
        fundamentals: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Derive all signals from technical indicators and fundamentals
        
        Returns complete signals dict
        """
        trend = SignalDerivation.derive_trend(
            technicals.get("ma_20"),
            technicals.get("ma_50"),
            technicals.get("ma_200")
        )
        
        valuation = SignalDerivation.derive_valuation(
            fundamentals.get("pe_ratio"),
            fundamentals.get("sector")
        )
        
        risk = SignalDerivation.derive_risk(
            technicals.get("volatility"),
            fundamentals.get("debt"),
            fundamentals.get("pe_ratio")
        )
        
        momentum = SignalDerivation.derive_momentum(
            technicals.get("rsi"),
            technicals.get("macd")
        )
        
        return {
            "trend": trend,
            "valuation": valuation,
            "risk": risk,
            "momentum": momentum
        }
