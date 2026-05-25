import google.generativeai as genai
from app.utils.config import get_settings

settings = get_settings()
genai.configure(api_key=settings.google_api_key, transport='rest')

class EmbeddingService:
    def __init__(self):
        self.model = settings.embedding_model

    def get_embedding(self, text: str):
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_query"
        )
        return result['embedding']

    def get_embeddings_batch(self, texts: list[str]):
        result = genai.embed_content(
            model=self.model,
            content=texts,
            task_type="retrieval_document"
        )
        return result['embedding']
