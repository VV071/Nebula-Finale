import pytest
from app.services.analysis.analyzer import NewsAnalyzer
from app.services.analysis.scope_classifier import ScopeClassifier
from app.services.analysis.news_type_classifier import NewsTypeClassifier
from app.services.analysis.impact_analyzer import ImpactAnalyzer


class TestAnalysisEngine:
    """Test suite for analysis engine components."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.analyzer = NewsAnalyzer()
        self.scope_classifier = ScopeClassifier()
        self.news_type_classifier = NewsTypeClassifier()
        self.impact_analyzer = ImpactAnalyzer()
    
    def test_scope_classification_global(self):
        """Test global scope classification."""
        headline = "Global markets rally on economic recovery"
        content = "Stock markets worldwide surged as investors..."
        
        scope = self.scope_classifier.classify(headline, content)
        assert scope == "Global"
    
    def test_scope_classification_company(self):
        """Test company scope classification."""
        headline = "Apple announces record quarterly earnings"
        content = "Apple Inc reported earnings that beat analyst estimates..."
        
        scope = self.scope_classifier.classify(headline, content)
        assert scope == "Company"
    
    def test_news_type_classification_earnings(self):
        """Test earnings news type classification."""
        headline = "Microsoft beats Q4 earnings expectations"
        content = "Microsoft reported quarterly revenue of $60 billion..."
        
        news_type = self.news_type_classifier.classify(headline, content)
        assert news_type == "Earnings"
    
    def test_news_type_classification_policy(self):
        """Test policy news type classification."""
        headline = "Federal Reserve announces interest rate decision"
        content = "The Federal Reserve announced it will raise interest rates..."
        
        news_type = self.news_type_classifier.classify(headline, content)
        assert news_type == "Policy"
    
    def test_impact_analysis_positive(self):
        """Test positive impact detection."""
        headline = "Company reports strong growth and increased profits"
        content = "The company announced robust earnings growth with profit surging 25%..."
        
        impact = self.impact_analyzer.analyze(headline, content, "Earnings")
        assert impact.direction in ["Positive", "Neutral"]
        assert 0.0 <= impact.confidence <= 1.0
    
    def test_impact_analysis_negative(self):
        """Test negative impact detection."""
        headline = "Company misses earnings estimates, stock plunges"
        content = "The company reported disappointing results, with revenue falling short..."
        
        impact = self.impact_analyzer.analyze(headline, content, "Earnings")
        assert impact.direction in ["Negative", "Neutral", "Unclear"]
        assert 0.0 <= impact.confidence <= 1.0
    
    def test_full_analysis(self):
        """Test complete analysis pipeline."""
        headline = "Federal Reserve raises interest rates by 0.25%"
        content = """
        The Federal Reserve announced today that it is raising interest rates 
        by 25 basis points to combat inflation. The decision brings the federal 
        funds rate to 5.25%-5.50%, the highest level in 22 years. The move was 
        unanimous among FOMC members.
        """
        
        intelligence = self.analyzer.analyze(
            headline=headline,
            content=content,
            source="Reuters",
            published_at="2026-02-08T10:00:00Z"
        )
        
        # Validate output structure
        assert intelligence.headline == headline
        assert intelligence.source == "Reuters"
        assert intelligence.scope in ["Global", "Country", "Sector", "Company"]
        assert intelligence.news_type in ["Macro", "Earnings", "Policy", "Geopolitical", "Corporate", "Sentiment"]
        assert isinstance(intelligence.entities.countries, list)
        assert isinstance(intelligence.entities.sectors, list)
        assert isinstance(intelligence.facts, list)
        assert intelligence.impact.direction in ["Positive", "Negative", "Neutral", "Unclear"]
        assert 0.0 <= intelligence.impact.confidence <= 1.0
        assert intelligence.impact.time_horizon in ["Short", "Medium", "Long"]
        assert len(intelligence.summary) > 0
    
    def test_no_investment_advice(self):
        """Verify output contains no investment advice."""
        headline = "Stock market reaches all-time high"
        content = "The S&P 500 index reached a record high today..."
        
        intelligence = self.analyzer.analyze(
            headline=headline,
            content=content,
            source="CNBC",
            published_at="2026-02-08T14:00:00Z"
        )
        
        # Verify no buy/sell language in output
        forbidden_words = ["buy", "sell", "invest", "purchase", "recommend"]
        output_text = (intelligence.summary + " ".join(intelligence.facts)).lower()
        
        for word in forbidden_words:
            assert word not in output_text, f"Found forbidden word: {word}"
