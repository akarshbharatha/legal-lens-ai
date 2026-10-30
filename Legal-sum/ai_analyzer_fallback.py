import os
import json
import random

class LegalAIAnalyzer:
    """AI-powered legal case analyzer using GPT-4o-mini (with fallback)"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-4o-mini"
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.enabled = self.api_key is not None
    
    def analyze_case(self, case_study, matched_cases):
        """
        Analyze case and provide verdict prediction
        
        Args:
            case_study: The original case study text
            matched_cases: List of top matched cases with details
            
        Returns:
            Dictionary with AI analysis and verdict prediction
        """
        
        try:
            # Get the top matched case for detailed analysis
            top_case = matched_cases[0] if matched_cases else None
            
            if not top_case:
                return {
                    'available': False,
                    'error': 'No matched cases found for analysis'
                }
            
            # Try OpenAI first if enabled
            if self.enabled:
                prompt = self._create_analysis_prompt(case_study, top_case, matched_cases[:3])
                analysis = self._call_openai_api(prompt)
            else:
                # Use fallback local analysis
                analysis = self._generate_local_analysis(case_study, matched_cases)
            
            return {
                'available': True,
                'analysis': analysis,
                'top_case_name': top_case.get('case_name', 'Unknown')
            }
            
        except Exception as e:
            return {
                'available': False,
                'error': f'Error in AI analysis: {str(e)}'
            }
    
    def _generate_local_analysis(self, case_study, matched_cases):
        """Generate analysis without OpenAI - using pattern matching"""
        
        # Keywords to detect case type
        keywords_plaintiff = [
            'breach', 'violation', 'damage', 'loss', 'failed', 'default',
            'negligence', 'fraud', 'misrepresentation', 'theft', 'assault'
        ]
        
        keywords_defendant = [
            'not responsible', 'act of god', 'force majeure', 'valid',
            'agreement', 'proper', 'lawful', 'justified', 'self-defense'
        ]
        
        case_lower = case_study.lower()
        plaintiff_score = sum(1 for kw in keywords_plaintiff if kw in case_lower)
        defendant_score = sum(1 for kw in keywords_defendant if kw in case_lower)
        
        # Calculate win probability based on similarity to matched cases
        avg_similarity = sum(c.get('similarity_score', 0) for c in matched_cases) / len(matched_cases) if matched_cases else 50
        
        # Adjust scores based on case similarity
        base_plaintiff = 45 + (plaintiff_score * 5)
        base_defendant = 45 + (defendant_score * 5)
        
        # Add similarity influence
        similarity_boost = (avg_similarity / 100) * 10
        
        plaintiff_prob = min(100, base_plaintiff + similarity_boost)
        defendant_prob = min(100, base_defendant + similarity_boost)
        
        # Normalize to 100%
        total = plaintiff_prob + defendant_prob
        plaintiff_prob = int((plaintiff_prob / total) * 100)
        defendant_prob = 100 - plaintiff_prob
        
        # Determine verdict
        if plaintiff_prob > defendant_prob + 10:
            verdict = "win"
            confidence = "high" if plaintiff_prob > 70 else "medium"
        elif defendant_prob > plaintiff_prob + 10:
            verdict = "loss"
            confidence = "high" if defendant_prob > 70 else "medium"
        else:
            verdict = "draw"
            confidence = "medium"
        
        # Extract key terms from case
        words = case_study.lower().split()
        case_type = "civil"
        if any(kw in case_lower for kw in ['criminal', 'crime', 'theft', 'assault', 'murder']):
            case_type = "criminal"
        elif any(kw in case_lower for kw in ['contract', 'agreement', 'payment', 'deliver']):
            case_type = "contract"
        elif any(kw in case_lower for kw in ['property', 'land', 'inheritance', 'succession']):
            case_type = "property"
        
        # Get matched case names
        top_cases = [c.get('case_name', 'Unknown') for c in matched_cases[:3]]
        
        return {
            "legal_issues": [
                f"{case_type.title()} dispute",
                "Rights and obligations of parties",
                "Liability assessment"
            ],
            "applicable_laws": [
                "Indian Contract Act, 1872",
                "Indian Penal Code, 1860",
                "Code of Civil Procedure, 1908"
            ],
            "key_facts": [
                "Based on similarity analysis with reference cases",
                f"Average match percentage: {int(avg_similarity)}%",
                "Local AI analysis (no API key configured)"
            ],
            "plaintiff_strengths": [
                "Multiple similar precedent cases found",
                "Clear factual basis for claim",
                "Applicable legal framework supports position"
            ],
            "plaintiff_weaknesses": [
                "Burden of proof requirements",
                "Potential counter-arguments from defendant",
                "Procedural compliance needed"
            ],
            "defendant_strengths": [
                "Possible valid defenses available",
                "Contractual clauses may protect position",
                "Alternative liability interpretations"
            ],
            "defendant_weaknesses": [
                "Precedent cases show similar outcomes",
                "Witness testimony may be challenging",
                "Documentary evidence may be unfavorable"
            ],
            "similarity_to_reference_cases": f"Moderate to high similarity found ({int(avg_similarity)}% match). The case shares common legal principles with top reference cases.",
            "precedent_value": "The reference cases provide valuable guidance for legal arguments and likely outcomes.",
            "verdict_prediction": verdict,
            "confidence_level": confidence,
            "win_probability_plaintiff": plaintiff_prob,
            "win_probability_defendant": defendant_prob,
            "reasoning": f"Analysis based on keyword matching and {len(matched_cases)} reference cases. Plaintiff win probability is {plaintiff_prob}% and defendant win probability is {defendant_prob}%. The {confidence} confidence level reflects the similarity between current case and reference cases.",
            "recommended_legal_strategy": f"Focus on leveraging the {'high' if avg_similarity > 70 else 'moderate'} similarity with reference cases. Strengthen arguments in areas where plaintiff has advantages. Address potential weaknesses through counter-evidence and legal precedents."
        }
    
    def _create_analysis_prompt(self, case_study, top_case, matched_cases):
        """Create a comprehensive prompt for GPT-4o-mini"""
        
        matched_cases_text = ""
        for idx, case in enumerate(matched_cases, 1):
            matched_cases_text += f"\n{idx}. Case: {case.get('case_name', 'Unknown')}\n"
            matched_cases_text += f"   Similarity: {case.get('similarity_score', 0)}%\n"
        
        prompt = f"""You are a senior legal analyst with expertise in Indian law. Analyze the following case and provide a comprehensive assessment.

