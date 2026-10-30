from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import hashlib

class LegalCaseMatcher:
    """Simple TF-IDF based model for finding similar legal cases"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)  # Use unigrams and bigrams
        )
        self.case_vectors = None
        self.case_names = None
        self.case_texts = None  # Store original texts for duplicate detection
        self.case_hashes = None  # Store hashes for quick comparison
    
    def train(self, texts, filenames):
        """
        Train the model on case texts
        
        Args:
            texts: List of case texts
            filenames: List of case filenames
        """
        print("Vectorizing cases...")
        self.case_vectors = self.vectorizer.fit_transform(texts)
        self.case_names = filenames
        self.case_texts = texts
        
        # Create hashes for duplicate detection
        self.case_hashes = []
        for text in texts:
            # Create hash of normalized text (lowercase, stripped)
            normalized = text.lower().strip()
            text_hash = hashlib.md5(normalized.encode()).hexdigest()
            self.case_hashes.append(text_hash)
        
        print("Training complete!")
    
    def find_similar_cases(self, query_text, top_n=5):
        """
        Find similar cases based on query text
        
        Args:
            query_text: Case study input text
            top_n: Number of similar cases to return
            
        Returns:
            List of dictionaries with case names and similarity scores
        """
        if self.case_vectors is None:
            raise ValueError("Model not trained yet!")
        
        # STEP 1: Check for exact duplicates first (normalized comparison)
        query_normalized = query_text.lower().strip()
        query_hash = hashlib.md5(query_normalized.encode()).hexdigest()
        
        exact_matches = []
        for idx, case_hash in enumerate(self.case_hashes):
            if case_hash == query_hash:
                exact_matches.append({
                    'case_name': self.format_case_name(self.case_names[idx]),
                    'similarity_score': 100.0,  # Exact match = 100%
                    'filename': self.case_names[idx],
                    'is_exact_match': True
                })
        
        # If exact matches found, return them first + top similar cases
        if exact_matches:
            remaining_n = top_n - len(exact_matches)
            if remaining_n > 0:
                similar = self._get_tfidf_similar(query_text, top_n=remaining_n, exclude_indices=[self.case_names.index(em['filename']) for em in exact_matches])
                return exact_matches + similar
            else:
                return exact_matches[:top_n]
        
        # STEP 2: If no exact matches, use TF-IDF
        return self._get_tfidf_similar(query_text, top_n=top_n)
    
    def _get_tfidf_similar(self, query_text, top_n=5, exclude_indices=None):
        """Get similar cases using TF-IDF cosine similarity"""
        
        # Transform query text to vector
        query_vector = self.vectorizer.transform([query_text])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.case_vectors).flatten()
        
        # Exclude certain indices if specified
        if exclude_indices:
            for idx in exclude_indices:
                similarities[idx] = -1  # Mark as excluded
        
        # Get top N most similar cases
        top_indices = np.argsort(similarities)[::-1][:top_n]
        
        results = []
        for idx in top_indices:
            if similarities[idx] < 0:  # Skip excluded
                continue
                
            similarity = float(similarities[idx])
            
            # BOOST SCORE: If text is very similar (>80%), boost closer to 100%
            # This helps with documents that are nearly identical but slightly reformatted
            if similarity > 0.75:
                # Boost very similar documents
                similarity = min(0.99, similarity * 1.15)
            
            case_name = self.format_case_name(self.case_names[idx])
            results.append({
                'case_name': case_name,
                'similarity_score': round(similarity * 100, 2),  # Convert to percentage
                'filename': self.case_names[idx],
                'is_exact_match': False
            })
        
        return results
    
    def format_case_name(self, filename):
        """Format filename to readable case name"""
        # Remove .PDF extension
        name = filename.replace('_1.PDF', '').replace('.PDF', '')
        # Replace underscores with spaces
        name = name.replace('_', ' ')
        # Split into title case words
        words = name.split()
        formatted = ' '.join(word.capitalize() for word in words)
        return formatted
