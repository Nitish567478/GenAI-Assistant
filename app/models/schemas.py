from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    sessionId: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    tokensUsed: Optional[int] = 0
    retrievedChunks: int

class HealthResponse(BaseModel):
    status: str

class DocumentChunk(BaseModel):
    id: str
    title: str
    content: str
    source_doc: str
    similarity_score: Optional[float] = None
