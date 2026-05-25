import logging
from typing import List, Dict
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.vectorstore.store import VectorStore
from app.utils.config import get_settings

settings = get_settings()

class SessionManager:
    def __init__(self, max_history: int = 5):
        self.history: Dict[str, List[Dict[str, str]]] = {}
        self.max_history = max_history

    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self.history:
            self.history[session_id] = []
        
        self.history[session_id].append({"role": role, "content": content})
        
        # Keep only the last N messages
        if len(self.history[session_id]) > self.max_history * 2:
            self.history[session_id] = self.history[session_id][-self.max_history * 2:]

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        return self.history.get(session_id, [])

class RAGService:
    def __init__(self, embedding_service: EmbeddingService, llm_service: LLMService, vector_store: VectorStore):
        self.embedding_service = embedding_service
        self.llm_service = llm_service
        self.vector_store = vector_store
        self.session_manager = SessionManager()

    async def answer_question(self, session_id: str, question: str):
        try:
            # 1. Embed query
            logging.info(f"Embedding query: {question[:50]}...")
            query_embedding = self.embedding_service.get_embedding(question)
            
            # 2. Retrieve top-k
            logging.info("Searching vector store...")
            results = self.vector_store.search(
                query_embedding, 
                top_k=settings.top_k, 
                threshold=settings.similarity_threshold
            )
            
            # 3. Build context
            context = "\n\n".join([f"Source: {chunk.title}\n{chunk.content}" for chunk, score in results])
            
            # 4. Get history
            history = self.session_manager.get_history(session_id)
            
            # 5. Generate response
            logging.info("Generating LLM response...")
            reply, tokens_used = self.llm_service.generate_response(context, history, question)
            
            # 6. Update history
            self.session_manager.add_message(session_id, "user", question)
            self.session_manager.add_message(session_id, "assistant", reply)
            
            logging.info("Response generated successfully.")
            return reply, tokens_used, len(results)
        except Exception as e:
            logging.error(f"Error in RAGService: {str(e)}")
            raise e
