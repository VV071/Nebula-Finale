import nltk
from app.services.analysis.scope_classifier import ScopeClassifier
from app.services.analysis.news_type_classifier import NewsTypeClassifier
from app.services.analysis.entity_extractor import EntityExtractor
from app.services.analysis.impact_analyzer import ImpactAnalyzer
from app.services.analysis.fact_extractor import FactExtractor
from app.schemas.news_output import NewsIntelligence


class NewsAnalyzer:
    """
    Main orchestrator for news analysis.
    Coordinates all analysis modules and produces structured intelligence output.
    """
    
    def __init__(self):
        # Initialize all analysis components
        self.scope_classifier = ScopeClassifier()
        self.news_type_classifier = NewsTypeClassifier()
        self.entity_extractor = EntityExtractor()
        self.impact_analyzer = ImpactAnalyzer()
        self.fact_extractor = FactExtractor()
        
        # Ensure NLTK data is available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
    
    def analyze(
        self,
        headline: str,
        content: str,
        source: str,
        published_at: str
    ) -> NewsIntelligence:
        """
        Analyze a news article and produce structured intelligence.
        
        Args:
            headline: Article headline
            content: Full article content
            source: News source name
            published_at: Publication timestamp
            
        Returns:
            NewsIntelligence object with complete analysis
        """
        # Validate inputs
        if not headline or len(headline.strip()) < 10:
            raise ValueError("Headline must be at least 10 characters")
        
        if not content or len(content.strip()) < 50:
            raise ValueError("Content must be at least 50 characters")
        
        # Step 1: Classify scope
        scope = self.scope_classifier.classify(headline, content)
        
        # Step 2: Classify news type
        news_type = self.news_type_classifier.classify(headline, content)
        
        # Step 3: Extract entities
        entities = self.entity_extractor.extract(headline, content)
        
        # Step 4: Analyze impact
        impact = self.impact_analyzer.analyze(headline, content, news_type)
        
        # Step 5: Extract facts
        facts = self.fact_extractor.extract(headline, content)
        
        # Step 6: Generate summary
        summary = self._generate_summary(headline, content, facts)
        
        # Construct and return intelligence
        return NewsIntelligence(
            headline=headline,
            source=source,
            published_at=published_at,
            scope=scope,
            news_type=news_type,
            entities=entities,
            impact=impact,
            facts=facts,
            summary=summary
        )
    
    def _generate_summary(self, headline: str, content: str, facts: list[str]) -> str:
        """
        Generate a concise neutral summary.
        
        Uses the first 2-3 sentences of the article or top facts.
        """
        # Try to use NLTK to get first few sentences
        try:
            sentences = nltk.sent_tokenize(content)
            # Take first 2-3 sentences, up to 300 characters
            summary_parts = []
            char_count = 0
            
            for sentence in sentences[:4]:
                if char_count + len(sentence) < 300:
                    summary_parts.append(sentence)
                    char_count += len(sentence)
                else:
                    break
            
            summary = ' '.join(summary_parts)
            
            # If summary is too short, add from facts
            if len(summary) < 100 and facts:
                summary = summary + " " + facts[0]
            
            return summary.strip()
            
        except Exception:
            # Fallback: use headline + first fact
            if facts:
                return f"{headline} {facts[0]}"
            else:
                return headline[:300]
