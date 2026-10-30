from datetime import datetime
from decimal import Decimal
from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Index, Numeric, String, text
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import Mapped, mapped_column
from app.common.database import Base

class QuestTask(Base):
    __tablename__ = 'quest_task'
    __table_args__ = (
        CheckConstraint("category IN ('delivery','study','repair','other')", name='ck_quest_category'),
        CheckConstraint("status IN ('open','accepted','submitted','completed','cancelled')", name='ck_quest_status'),
        CheckConstraint('reward BETWEEN 0 AND 9999.99', name='ck_quest_reward'),
        CheckConstraint('assignee_id IS NULL OR assignee_id <> owner_id', name='ck_quest_assignee'),
        Index('ix_quest_browse', 'status', 'category', 'deadline', 'id'),
        Index('ix_quest_owner', 'owner_id', 'created_at', 'id'),
        Index('ix_quest_assignee', 'assignee_id', 'created_at', 'id'),
    )
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='RESTRICT'))
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey('user.id', ondelete='RESTRICT'), nullable=True)
    title: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(String(1500))
    category: Mapped[str] = mapped_column(String(16))
    location: Mapped[str] = mapped_column(String(160))
    reward: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    deadline: Mapped[datetime] = mapped_column(DATETIME(fsp=6))
    contact_type: Mapped[str] = mapped_column(String(16))
    contact_value: Mapped[str] = mapped_column(String(64))
    assignee_contact_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    assignee_contact_value: Mapped[str | None] = mapped_column(String(64), nullable=True)
    completion_note: Mapped[str] = mapped_column(String(500), default='')
    status: Mapped[str] = mapped_column(String(16), default='open')
    created_at: Mapped[datetime] = mapped_column(DATETIME(fsp=6), server_default=text('CURRENT_TIMESTAMP(6)'))
    updated_at: Mapped[datetime] = mapped_column(DATETIME(fsp=6), server_default=text('CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)'))
