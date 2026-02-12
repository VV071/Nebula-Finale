import json
from pathlib import Path
from typing import Literal


class ScopeClassifier:
    """Classifies news articles by scope: Global, Country, Sector, or Company."""
    
    def __init__(self):
        # Load reference data
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        
        with open(data_dir / "keywords.json", "r") as f:
            self.keywords = json.load(f)
        
        with open(data_dir / "countries.json", "r") as f:
            self.countries = json.load(f)
    
    def classify(self, headline: str, content: str) -> Literal["Global", "Country", "Sector", "Company"]:
        """
        Classify the scope of the news article.
        
        Args:
            headline: Article headline
            content: Article content
            
        Returns:
            Scope classification
        """
        text = (headline + " " + content).lower()
        
        # Check for global keywords
        global_keywords = self.keywords["scope"]["global"]
        if any(kw in text for kw in global_keywords):
            # Also check if multiple countries are mentioned
            country_count = sum(1 for country in self.countries if country.lower() in text)
            if country_count >= 2:
                return "Global"
        
        # Check for specific companies (mentions of CEO, earnings, quarterly, etc.)
        company_indicators = ["CEO", "CFO", "quarterly", "earnings report", "announces", "launches"]
        if any(indicator.lower() in text for indicator in company_indicators):
            return "Company"
        
        # Check for sector-wide news
        sector_keywords = self.keywords["scope"]["sector"]
        if any(kw in text for kw in sector_keywords):
            return "Sector"
        
        # Check for country-specific news
        country_keywords = self.keywords["scope"]["country"]
        country_count = sum(1 for country in self.countries if country.lower() in text)
        
        if country_count >= 1 or any(kw in text for kw in country_keywords):
            return "Country"
        
        # Default to Global if unclear
        return "Global"
