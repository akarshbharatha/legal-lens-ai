from nlp_model import LegalCaseMatcher
from summarizer import LegalCaseSummarizer
from ai_analyzer import LegalAIAnalyzer

class LegalChatbot:
    def __init__(self, trained_model):
        self.matcher = trained_model
        self.summarizer = LegalCaseSummarizer()
        self.ai = LegalAIAnalyzer()

    def get_response(self, user_query):
        if not user_query.strip():
            return "Please enter a legal question."

        # Step 1: Find similar cases
        results = self.matcher.find_similar_cases(user_query, top_n=3)

        if not results:
            return "I could not find relevant legal cases for your question."

        # Step 2: Build context from PDF cases
        context = ""
        for case in results:
            context += f"""
Case Name: {case.get('case_name', 'Unknown')}
Summary: {case.get('summary', 'No summary available')}
Similarity Score: {case.get('similarity_score', 0)}%
"""

        # Step 3: Ask AI
        if self.ai.is_available():
            return self.ai.chat_response(user_query, context)

        return "AI service is currently unavailable."
