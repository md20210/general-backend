"""
Bar Model for Ca l'Elena Bar Website
Stores general information, menus, news, reservations, and newsletter subscriptions
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class BarInfo(Base):
    """General bar information - should have only one row"""
    __tablename__ = "bar_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), default="Ca l'Elena")
    description = Column(JSON)  # Multilingual: {"ca": "...", "es": "...", ...}
    address = Column(String(500))
    phone = Column(String(50))
    opening_hours = Column(JSON)  # {"Mo-Fr": "07:00-20:00", "Sa": "08:00-16:00", ...}
    cuisine = Column(String(255))
    price_range = Column(String(50))
    rating = Column(String(100))
    location_lat = Column(String(50), default="41.359276")
    location_lng = Column(String(50), default="2.124410")
    facebook_url = Column(String(500))

    # Store featured menu items as JSON array
    featured_items = Column(JSON)  # [{"name": "Fideua", "description": "...", ...}]

    # Store reviews as JSON array
    reviews = Column(JSON)  # [{"author": "Alan Wiley", "text": "...", "rating": 4}]

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BarMenu(Base):
    """Bar menus (PDF/DOCX uploads) - links to documents table"""
    __tablename__ = "bar_menus"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))  # "Mittagskarte", "Speisekarte", "Getränkekarte"
    description = Column(Text, nullable=True)
    menu_type = Column(String(100))  # "lunch", "food", "drinks"
    document_id = Column(Integer, nullable=True)  # Reference to documents table
    document_url = Column(String(500), nullable=True)  # If external URL
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BarNews(Base):
    """News and announcements for the bar"""
    __tablename__ = "bar_news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(JSON)  # Multilingual: {"ca": "...", "es": "...", "en": "...", "de": "...", "fr": "..."}
    content = Column(JSON)  # Multilingual: {"ca": "...", "es": "...", "en": "...", "de": "...", "fr": "..."}
    image_url = Column(String(500), nullable=True)
    publish_date = Column(DateTime, default=datetime.utcnow)
    is_published = Column(Boolean, default=True)
    is_event = Column(Boolean, default=False)  # True if this is an event
    event_date = Column(DateTime, nullable=True)  # Event date if is_event=True

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BarReservation(Base):
    """Online reservations"""
    __tablename__ = "bar_reservations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(100))
    reservation_date = Column(DateTime)
    num_guests = Column(Integer)
    message = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, confirmed, cancelled

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BarNewsletter(Base):
    """Newsletter subscriptions"""
    __tablename__ = "bar_newsletter"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    name = Column(String(255), nullable=True)
    language = Column(String(5), default="ca")  # ca, es, en, de, fr
    is_active = Column(Boolean, default=True)
    subscribed_at = Column(DateTime, default=datetime.utcnow)
    unsubscribed_at = Column(DateTime, nullable=True)


class BarSettings(Base):
    """Admin settings for bar chatbot"""
    __tablename__ = "bar_settings"

    id = Column(Integer, primary_key=True, index=True)
    llm_provider = Column(String(50), default="ollama")  # "ollama" or "grok"
    grok_api_key = Column(String(500), nullable=True)
    ollama_model = Column(String(100), default="llama3.2:3b")
    auto_speak_enabled = Column(Boolean, default=True)
    contact_email = Column(String(255), nullable=True)  # Email for contact form submissions
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
