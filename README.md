# Nutrition Coaching Application

This project provides a simple REST API that allows users to register, log meals, receive nutrition summaries, and get personalized recommendations.

## Tech Stack

* **FastAPI** – modern, fast web framework.
* **SQLModel** – type-hinted ORM (built on SQLAlchemy).
* **SQLite** – lightweight embedded database.

## Getting Started

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server**

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at http://127.0.0.1:8000.

3. **Explore the API**

   Navigate to http://127.0.0.1:8000/docs for interactive Swagger UI documentation.

## Key Endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| POST   | /users               | Create a new user profile |
| POST   | /users/{id}/meals    | Log a meal for a user |
| GET    | /users/{id}/summary  | Daily nutrition summary for a user |
| GET    | /users/{id}/recommendation | Personalized calorie & macro targets |

## Project Structure

```
app/
 ├── __init__.py
 ├── database.py   # DB connection & session helpers
 ├── models.py     # SQLModel ORM models
 ├── services.py   # Business logic (calculations & summaries)
 └── main.py       # FastAPI application & routes
```