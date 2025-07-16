from typing import Optional, List
from datetime import date
from sqlmodel import SQLModel, Field, Relationship


class Meal(SQLModel, table=True):
    """Meal logged by the user."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

    name: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    date: date

    # Relationships
    user: Optional["User"] = Relationship(back_populates="meals")


class User(SQLModel, table=True):
    """User profile with basic anthropometrics & goals."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    age: int
    gender: str  # "male" | "female"
    height_cm: float
    weight_kg: float
    activity_level: str  # "sedentary", "light", "moderate", "active", "very_active"
    goal: str  # "maintain", "lose", "gain"

    # Relationships
    meals: List[Meal] = Relationship(back_populates="user")