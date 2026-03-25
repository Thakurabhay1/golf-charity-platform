from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, date

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    subscription_type: str
    charity_id: int
    contribution_percentage: float = 10.0

class User(UserBase):
    id: int
    subscription_status: str
    renewal_date: Optional[datetime] = None
    charity_id: Optional[int] = None
    contribution_percentage: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ScoreBase(BaseModel):
    score: int
    date: date

class ScoreCreate(ScoreBase):
    pass

class Score(ScoreBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CharityBase(BaseModel):
    name: str
    description: str
    image_url: Optional[str] = None
    website: Optional[str] = None

class CharityCreate(CharityBase):
    pass

class Charity(CharityBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DrawBase(BaseModel):
    draw_date: date
    numbers: List[int]

class DrawCreate(DrawBase):
    pass

class Draw(DrawBase):
    id: int
    status: str
    prize_pool: Optional[float] = 0
    created_at: datetime

    class Config:
        from_attributes = True

class DrawParticipant(BaseModel):
    id: int
    draw_id: int
    user_id: int
    numbers: List[int]
    created_at: datetime

    class Config:
        from_attributes = True

class WinnerBase(BaseModel):
    draw_id: int
    user_id: int
    match_type: int
    prize_amount: float

class WinnerCreate(WinnerBase):
    pass

class Winner(WinnerBase):
    id: int
    status: str
    proof_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
