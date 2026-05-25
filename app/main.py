import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import api
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.vectorstore.store import VectorStore
from app.utils.config import get_settings
import os
from dotenv import load_dotenv

load_dotenv()
settings = get_settings()

app = FastAPI(title="GenAI RAG Assistant")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    try:
        api.startup_error = None
        # Initialize services
        api.embedding_service = EmbeddingService()
        api.llm_service = LLMService()
        
        # Load and index documents
        docs_path = os.path.join(os.getcwd(), "docs.json")
        if not os.path.exists(docs_path):
            # Fallback for different working directories
            docs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs.json")
            
        print(f"Loading documents from: {docs_path}")
        api.vector_store = VectorStore.load_from_json(docs_path, api.embedding_service)
        
        api.rag_service = RAGService(
            api.embedding_service, 
            api.llm_service, 
            api.vector_store
        )
        print("Application initialized and documents indexed successfully.")
    except Exception as e:
        api.startup_error = str(e)
        print(f"CRITICAL ERROR DURING STARTUP: {api.startup_error}")

# Include routes
app.include_router(api.router, prefix="/api")

# Serve frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
