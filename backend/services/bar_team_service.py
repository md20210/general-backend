"""
Bar Team Service - Business logic for team members
"""
from sqlalchemy.orm import Session
from backend.models.bar import BarTeam
from backend.schemas.bar import BarTeamCreate, BarTeamUpdate
from typing import List, Optional


class BarTeamService:
    """Service for managing bar team members"""

    @staticmethod
    def get_all_team_members(db: Session, published_only: bool = False) -> List[BarTeam]:
        """Get all team members"""
        query = db.query(BarTeam).order_by(BarTeam.display_order, BarTeam.created_at)

        if published_only:
            query = query.filter(BarTeam.is_published == True)

        return query.all()

    @staticmethod
    def get_team_member(db: Session, team_id: int) -> Optional[BarTeam]:
        """Get a single team member by ID"""
        return db.query(BarTeam).filter(BarTeam.id == team_id).first()

    @staticmethod
    def create_team_member(db: Session, team_data: BarTeamCreate) -> BarTeam:
        """Create a new team member"""
        team_member = BarTeam(
            name=team_data.name,
            description=team_data.description,
            image=team_data.image,
            display_order=team_data.display_order,
            is_published=team_data.is_published
        )
        db.add(team_member)
        db.commit()
        db.refresh(team_member)
        return team_member

    @staticmethod
    def update_team_member(db: Session, team_id: int, team_data: BarTeamUpdate) -> Optional[BarTeam]:
        """Update an existing team member"""
        team_member = db.query(BarTeam).filter(BarTeam.id == team_id).first()
        if not team_member:
            return None

        update_data = team_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(team_member, field, value)

        db.commit()
        db.refresh(team_member)
        return team_member

    @staticmethod
    def delete_team_member(db: Session, team_id: int) -> bool:
        """Delete a team member"""
        team_member = db.query(BarTeam).filter(BarTeam.id == team_id).first()
        if not team_member:
            return False

        db.delete(team_member)
        db.commit()
        return True