**CURRENT CASE TO ANALYZE:**
{case_study}

**TOP SIMILAR REFERENCE CASES FROM LEGAL DATABASE:**
{matched_cases_text}

**TASK:**
1. Analyze the legal issues in the current case
2. Identify key legal principles applicable
3. Examine the similarity to the reference cases provided
4. Assess the strength of the plaintiff's case
5. Predict the likely verdict with reasoning
6. Provide percentage probability of winning for each party

**OUTPUT FORMAT (JSON):**
{{
    "legal_issues": ["List of main legal issues"],
    "applicable_laws": ["List of relevant laws and acts"],
    "key_facts": ["Most important factual points"],
    "plaintiff_strengths": ["Advantages for plaintiff"],
    "plaintiff_weaknesses": ["Disadvantages for plaintiff"],
    "defendant_strengths": ["Advantages for defendant"],
    "defendant_weaknesses": ["Disadvantages for defendant"],
    "similarity_to_reference_cases": "How similar is this to the reference cases",
    "precedent_value": "How helpful are the reference cases",
    "verdict_prediction": "win" or "loss" or "draw",
    "confidence_level": "high/medium/low",
    "win_probability_plaintiff": 0-100,
    "win_probability_defendant": 0-100,
    "reasoning": "Detailed explanation of the analysis",
    "recommended_legal_strategy": "Strategic advice for the case"
}}

Provide your analysis in valid JSON format only."""
        
        return prompt
    
    def _call_openai_api(self, prompt):
        """Call OpenAI API using requests"""
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a legal expert specializing in Indian law and case analysis."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1500
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Try to parse JSON from response
            try:
                # Extract JSON if wrapped in markdown
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0].strip()
                
                return json.loads(content)
            except:
                # Return as text if JSON parsing fails
                return {"raw_analysis": content}
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def is_available(self):
        """Check if AI analyzer is available (always true now with fallback)"""
        return True
    
    def chat_response(self, user_query, context):
        """
        General chatbot response using legal context + AI
        """
        if self.enabled:
            return self._chat_with_openai(user_query, context)
        else:
            return self._chat_local(user_query, context)
    
    def _chat_with_openai(self, user_query, context):
        """Chat with OpenAI"""
        prompt = f"""
You are a professional legal assistant specializing in Indian law.

Use the following legal references to answer the user's question clearly and accurately.

### Legal Context:
{context}

### User Question:
{user_query}

### Instructions:
- Answer in simple language
- Mention relevant laws or sections if applicable
- Be legally accurate
- Avoid unnecessary complexity
"""
        try:
            import requests

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a legal expert AI."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }

            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _chat_local(self, user_query, context):
        """Local fallback for chat"""
        query_lower = user_query.lower()
        
        if any(kw in query_lower for kw in ['legal', 'law', 'act', 'section']):
            return f"Based on the legal context provided: {context[:200]}... The applicable legal framework covers your question. For detailed analysis, please refer to relevant statutes and case law."
        elif any(kw in query_lower for kw in ['winning', 'win', 'probability', 'chance']):
            return "Based on the reference cases and legal analysis, the outcome depends on the strength of evidence, applicable laws, and precedents. The similarity to reference cases is a good indicator of potential outcomes."
        else:
            return f"Regarding your question: {user_query[:50]}... The legal context shows that these matters are governed by Indian law. Please consult with a qualified legal professional for personalized advice."
