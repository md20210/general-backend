"""
Bar Chat API Endpoints
Provides RAG-powered chat functionality for Bar Ca l'Elena
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from backend.services.bar_chat_service import bar_chat_service
from backend.services.bar_elasticsearch_service import bar_es_service
from backend.services.bar_service import BarService
from backend.database import get_db
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bar/chat", tags=["Bar Chat"])


class ChatMessage(BaseModel):
    """Chat message model"""
    message: str
    language: str = "en"  # ca, es, en, de, fr
    conversation_history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    context_used: str
    language: str
    llm_provider: str
    success: bool
    error: Optional[str] = None


class IndexStatus(BaseModel):
    """Elasticsearch index status"""
    exists: bool
    document_count: int
    languages: List[str]


@router.post("/message", response_model=ChatResponse)
async def send_message(chat_msg: ChatMessage, db: Session = Depends(get_db)):
    """
    Send a message to the chatbot and get a response

    The chatbot uses RAG (Retrieval-Augmented Generation) to provide
    accurate answers based on bar information in Elasticsearch.

    - **message**: User's question or message
    - **language**: Language code (ca, es, en, de, fr)
    - **conversation_history**: Previous messages for context (optional)

    Note: LLM provider is automatically selected from admin settings
    """
    try:
        # Get LLM provider from admin settings
        settings = BarService.get_settings(db)
        llm_provider = settings.llm_provider if settings else "ollama"

        result = await bar_chat_service.chat(
            message=chat_msg.message,
            language=chat_msg.language,
            llm_provider=llm_provider,
            conversation_history=chat_msg.conversation_history
        )
        return ChatResponse(**result)

    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/create")
async def create_search_index():
    """
    Create Elasticsearch index for bar data

    **Admin only** - Creates the search index with multilingual support
    """
    try:
        success = bar_es_service.create_index()
        if success:
            return {"message": "Index created successfully", "index": bar_es_service.index_name}
        else:
            raise HTTPException(status_code=500, detail="Failed to create index")
    except Exception as e:
        logger.error(f"❌ Error creating index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/populate")
async def populate_search_index(db: Session = Depends(get_db)):
    """
    Populate Elasticsearch index with bar data

    **Admin only** - Indexes all bar information in all languages
    """
    try:
        # Get bar info from database
        bar_info = BarService.get_bar_info(db)
        if not bar_info:
            raise HTTPException(status_code=404, detail="Bar info not found")

        # Convert to dict
        bar_data = {
            "description": bar_info.description,
            "address": bar_info.address,
            "phone": bar_info.phone,
            "cuisine": bar_info.cuisine,
            "price_range": bar_info.price_range,
            "rating": bar_info.rating,
            "location_lat": bar_info.location_lat,
            "location_lng": bar_info.location_lng,
            "opening_hours": bar_info.opening_hours,
            "featured_items": bar_info.featured_items,
            "reviews": bar_info.reviews
        }

        # Index data
        success = bar_es_service.index_bar_info(bar_data)
        if success:
            return {
                "message": "Bar data indexed successfully",
                "index": bar_es_service.index_name,
                "languages": ["ca", "es", "en", "de", "fr"]
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to index data")

    except Exception as e:
        logger.error(f"❌ Error indexing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/index/status", response_model=IndexStatus)
async def get_index_status():
    """
    Get Elasticsearch index status

    Returns information about the current index state
    """
    try:
        if not bar_es_service.es:
            return IndexStatus(
                exists=False,
                document_count=0,
                languages=[]
            )

        # Check if index exists
        exists = bar_es_service.es.indices.exists(index=bar_es_service.index_name)

        if not exists:
            return IndexStatus(
                exists=False,
                document_count=0,
                languages=[]
            )

        # Get document count
        count_response = bar_es_service.es.count(index=bar_es_service.index_name)
        doc_count = count_response.get("count", 0)

        return IndexStatus(
            exists=True,
            document_count=doc_count,
            languages=["ca", "es", "en", "de", "fr"]
        )

    except Exception as e:
        logger.error(f"❌ Error getting index status: {e}")
        return IndexStatus(
            exists=False,
            document_count=0,
            languages=[]
        )


@router.get("/search")
async def search_bar_info(query: str, language: str = "en", limit: int = 5):
    """
    Search bar information

    Test endpoint to search the indexed bar data

    - **query**: Search query
    - **language**: Language code (ca, es, en, de, fr)
    - **limit**: Maximum number of results
    """
    try:
        results = bar_es_service.search(query, language, limit)
        return {
            "query": query,
            "language": language,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class TranslateRequest(BaseModel):
    """Translation request model"""
    text: str
    target_language: str = "en"  # ca, es, en, de, fr


class TranslateResponse(BaseModel):
    """Translation response model"""
    translation: str
    target_language: str
    llm_provider: str
    success: bool
    error: Optional[str] = None


@router.post("/translate", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest, db: Session = Depends(get_db)):
    """
    Translate German text to target language

    Simple translation without RAG context - just translate the input text.

    - **text**: German text to translate
    - **target_language**: Target language code (ca, es, en, de, fr)

    Note: LLM provider is automatically selected from admin settings
    """
    try:
        # Get LLM provider from admin settings
        settings = BarService.get_settings(db)
        llm_provider = settings.llm_provider if settings else "ollama"

        result = await bar_chat_service.translate(
            text=request.text,
            target_language=request.target_language,
            llm_provider=llm_provider
        )
        return TranslateResponse(**result)

    except Exception as e:
        logger.error(f"❌ Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
