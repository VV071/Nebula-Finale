import json
from pathlib import Path
from typing import Literal
from collections import defaultdict


class NewsTypeClassifier:
    """Classifies news articles by type: Macro, Earnings, Policy, Geopolitical, Corporate, or Sentiment."""
    
    def __init__(self):
        # Load keywords
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        
        with open(data_dir / "keywords.json", "r") as f:
            self.keywords = json.load(f)
    
    def classify(self, headline: str, content: str) -> Literal["Macro", "Earnings", "Policy", "Geopolitical", "Corporate", "Sentiment"]:
        """
        Classify the type of news article.
        
        Args:
            headline: Article headline
            content: Article content
            
        Returns:
            News type classification
        """
        text = (headline + " " + content).lower()
        
        # Count matches for each news type
        scores = defaultdict(int)
        
        for news_type, keywords in self.keywords["news_type"].items():
            for keyword in keywords:
                if keyword.lower() in text:
                    # Give more weight to headline matches
                    if keyword.lower() in headline.lower():
                        scores[news_type] += 2
                    else:
                        scores[news_type] += 1
        
        # Return type with highest score
        if scores:
            best_type = max(scores.items(), key=lambda x: x[1])[0]
            
            # Map to proper case
            type_map = {
                "macro": "Macro",
                "earnings": "Earnings",
                "policy": "Policy",
                "geopolitical": "Geopolitical",
                "corporate": "Corporate",
                "sentiment": "Sentiment"
            }
            return type_map[best_type]
        
        # Default to Sentiment if unclear
        return "Sentiment"
