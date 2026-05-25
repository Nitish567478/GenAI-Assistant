import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from app.utils.config import get_settings
from typing import List, Dict

settings = get_settings()

class LLMService:
    def __init__(self):
        self.model_names = self._build_model_list()
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
        last_quota_error = None

        for model_name in self.model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt, generation_config=self.config)
                
                if not response.candidates:
                    return "I'm sorry, I couldn't generate a response. The request might have been blocked by safety filters.", 0

                # In a real production app, we'd handle safety ratings and other attributes
                reply = response.text if response.candidates[0].content.parts else "I'm sorry, I couldn't generate a response."
                tokens_used = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
                
                return reply, tokens_used
            except Exception as e:
                if self._is_quota_error(e):
                    last_quota_error = e
                    continue
                raise e

        retry_hint = self._extract_retry_hint(last_quota_error)
        return (
            "Gemini API quota is temporarily exhausted for this demo. "
            f"Please try again {retry_hint}, or upgrade the Google AI Studio billing/quota for the API key.",
            0,
        )

    def _build_model_list(self) -> List[str]:
        models = [settings.llm_model]
        models.extend(
            model.strip()
            for model in settings.llm_fallback_models.split(",")
            if model.strip()
        )
        return list(dict.fromkeys(models))

    def _is_quota_error(self, error: Exception) -> bool:
        error_text = str(error).lower()
        return isinstance(error, ResourceExhausted) or "429" in error_text or "quota" in error_text

    def _extract_retry_hint(self, error: Exception | None) -> str:
        if error is None:
            return "later"

        error_text = str(error)
        marker = "Please retry in "
        if marker in error_text:
            retry_text = error_text.split(marker, 1)[1].split(".", 1)[0].strip()
            return f"in {retry_text}"

        return "later"

    def _format_history(self, history: List[Dict[str, str]]) -> str:
        formatted = ""
        for msg in history:
            role = "User" if msg['role'] == 'user' else "Assistant"
            formatted += f"{role}: {msg['content']}\n"
        return formatted
