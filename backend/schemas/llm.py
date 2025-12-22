"""LLM Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class LLMGenerateRequest(BaseModel):
    """Request schema for LLM text generation."""
    prompt: str = Field(..., description="Text prompt for the LLM")
    provider: str = Field(default="ollama", description="LLM provider (ollama, grok, anthropic)")
    model: Optional[str] = Field(None, description="Model name (provider-specific)")
    temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(default=2000, ge=1, le=100000, description="Maximum tokens to generate")
    timeout: int = Field(default=300, ge=1, le=600, description="Request timeout in seconds (300s default for CPU inference)")


class LLMGenerateResponse(BaseModel):
    """Response schema for LLM text generation."""
    response: str
    provider: str
    model: str
    usage: Dict[str, int]


class LLMEmbedRequest(BaseModel):
    """Request schema for text embeddings."""
    text: str = Field(..., description="Text to embed")
    model: Optional[str] = Field(None, description="Embedding model name")


class LLMEmbedResponse(BaseModel):
    """Response schema for text embeddings."""
    embedding: List[float]
    model: str
    dimensions: int


class LLMModel(BaseModel):
    """Schema for LLM model information."""
    name: str
    provider: str
    description: str


class LLMModelsResponse(BaseModel):
    """Response schema for listing models."""
    models: List[LLMModel]
    total: int
