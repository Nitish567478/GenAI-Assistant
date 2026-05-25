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
startup_error = None

def get_rag_service():
    global rag_service
    return rag_service

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, service: RAGService = Depends(get_rag_service)):
    if service is None:
        logging.error("RAGService not initialized")
        detail = "System failed to initialize."
        if startup_error:
            detail = f"{detail} Startup error: {startup_error}"
        raise HTTPException(
            status_code=500, 
            detail=detail,
        )

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
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Error in chat endpoint: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Backend Error: {error_msg}")

@router.get("/health", response_model=HealthResponse)
async def health():
    status = "healthy"
    details = []
    
    if rag_service is None:
        status = "unhealthy"
        details.append("RAGService not initialized")
    if startup_error:
        status = "unhealthy"
        details.append(f"Startup error: {startup_error}")
    
    return HealthResponse(status=status, details=details if details else None)
