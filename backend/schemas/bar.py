"""
Pydantic schemas for Bar API
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


class FeaturedItemSchema(BaseModel):
    """Featured menu item"""
    name: str
    description: Optional[str] = None
    price: Optional[str] = None


class ReviewSchema(BaseModel):
    """Customer review"""
    author: str
    text: str
    rating: Optional[int] = None


class BarInfoResponse(BaseModel):
    """Response schema for bar general information"""
    id: int
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    opening_hours: Optional[Dict[str, str]] = None
    cuisine: Optional[str] = None
    price_range: Optional[str] = None
    rating: Optional[str] = None
    location_lat: Optional[str] = None
    location_lng: Optional[str] = None
    facebook_url: Optional[str] = None
    featured_items: Optional[List[Dict[str, Any]]] = None
    reviews: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class BarInfoUpdate(BaseModel):
    """Schema for updating bar information"""
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    opening_hours: Optional[Dict[str, str]] = None
    cuisine: Optional[str] = None
    price_range: Optional[str] = None
    rating: Optional[str] = None
    facebook_url: Optional[str] = None
    featured_items: Optional[List[Dict[str, Any]]] = None
    reviews: Optional[List[Dict[str, Any]]] = None


class BarMenuResponse(BaseModel):
    """Response schema for bar menu"""
    id: int
    title: str
    description: Optional[str] = None
    menu_type: str
    document_id: Optional[int] = None
    document_url: Optional[str] = None
    is_active: bool
    display_order: int
    created_at: datetime

    class Config:
        from_attributes = True


class BarMenuCreate(BaseModel):
    """Schema for creating a new menu"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    menu_type: str = Field(..., pattern="^(lunch|food|drinks|other)$")
    document_url: Optional[str] = None
    display_order: int = 0


class BarNewsResponse(BaseModel):
    """Response schema for bar news"""
    id: int
    title: str
    content: str
    image_url: Optional[str] = None
    publish_date: datetime
    is_published: bool
    is_event: bool
    event_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BarNewsCreate(BaseModel):
    """Schema for creating news/announcement"""
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    image_url: Optional[str] = None
    is_published: bool = True
    is_event: bool = False
    event_date: Optional[datetime] = None


class BarReservationResponse(BaseModel):
    """Response schema for reservation"""
    id: int
    name: str
    email: str
    phone: str
    reservation_date: datetime
    num_guests: int
    message: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class BarReservationCreate(BaseModel):
    """Schema for creating a reservation"""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=5, max_length=100)
    reservation_date: datetime
    num_guests: int = Field(..., ge=1, le=50)
    message: Optional[str] = None


class BarNewsletterResponse(BaseModel):
    """Response schema for newsletter subscription"""
    id: int
    email: str
    name: Optional[str] = None
    is_active: bool
    subscribed_at: datetime

    class Config:
        from_attributes = True


class BarNewsletterCreate(BaseModel):
    """Schema for newsletter subscription"""
    email: EmailStr
    name: Optional[str] = Field(None, max_length=255)


class AdminLoginRequest(BaseModel):
    """Admin login request"""
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    """Admin login response"""
    access_token: str
    token_type: str = "bearer"


class LLMSelectRequest(BaseModel):
    """LLM selection request"""
    llm_provider: str = Field(..., pattern="^(ollama|grok)$")


class LLMSelectResponse(BaseModel):
    """LLM selection response"""
    llm_provider: str
    message: str
