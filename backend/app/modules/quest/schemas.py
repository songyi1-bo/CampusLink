from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Literal
from pydantic import Field, field_validator
from app.modules.ride.schemas import Contact, PublicPerson, StrictModel

Category = Literal['delivery', 'study', 'repair', 'other']
Status = Literal['open', 'accepted', 'submitted', 'completed', 'cancelled']

class QuestWrite(Contact):
    title: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=5, max_length=1500)
    category: Category
    location: str = Field(min_length=2, max_length=160)
    reward: Decimal = Field(ge=0, le=Decimal('9999.99'), decimal_places=2)
    deadline: datetime

    @field_validator('deadline')
    @classmethod
    def future_deadline(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError('截止时间必须包含时区')
        value = value.astimezone(timezone.utc)
        if not datetime.now(timezone.utc) < value <= datetime.now(timezone.utc) + timedelta(days=30):
            raise ValueError('请选择未来 30 天内的截止时间')
        return value

class Completion(StrictModel):
    completion_note: str = Field(min_length=2, max_length=500)

class QuestDetail(StrictModel):
    id: int
    owner: PublicPerson
    assignee: PublicPerson | None
    title: str
    description: str
    category: Category
    location: str
    reward: str
    deadline: datetime
    status: Status
    display_status: str
    created_at: datetime
    updated_at: datetime

class Relation(StrictModel):
    role: Literal['owner', 'assignee', 'visitor']
    can_edit: bool
    can_accept: bool
    can_withdraw: bool
    can_submit: bool
    can_confirm: bool
    can_cancel: bool
    can_contact: bool
    completion_note: str | None

class QuestContacts(StrictModel):
    owner: Contact
    assignee: Contact | None
