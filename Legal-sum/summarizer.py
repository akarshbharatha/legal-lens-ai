import re
from collections import Counter
import math

class LegalCaseSummarizer:
    """Advanced extractive text summarizer optimized for legal cases"""
    
    def __init__(self):
        self.stop_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
            'this', 'said', 'each', 'which', 'their', 'time', 'if', 'will',
            'about', 'how', 'up', 'out', 'many', 'then', 'them', 'these', 'can',
            'him', 'has', 'been', 'when', 'than', 'its', 'who', 'oil', 'sit',
            'now', 'find', 'down', 'day', 'did', 'get', 'made', 'may', 'said',
            'against', 'upon', 'also'
        }
        
        # Legal keywords with importance weights
        self.legal_keywords = {
            'judgment': 3.0,
            'verdict': 3.0,
            'convicted': 3.0,
            'acquitted': 3.0,
            'order': 2.5,
            'ruling': 3.0,
            'plaintiff': 2.5,
            'defendant': 2.5,
            'petitioner': 2.5,
            'respondent': 2.5,
            'appeal': 2.5,
            'court': 2.0,
            'case': 2.0,
            'evidence': 2.5,
            'witness': 2.5,
            'damages': 2.5,
            'liability': 2.5,
            'breach': 2.5,
            'contract': 2.0,
            'agreement': 2.0,
            'property': 2.0,
            'rights': 2.0,
            'claims': 2.0,
            'law': 1.5,
            'act': 1.5,
            'section': 1.5,
            'statute': 1.5,
            'provision': 1.5,
            'guilty': 3.0,
            'innocent': 3.0,
            'charge': 2.0,
            'charged': 2.0,
            'crime': 2.5,
            'criminal': 2.0,
            'civil': 2.0,
            'penalty': 2.5,
            'fine': 2.5,
            'imprisonment': 2.5,
            'fraud': 2.5,
            'negligence': 2.5,
            'defense': 2.0,
            'prosecution': 2.0,
            'attorney': 1.5,
            'counsel': 1.5,
            'filed': 1.5,
            'hearing': 1.5
        }
    
    def summarize(self, text, max_sentences=3):
        """
        Summarize the input text with improved algorithm
        
        Args:
            text: Input text to summarize
            max_sentences: Maximum number of sentences in summary
            
        Returns:
            Summarized text
        """
        if not text or len(text.strip()) < 50:
            return text
        
        # Clean and split into sentences
        sentences = self._split_into_sentences(text)
        
        if len(sentences) <= max_sentences:
            return text
        
        # Calculate comprehensive sentence scores
        sentence_scores = self._calculate_advanced_scores(sentences, text)
        
        # Get top sentences
        top_indices = sorted(range(len(sentences)), 
                            key=lambda i: sentence_scores[i], 
                            reverse=True)[:max_sentences]
        
        # Sort by original position to maintain flow
        top_indices = sorted(top_indices)
        
        # Join sentences
        summary = ' '.join([sentences[i] for i in top_indices])
        
        return summary
    
    def _split_into_sentences(self, text):
        """Split text into sentences with better handling"""
        # Clean the text
        text = re.sub(r'\s+', ' ', text)
        
        # Split by sentence endings
        sentences = re.split(r'[.!?]\s+', text)
        
        # Filter out very short sentences and clean
        sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
        
        return sentences
    
    def _calculate_advanced_scores(self, sentences, full_text):
        """Calculate advanced importance scores for each sentence"""
        scores = []
        
        # Calculate word frequencies
        word_freq = self._word_frequency(sentences)
        
        # Calculate TF-IDF-like scores
        for idx, sentence in enumerate(sentences):
            score = 0
            words = self._extract_words(sentence)
            
            if len(words) == 0:
                scores.append(0)
                continue
            
            # 1. WORD FREQUENCY SCORE (30% weight)
            freq_score = 0
            for word in words:
                if word in word_freq:
                    freq_score += word_freq[word]
            freq_score = (freq_score / len(words)) * 30 if len(words) > 0 else 0
            
            # 2. LEGAL KEYWORD SCORE (40% weight)
            keyword_score = 0
            for word in words:
                if word.lower() in self.legal_keywords:
                    keyword_score += self.legal_keywords[word.lower()]
            keyword_score = min(40, (keyword_score / len(words)) * 40) if len(words) > 0 else 0
            
            # 3. POSITION SCORE (20% weight) - First and last sentences are important
            if idx == 0:
                position_score = 20  # First sentence
            elif idx == len(sentences) - 1:
                position_score = 15  # Last sentence
            else:
                position_score = max(0, 10 - (idx * 0.5))
            
            # 4. SENTENCE LENGTH SCORE (10% weight) - Balanced length
            word_count = len(words)
            if 10 <= word_count <= 30:
                length_score = 10
            elif word_count > 30:
                length_score = 5
            else:
                length_score = 3
            
            # Combine all scores
            total_score = freq_score + keyword_score + position_score + length_score
            scores.append(total_score)
        
        return scores
    
    def _extract_words(self, text):
        """Extract and filter words from text"""
        # Convert to lowercase and extract words
        words = re.findall(r'\b\w+\b', text.lower())
        # Remove stop words and short words
        words = [w for w in words if w not in self.stop_words and len(w) > 2]
        return words
    
    def _word_frequency(self, sentences):
        """Calculate normalized word frequency across all sentences"""
        word_freq = Counter()
        
        for sentence in sentences:
            words = self._extract_words(sentence)
            word_freq.update(words)
        
        # Normalize frequencies (TF normalization)
        if word_freq:
            max_freq = max(word_freq.values())
            word_freq = {word: (freq / max_freq) for word, freq in word_freq.items()}
        
        return word_freq
    
    def summarize_case_study(self, case_text, max_sentences=3):
        """
        Summarize a case study text optimized for legal analysis
        
        Args:
            case_text: The case study text to summarize
            max_sentences: Number of sentences in summary
            
        Returns:
            Summarized case study with key information
        """
        # Use advanced summarization
        return self.summarize(case_text, max_sentences)
    
    def extract_key_points(self, text):
        """Extract bullet-point style key information from text"""
        sentences = self._split_into_sentences(text)
        
        if not sentences:
            return []
        
        # Get top 3-5 key sentences
        num_points = min(5, max(3, len(sentences) // 3))
        sentence_scores = self._calculate_advanced_scores(sentences, text)
        
        top_indices = sorted(range(len(sentences)), 
                            key=lambda i: sentence_scores[i], 
                            reverse=True)[:num_points]
        
        # Sort by original position
        top_indices = sorted(top_indices)
        
        # Extract key points
        key_points = [sentences[i].strip() for i in top_indices]
        return key_points
