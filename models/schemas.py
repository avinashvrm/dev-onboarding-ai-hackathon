from pydantic import BaseModel
from typing import List, Optional

class TopicListResponse(BaseModel):
    topics: List[str]

class RAGQueryRequest(BaseModel):
    topic_id: str
    query: str

class RAGSearchRequest(BaseModel):
    query: str

class RAGResponse(BaseModel):
    context: str

class IngestResponse(BaseModel):
    status: str
    message: str 