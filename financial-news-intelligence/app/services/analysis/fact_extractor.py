import re
import nltk
from typing import List

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class FactExtractor:
    """Extracts verifiable facts from news articles."""
    
    def __init__(self):
        self.fact_indicators = [
            "announced", "reported", "confirmed", "stated", "said",
            "revealed", "disclosed", "showed", "indicated", "declared"
        ]
    
    def extract(self, headline: str, content: str) -> List[str]:
        """
        Extract verifiable facts from article text.
        
        Args:
            headline: Article headline
            content: Article content
            
        Returns:
            List of extracted facts
        """
        facts = []
        
        # Tokenize into sentences
        try:
            sentences = nltk.sent_tokenize(content)
        except Exception:
            # Fallback to simple split
            sentences = content.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if self._is_factual(sentence):
                # Clean and add to facts
                fact = self._clean_fact(sentence)
                if fact and len(fact) > 20:  # Avoid too short statements
                    facts.append(fact)
        
        # Limit to most important facts (first 10)
        return facts[:10]
    
    def _is_factual(self, sentence: str) -> bool:
        """Determine if a sentence contains factual information."""
        sentence_lower = sentence.lower()
        
        # Must contain a fact indicator
        has_indicator = any(indicator in sentence_lower for indicator in self.fact_indicators)
        
        # Should contain numeric data or specific information
        has_number = bool(re.search(r'\d+', sentence))
        
        # Should not contain speculation words
        speculation_words = ["may", "might", "could", "possibly", "perhaps", "likely", "expected to", "predicted"]
        has_speculation = any(word in sentence_lower for word in speculation_words)
        
        # Should not be a question
        is_question = sentence.strip().endswith('?')
        
        return (has_indicator or has_number) and not has_speculation and not is_question
    
    def _clean_fact(self, sentence: str) -> str:
        """Clean and format a fact sentence."""
        # Remove extra whitespace
        sentence = ' '.join(sentence.split())
        
        # Ensure it ends with a period
        if not sentence.endswith('.'):
            sentence += '.'
        
        # Remove attribution if too verbose (e.g., "according to sources familiar with...")
        # Keep direct quotes though
        if "according to" in sentence.lower() and '"' not in sentence:
            # Simplify
            sentence = re.sub(r'according to [^,\.]+[,\.]', '', sentence, flags=re.IGNORECASE)
            sentence = ' '.join(sentence.split())
        
        return sentence.strip()
