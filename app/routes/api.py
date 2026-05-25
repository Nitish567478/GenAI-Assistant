from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, HealthResponse
from app.services.rag_service import RAGService
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.vectorstore.store import VectorStore
import logging

router = APIRouter()

# Global instances (initialized in main.py)
embedding_service = None
llm_service = None
vector_store = None
rag_service = None

def get_rag_service():
    global rag_service
    return rag_service

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, service: RAGService = Depends(get_rag_service)):
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message field is required")
        
        reply, tokens_used, retrieved_chunks = await service.answer_question(
            request.sessionId, request.message
        )
        
        return ChatResponse(
            reply=reply,
            tokensUsed=tokens_used,
            retrievedChunks=retrieved_chunks
        )
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy")
