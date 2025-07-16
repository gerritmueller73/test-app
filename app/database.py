from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager

# SQLite database file
DATABASE_URL = "sqlite:///nutrition.db"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    """Create database tables (run on startup)."""
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Session:  # type: ignore[override]
    """Yield a database session context manager for dependency injection."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()