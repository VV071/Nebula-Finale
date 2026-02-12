import json
from pathlib import Path
from typing import Literal
from app.schemas.news_output import ImpactAnalysis


class ImpactAnalyzer:
    """Analyzes potential market impact of news articles."""
    
    def __init__(self):
        # Load keywords
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        
        with open(data_dir / "keywords.json", "r") as f:
            self.keywords = json.load(f)
    
    def analyze(self, headline: str, content: str, news_type: str) -> ImpactAnalysis:
        """
        Analyze the market impact of the news article.
        
        Args:
            headline: Article headline
            content: Article content
            news_type: Type of news (for context)
            
        Returns:
            ImpactAnalysis with direction, confidence, and time horizon
        """
        text = (headline + " " + content).lower()
        
        # Determine impact direction
        direction = self._analyze_direction(text, headline.lower())
        
        # Calculate confidence score
        confidence = self._calculate_confidence(text, headline.lower(), direction)
        
        # Determine time horizon
        time_horizon = self._determine_time_horizon(text, news_type)
        
        return ImpactAnalysis(
            direction=direction,
            confidence=round(confidence, 2),
            time_horizon=time_horizon
        )
    
    def _analyze_direction(self, text: str, headline: str) -> Literal["Positive", "Negative", "Neutral", "Unclear"]:
        """Determine impact direction using sentiment keywords."""
        positive_score = 0
        negative_score = 0
        
        # Count positive keywords
        for keyword in self.keywords["impact"]["positive"]:
            count = text.count(keyword.lower())
            # Double weight for headline
            if keyword.lower() in headline:
                positive_score += count * 2
            else:
                positive_score += count
        
        # Count negative keywords
        for keyword in self.keywords["impact"]["negative"]:
            count = text.count(keyword.lower())
            if keyword.lower() in headline:
                negative_score += count * 2
            else:
                negative_score += count
        
        # Count neutral keywords
        neutral_count = sum(1 for kw in self.keywords["impact"]["neutral"] if kw.lower() in text)
        
        # Conservative decision logic
        if neutral_count > 2:
            return "Neutral"
        
        if positive_score > negative_score * 1.5:
            return "Positive"
        elif negative_score > positive_score * 1.5:
            return "Negative"
        elif positive_score == 0 and negative_score == 0:
            return "Unclear"
        else:
            return "Neutral"
    
    def _calculate_confidence(self, text: str, headline: str, direction: str) -> float:
        """Calculate confidence score based on multiple factors."""
        confidence = 0.0
        
        # Factor 1: Language clarity (0.3 weight)
        # Check for specific numeric data
        import re
        numbers = re.findall(r'\d+\.?\d*%|\$\d+|\d+\s*(million|billion|trillion)', text)
        clarity_score = min(len(numbers) / 3, 1.0) * 0.3
        confidence += clarity_score
        
        # Factor 2: Supporting facts (0.3 weight)
        # Sentences with specific information
        sentences = text.split('.')
        specific_sentences = [s for s in sentences if any(char.isdigit() for char in s)]
        facts_score = min(len(specific_sentences) / 5, 1.0) * 0.3
        confidence += facts_score
        
        # Factor 3: Source reliability (0.2 weight)
        # Assume moderate reliability for now (can be enhanced with source scoring)
        source_score = 0.6 * 0.2
        confidence += source_score
        
        # Factor 4: Specificity (0.2 weight)
        # Presence of dates, names, specific events
        specific_terms = ["announced", "reported", "confirmed", "stated", "said"]
        specificity = sum(1 for term in specific_terms if term in text)
        specificity_score = min(specificity / 3, 1.0) * 0.2
        confidence += specificity_score
        
        # Reduce confidence if direction is Unclear
        if direction == "Unclear":
            confidence *= 0.5
        
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def _determine_time_horizon(self, text: str, news_type: str) -> Literal["Short", "Medium", "Long"]:
        """Determine time horizon of impact."""
        # Check for explicit time indicators
        short_count = sum(1 for kw in self.keywords["time_horizon"]["short"] if kw.lower() in text)
        medium_count = sum(1 for kw in self.keywords["time_horizon"]["medium"] if kw.lower() in text)
        long_count = sum(1 for kw in self.keywords["time_horizon"]["long"] if kw.lower() in text)
        
        # Use explicit indicators if available
        if long_count > medium_count and long_count > short_count:
            return "Long"
        elif medium_count > short_count:
            return "Medium"
        elif short_count > 0:
            return "Short"
        
        # Otherwise, infer from news type
        type_horizon_map = {
            "Earnings": "Short",
            "Macro": "Medium",
            "Policy": "Long",
            "Geopolitical": "Long",
            "Corporate": "Medium",
            "Sentiment": "Short"
        }
        
        return type_horizon_map.get(news_type, "Medium")
