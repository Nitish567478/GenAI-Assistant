import google.generativeai as genai
from app.utils.config import get_settings
from typing import List, Dict

settings = get_settings()

class LLMService:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.llm_model)
        self.config = genai.types.GenerationConfig(
            temperature=0.2,
            max_output_tokens=500,
        )

    def generate_response(self, context: str, history: List[Dict[str, str]], user_question: str):
        prompt = f"""
You are a helpful assistant.

- If the user's message is a greeting or small talk (like 'hi', 'hello', 'how are you?'), respond politely and naturally.
- If the user asks for general programming help, coding snippets (like 'write a python program'), or common knowledge, feel free to use your own knowledge to help them.
- For questions specifically about the company, its policies, or the provided documents, prioritize using the provided context.
- If the question is clearly about a specific document or policy but the context is missing, only then say "I could not find enough information in the knowledge base to answer this question."

Context:
{context if context else "No specific document context found for this query."}

Conversation History:
{self._format_history(history)}

Question:
{user_question}
"""
        try:
            response = self.model.generate_content(prompt, generation_config=self.config)
            
            if not response.candidates:
                return "I'm sorry, I couldn't generate a response. The request might have been blocked by safety filters.", 0

            # In a real production app, we'd handle safety ratings and other attributes
            reply = response.text if response.candidates[0].content.parts else "I'm sorry, I couldn't generate a response."
            tokens_used = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            
            return reply, tokens_used
        except Exception as e:
            raise e

    def _format_history(self, history: List[Dict[str, str]]) -> str:
        formatted = ""
        for msg in history:
            role = "User" if msg['role'] == 'user' else "Assistant"
            formatted += f"{role}: {msg['content']}\n"
        return formatted
