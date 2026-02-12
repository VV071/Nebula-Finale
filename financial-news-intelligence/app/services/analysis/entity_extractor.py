import json
import re
from pathlib import Path
from app.schemas.news_output import Entities


class EntityExtractor:
    """Extracts entities (countries, sectors, companies, indices) from news articles."""
    
    def __init__(self):
        # Load reference data
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        
        with open(data_dir / "countries.json", "r") as f:
            self.countries = json.load(f)
        
        with open(data_dir / "sectors.json", "r") as f:
            self.sectors_data = json.load(f)
        
        with open(data_dir / "indices.json", "r") as f:
            self.indices = json.load(f)
        
        # Create sector keyword mappings
        self.sector_keywords = {}
        for sector, keywords in self.sectors_data.items():
            for keyword in keywords:
                self.sector_keywords[keyword.lower()] = sector
    
    def extract(self, headline: str, content: str) -> Entities:
        """
        Extract entities from article text.
        
        Args:
            headline: Article headline
            content: Article content
            
        Returns:
            Entities object with extracted countries, sectors, companies, and indices
        """
        text = headline + " " + content
        text_lower = text.lower()
        
        # Extract countries
        found_countries = []
        for country in self.countries:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(country.lower()) + r'\b'
            if re.search(pattern, text_lower):
                # Normalize country names (use full name)
                if country in ["USA", "US"]:
                    normalized = "United States"
                elif country in ["UK"]:
                    normalized = "United Kingdom"
                elif country in ["PRC"]:
                    normalized = "China"
                else:
                    normalized = country
                
                if normalized not in found_countries:
                    found_countries.append(normalized)
        
        # Extract sectors
        found_sectors = set()
        for keyword, sector in self.sector_keywords.items():
            if keyword in text_lower:
                found_sectors.add(sector)
        
        # Extract indices
        found_indices = []
        for index in self.indices:
            pattern = r'\b' + re.escape(index.lower()) + r'\b'
            if re.search(pattern, text_lower):
                if index not in found_indices:
                    found_indices.append(index)
        
        # Extract companies (simple heuristic: capitalized words near financial terms)
        # This is a conservative approach - in production, you'd use NER
        found_companies = []
        company_indicators = ["Inc", "Corp", "Ltd", "LLC", "Plc", "AG"]
        
        for indicator in company_indicators:
            pattern = r'([A-Z][a-z]+\s+)+' + re.escape(indicator)
            matches = re.findall(pattern, text)
            for match in matches:
                company = match.strip() + " " + indicator
                if company not in found_companies:
                    found_companies.append(company)
        
        # Limit to most relevant entities
        return Entities(
            countries=found_countries[:5],  # Top 5
            sectors=list(found_sectors)[:5],
            companies=found_companies[:5],
            indices=found_indices[:5]
        )
