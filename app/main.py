from datetime import date, timedelta
from typing import List

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    Query,
)
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from .database import init_db, get_session
from .models import User, Meal, ProgressEntry, GoalMilestone
from .services import get_daily_summary, get_recommendation
from .schemas import (
    UserCreate,
    UserRead,
    Token,
    MealCreate,
    MealRead,
    ProgressEntryCreate,
    ProgressEntryRead,
    GoalMilestoneCreate,
    GoalMilestoneRead,
)
from .auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
)

app = FastAPI(title="Nutrition Coaching API", version="0.2.0")

# Initialize DB tables on startup
init_db()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Home page
@app.get("/", response_class=HTMLResponse)
def root():
    return FileResponse("static/index.html")


@app.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, session: Session = Depends(get_session)):
    # Ensure email uniqueness
    existing = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_in.email,
        name=user_in.name,
        age=user_in.age,
        gender=user_in.gender,
        height_cm=user_in.height_cm,
        weight_kg=user_in.weight_kg,
        activity_level=user_in.activity_level,
        goal=user_in.goal,
        hashed_password=get_password_hash(user_in.password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# Login and token endpoint
@app.post("/auth/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token = create_access_token({"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users", response_model=List[UserRead])
def list_users(session: Session = Depends(get_session), _: User = Depends(get_current_user)):
    return session.exec(select(User)).all()


@app.post("/users/{user_id}/meals", response_model=MealRead, status_code=status.HTTP_201_CREATED)
def log_meal(
    user_id: int,
    meal_in: MealCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to log meal for this user")

    # Ensure path ID matches body or body missing id
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    meal = Meal(user_id=user_id, **meal_in.dict())
    session.add(meal)
    session.commit()
    session.refresh(meal)
    return meal


# ---------------------- Progress Tracking ----------------------


@app.post("/users/{user_id}/progress", response_model=ProgressEntryRead, status_code=status.HTTP_201_CREATED)
def add_progress_entry(
    user_id: int,
    entry_in: ProgressEntryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to add progress for this user")

    # Validate user exists
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    entry = ProgressEntry(user_id=user_id, **entry_in.dict())
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@app.get("/users/{user_id}/progress", response_model=List[ProgressEntryRead])
def list_progress_entries(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    statement = select(ProgressEntry).where(ProgressEntry.user_id == user_id).order_by(ProgressEntry.date)
    return session.exec(statement).all()


# ---------------------- Goal Milestones ----------------------


@app.post("/users/{user_id}/goals", response_model=GoalMilestoneRead, status_code=status.HTTP_201_CREATED)
def add_goal_milestone(
    user_id: int,
    goal_in: GoalMilestoneCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to add goal for this user")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    milestone = GoalMilestone(user_id=user_id, **goal_in.dict())
    session.add(milestone)
    session.commit()
    session.refresh(milestone)
    return milestone


@app.get("/users/{user_id}/goals", response_model=List[GoalMilestoneRead])
def list_goal_milestones(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    statement = select(GoalMilestone).where(GoalMilestone.user_id == user_id).order_by(GoalMilestone.target_date)
    return session.exec(statement).all()


@app.get("/users/{user_id}/summary")
def daily_summary(
    user_id: int,
    date_str: str = Query(default_factory=lambda: date.today().isoformat()),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
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
def recommendation(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return get_recommendation(user)