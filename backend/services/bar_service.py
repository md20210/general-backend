"""
Bar Service for Ca l'Elena
Handles business logic for bar information, menus, news, reservations
"""
from sqlalchemy.orm import Session
from backend.models.bar import BarInfo, BarMenu, BarNews, BarReservation, BarNewsletter
from backend.schemas.bar import (
    BarInfoUpdate, BarMenuCreate, BarNewsCreate,
    BarReservationCreate, BarNewsletterCreate
)
from typing import List, Optional
from datetime import datetime


class BarService:
    """Service class for bar operations"""

    @staticmethod
    def get_bar_info(db: Session) -> Optional[BarInfo]:
        """Get bar general information (should only be one row)"""
        return db.query(BarInfo).first()

    @staticmethod
    def create_or_update_bar_info(db: Session, bar_data: BarInfoUpdate) -> BarInfo:
        """Create or update bar general information"""
        bar_info = db.query(BarInfo).first()

        if not bar_info:
            # Create new
            bar_info = BarInfo(
                name="Ca l'Elena",
                **bar_data.model_dump(exclude_unset=True)
            )
            db.add(bar_info)
        else:
            # Update existing
            for key, value in bar_data.model_dump(exclude_unset=True).items():
                setattr(bar_info, key, value)
            bar_info.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(bar_info)
        return bar_info

    @staticmethod
    def initialize_bar_data(db: Session):
        """Initialize bar data with default values from prompt"""
        bar_info = db.query(BarInfo).first()
        if bar_info:
            return bar_info  # Already initialized

        bar_data = BarInfoUpdate(
            description="Bar Ca l'Elena ist ein traditionelles spanisches Bar-Restaurant mit hausgemachten Gerichten, Tapas, frischem Fisch und Fleisch. Bekannt für gegrillte Sardinen, Spanische Omelette und lokale Weine. Große sonnige Terrasse, freundlicher Service.",
            address="Carrer d'Amadeu Torner, 20, 08902 L'Hospitalet de Llobregat, Barcelona, Spain",
            phone="+34 933 36 50 43",
            opening_hours={
                "Mo-Fr": "07:00-20:00",
                "Sa": "08:00-16:00",
                "So": "Geschlossen"
            },
            cuisine="Spanisch, Tapas, Mediterran",
            price_range="€-€€",
            rating="2.8/5 auf TripAdvisor (12 Bewertungen)",
            facebook_url="https://www.facebook.com/barcalelena/",
            featured_items=[
                {"name": "Fideua", "description": "Traditional Catalan seafood noodle dish"},
                {"name": "Vermut", "description": "Traditional Spanish vermouth"},
                {"name": "Vino", "description": "Local wines"},
                {"name": "Ensalada Con Queso de Cabra", "description": "Salad with goat cheese"},
                {"name": "Huevos Con Bacon", "description": "Eggs with bacon"},
                {"name": "Puding", "description": "Homemade pudding"},
                {"name": "Cafe Con Leche", "description": "Coffee with milk"},
                {"name": "Tarta de Queso", "description": "Cheesecake"}
            ],
            reviews=[
                {
                    "author": "Alan Wiley",
                    "text": "Guter Wert und freundliches Personal.",
                    "rating": 4
                },
                {
                    "author": "Pedro Rojas",
                    "text": "Gute hausgemachte Essen zu guten Preisen.",
                    "rating": 4
                }
            ]
        )

        return BarService.create_or_update_bar_info(db, bar_data)

    # Menu operations
    @staticmethod
    def get_all_menus(db: Session, active_only: bool = True) -> List[BarMenu]:
        """Get all menus"""
        query = db.query(BarMenu)
        if active_only:
            query = query.filter(BarMenu.is_active == True)
        return query.order_by(BarMenu.display_order).all()

    @staticmethod
    def get_menu_by_id(db: Session, menu_id: int) -> Optional[BarMenu]:
        """Get menu by ID"""
        return db.query(BarMenu).filter(BarMenu.id == menu_id).first()

    @staticmethod
    def create_menu(db: Session, menu_data: BarMenuCreate, document_id: Optional[int] = None) -> BarMenu:
        """Create new menu"""
        menu = BarMenu(
            **menu_data.model_dump(),
            document_id=document_id
        )
        db.add(menu)
        db.commit()
        db.refresh(menu)
        return menu

    @staticmethod
    def delete_menu(db: Session, menu_id: int) -> bool:
        """Delete menu"""
        menu = db.query(BarMenu).filter(BarMenu.id == menu_id).first()
        if menu:
            db.delete(menu)
            db.commit()
            return True
        return False

    # News operations
    @staticmethod
    def get_all_news(db: Session, published_only: bool = True, limit: int = 50) -> List[BarNews]:
        """Get all news/announcements"""
        query = db.query(BarNews)
        if published_only:
            query = query.filter(BarNews.is_published == True)
        return query.order_by(BarNews.publish_date.desc()).limit(limit).all()

    @staticmethod
    def get_news_by_id(db: Session, news_id: int) -> Optional[BarNews]:
        """Get news by ID"""
        return db.query(BarNews).filter(BarNews.id == news_id).first()

    @staticmethod
    def create_news(db: Session, news_data: BarNewsCreate) -> BarNews:
        """Create new news/announcement"""
        news = BarNews(**news_data.model_dump())
        db.add(news)
        db.commit()
        db.refresh(news)
        return news

    @staticmethod
    def update_news(db: Session, news_id: int, news_data: BarNewsCreate) -> Optional[BarNews]:
        """Update news"""
        news = db.query(BarNews).filter(BarNews.id == news_id).first()
        if news:
            for key, value in news_data.model_dump().items():
                setattr(news, key, value)
            news.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(news)
        return news

    @staticmethod
    def delete_news(db: Session, news_id: int) -> bool:
        """Delete news"""
        news = db.query(BarNews).filter(BarNews.id == news_id).first()
        if news:
            db.delete(news)
            db.commit()
            return True
        return False

    # Reservation operations
    @staticmethod
    def get_all_reservations(db: Session, limit: int = 100) -> List[BarReservation]:
        """Get all reservations"""
        return db.query(BarReservation).order_by(BarReservation.reservation_date.desc()).limit(limit).all()

    @staticmethod
    def create_reservation(db: Session, reservation_data: BarReservationCreate) -> BarReservation:
        """Create new reservation"""
        reservation = BarReservation(**reservation_data.model_dump())
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
        return reservation

    @staticmethod
    def update_reservation_status(db: Session, reservation_id: int, status: str) -> Optional[BarReservation]:
        """Update reservation status"""
        reservation = db.query(BarReservation).filter(BarReservation.id == reservation_id).first()
        if reservation:
            reservation.status = status
            reservation.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(reservation)
        return reservation

    # Newsletter operations
    @staticmethod
    def get_all_subscribers(db: Session, active_only: bool = True) -> List[BarNewsletter]:
        """Get all newsletter subscribers"""
        query = db.query(BarNewsletter)
        if active_only:
            query = query.filter(BarNewsletter.is_active == True)
        return query.all()

    @staticmethod
    def subscribe_newsletter(db: Session, subscription_data: BarNewsletterCreate) -> BarNewsletter:
        """Subscribe to newsletter"""
        # Check if email already exists
        existing = db.query(BarNewsletter).filter(BarNewsletter.email == subscription_data.email).first()
        if existing:
            # Reactivate if was unsubscribed
            if not existing.is_active:
                existing.is_active = True
                existing.subscribed_at = datetime.utcnow()
                existing.unsubscribed_at = None
                db.commit()
                db.refresh(existing)
            return existing

        # Create new subscription
        subscription = BarNewsletter(**subscription_data.model_dump())
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription

    @staticmethod
    def unsubscribe_newsletter(db: Session, email: str) -> bool:
        """Unsubscribe from newsletter"""
        subscription = db.query(BarNewsletter).filter(BarNewsletter.email == email).first()
        if subscription:
            subscription.is_active = False
            subscription.unsubscribed_at = datetime.utcnow()
            db.commit()
            return True
        return False
