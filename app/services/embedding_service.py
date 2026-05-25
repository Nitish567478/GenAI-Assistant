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
            task_type="retrieval_query",
            output_dimensionality=settings.embedding_dimensions,
        )
        return result['embedding']

    def get_embeddings_batch(self, texts: list[str]):
        result = genai.embed_content(
            model=self.model,
            content=texts,
            task_type="retrieval_document",
            output_dimensionality=settings.embedding_dimensions,
        )
        return self._extract_batch_embeddings(result)

    def _extract_batch_embeddings(self, result):
        if 'embeddings' in result:
            return result['embeddings']

        embeddings = result.get('embedding')
        if isinstance(embeddings, list) and embeddings and isinstance(embeddings[0], list):
            return embeddings

        raise KeyError(f"Could not find batch embeddings in response keys: {list(result.keys())}")
