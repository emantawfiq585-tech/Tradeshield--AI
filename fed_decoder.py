from groq import Groq
from config import GROQ_API_KEY

class FedDecoder:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
    
    async def analyze_statement(self, text):
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a Federal Reserve policy analyst. Analyze the statement and provide insights about monetary policy, interest rates, inflation, and market implications."},
                    {"role": "user", "content": f"Analyze this Fed statement:\n\n{text}"}
                ],
                max_tokens=500
            )
            return {'success': True, 'analysis': completion.choices[0].message.content}
        except Exception as e:
            return {'success': False, 'error': str(e)}
