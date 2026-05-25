import faiss
import numpy as np
import json
import os
from typing import List, Tuple
from app.models.schemas import DocumentChunk
from app.utils.config import get_settings

settings = get_settings()

class VectorStore:
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product for Cosine Similarity (with normalized vectors)
        self.chunks: List[DocumentChunk] = []

    def add_chunks(self, chunks: List[DocumentChunk], embeddings: List[List[float]]):
        embeddings_np = np.array(embeddings).astype('float32')
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings_np)
        self.index.add(embeddings_np)
        self.chunks.extend(chunks)

    def search(self, query_embedding: List[float], top_k: int = 3, threshold: float = 0.7) -> List[Tuple[DocumentChunk, float]]:
        query_np = np.array([query_embedding]).astype('float32')
        faiss.normalize_L2(query_np)
        
        distances, indices = self.index.search(query_np, top_k)
        
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            score = float(distances[0][i])
            if idx != -1 and score >= threshold:
                chunk = self.chunks[idx]
                chunk.similarity_score = score
                results.append((chunk, score))
        
        return results

    @classmethod
    def load_from_json(cls, file_path: str, embedding_service):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Documents file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            docs = json.load(f)
        
        chunks = []
        texts = []
        chunk_id = 0
        
        for doc in docs:
            # Simple chunking logic (could be improved for very long docs)
            content = doc['content']
            # For this assignment, we'll treat each doc as a chunk if it's small, 
            # or split if it's large. Given the sample docs, they are small.
            chunk = DocumentChunk(
                id=str(chunk_id),
                title=doc['title'],
                content=content,
                source_doc=doc['title']
            )
            chunks.append(chunk)
            texts.append(content)
            chunk_id += 1
            
        embeddings = embedding_service.get_embeddings_batch(texts)
        
        # Dimension for embedding-001 is 768
        instance = cls(dimension=len(embeddings[0]))
        instance.add_chunks(chunks, embeddings)
        return instance
