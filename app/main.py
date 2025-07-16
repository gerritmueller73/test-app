from datetime import date
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from .database import init_db, get_session
from .models import User, Meal
from .services import get_daily_summary, get_recommendation

app = FastAPI(title="Nutrition Coaching API", version="0.1.0")

# Initialize DB tables on startup
init_db()


@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.get("/users", response_model=List[User])
def list_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()


@app.post("/users/{user_id}/meals", response_model=Meal, status_code=status.HTTP_201_CREATED)
def log_meal(user_id: int, meal: Meal, session: Session = Depends(get_session)):
    # Ensure path ID matches body or body missing id
    if meal.user_id and meal.user_id != user_id:
        raise HTTPException(status_code=400, detail="user_id mismatch between path and body")
    meal.user_id = user_id

    # Validate user exists
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.add(meal)
    session.commit()
    session.refresh(meal)
    return meal


@app.get("/users/{user_id}/summary")
def daily_summary(
    user_id: int,
    date_str: str = Query(default_factory=lambda: date.today().isoformat()),
    session: Session = Depends(get_session),
):
    try:
        day = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    # Ensure user exists
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return get_daily_summary(session, user_id=user_id, day=day)


@app.get("/users/{user_id}/recommendation")
def recommendation(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return get_recommendation(user)