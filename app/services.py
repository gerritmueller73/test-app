from datetime import date
from typing import Dict, Any

from sqlmodel import Session, select

from .models import User, Meal


def _bmr_mifflin_st_jeor(user: User) -> float:
    """Calculate Basal Metabolic Rate (BMR) using the Mifflin-St Jeor Equation."""
    if user.gender.lower() == "male":
        s = 5
    else:
        s = -161
    return 10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age + s


def _activity_factor(level: str) -> float:
    mapping = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }
    return mapping.get(level.lower(), 1.2)


def _goal_adjustment(goal: str) -> float:
    if goal == "lose":
        return -500  # kcal per day deficit
    if goal == "gain":
        return 500
    return 0


def get_recommendation(user: User) -> Dict[str, Any]:
    """Return recommended daily calories & macronutrients for the user."""
    bmr = _bmr_mifflin_st_jeor(user)
    tdee = bmr * _activity_factor(user.activity_level)
    target_cal = tdee + _goal_adjustment(user.goal)

    # Macro distribution (% of calories)
    protein_pct = 0.25
    fat_pct = 0.25
    carbs_pct = 0.5

    protein_g = (target_cal * protein_pct) / 4  # 4 kcal per g protein
    fat_g = (target_cal * fat_pct) / 9
    carbs_g = (target_cal * carbs_pct) / 4

    return {
        "calories": round(target_cal),
        "protein_g": round(protein_g),
        "fat_g": round(fat_g),
        "carbs_g": round(carbs_g),
    }


def get_daily_summary(session: Session, user_id: int, day: date):
    """Aggregate nutrition data for the specified user on a given date."""
    statement = select(Meal).where(Meal.user_id == user_id, Meal.date == day)
    meals = session.exec(statement).all()

    total_cal = sum(m.calories for m in meals)
    protein_g = sum(m.protein_g for m in meals)
    carbs_g = sum(m.carbs_g for m in meals)
    fat_g = sum(m.fat_g for m in meals)

    return {
        "date": str(day),
        "total_calories": total_cal,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
        "meals": meals,
    }