from typing import List, Optional
from datetime import date

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    name: str
    age: int = Field(gt=0, lt=120)
    gender: str
    height_cm: float = Field(gt=0)
    weight_kg: float = Field(gt=0)
    activity_level: str
    goal: str


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MealBase(BaseModel):
    name: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    date: date


class MealCreate(MealBase):
    pass


class MealRead(MealBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


# Progress tracking


class ProgressEntryBase(BaseModel):
    date: date
    weight_kg: float = Field(gt=0)
    waist_cm: Optional[float] = Field(default=None, gt=0)
    chest_cm: Optional[float] = Field(default=None, gt=0)
    hips_cm: Optional[float] = Field(default=None, gt=0)
    body_fat_pct: Optional[float] = Field(default=None, ge=0, le=100)
    note: Optional[str] = None


class ProgressEntryCreate(ProgressEntryBase):
    pass


class ProgressEntryRead(ProgressEntryBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True