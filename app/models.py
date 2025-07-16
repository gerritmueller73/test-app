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
    email: str
    name: str
    age: int
    gender: str  # "male" | "female"
    height_cm: float
    weight_kg: float
    activity_level: str  # "sedentary", "light", "moderate", "active", "very_active"
    goal: str  # "maintain", "lose", "gain"
    hashed_password: str

    # Relationships
    meals: List[Meal] = Relationship(back_populates="user")
    progress_entries: List["ProgressEntry"] = Relationship(back_populates="user")
    milestones: List["GoalMilestone"] = Relationship(back_populates="user")


# Progress tracking (weight, measurements)


class ProgressEntry(SQLModel, table=True):
    """Stores weight and body measurement progress for the user."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

    # Metrics
    date: date
    weight_kg: float = Field(gt=0)
    waist_cm: Optional[float] = Field(default=None, gt=0)
    chest_cm: Optional[float] = Field(default=None, gt=0)
    hips_cm: Optional[float] = Field(default=None, gt=0)
    body_fat_pct: Optional[float] = Field(default=None, ge=0, le=100)
    note: Optional[str] = None

    # Relationship
    user: Optional[User] = Relationship(back_populates="progress_entries")


# Goal milestones


class GoalMilestone(SQLModel, table=True):
    """Defines a goal milestone that a user wants to achieve by a target date."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

    description: str
    target_date: date
    is_completed: bool = False
    completed_date: Optional[date] = None

    user: Optional[User] = Relationship(back_populates="milestones")