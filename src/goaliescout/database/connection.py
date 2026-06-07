"""Database connection management for GoalieScout.

Uses SQLite by default for zero-configuration local setup.  Switching to
PostgreSQL (or any other SQLAlchemy-compatible backend) requires only
changing the ``DATABASE_URL`` environment variable or passing a different
``url`` to :func:`get_engine`.

Example::

    # SQLite (default)
    engine = get_engine()

    # PostgreSQL
    engine = get_engine("postgresql+psycopg2://user:pass@localhost/goaliescout")
"""

import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker

_DEFAULT_SQLITE_PATH = "./data/goaliescout.db"

# Module-level cached engine
_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def get_engine(url: Optional[str] = None, echo: bool = False) -> Engine:
    """Return a (cached) SQLAlchemy engine.

    Args:
        url: SQLAlchemy database URL.  Falls back to the
             ``DATABASE_URL`` environment variable, then to a local
             SQLite file at :data:`_DEFAULT_SQLITE_PATH`.
        echo: If ``True``, log all SQL statements (useful for debugging).

    Returns:
        A :class:`sqlalchemy.engine.Engine` instance.
    """
    global _engine, _SessionLocal

    if _engine is not None and url is None:
        return _engine

    resolved_url = url or os.getenv("DATABASE_URL") or f"sqlite:///{_DEFAULT_SQLITE_PATH}"

    # Ensure the directory exists for SQLite databases
    if resolved_url.startswith("sqlite:///"):
        db_path = resolved_url[len("sqlite:///"):]
        if db_path and db_path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

    engine = create_engine(
        resolved_url,
        echo=echo,
        # SQLite-specific: enable WAL mode for better concurrent read performance
        connect_args={"check_same_thread": False} if "sqlite" in resolved_url else {},
    )

    if url is None:
        _engine = engine
        _SessionLocal = sessionmaker(bind=_engine, autoflush=True, autocommit=False)

    return engine


def get_session_factory(engine: Optional[Engine] = None) -> sessionmaker:
    """Return a session factory bound to *engine*.

    Args:
        engine: Optional engine.  Defaults to the cached engine from
                :func:`get_engine`.

    Returns:
        A :class:`sqlalchemy.orm.sessionmaker` instance.
    """
    global _SessionLocal
    if engine is not None:
        return sessionmaker(bind=engine, autoflush=True, autocommit=False)
    if _SessionLocal is None:
        get_engine()  # initialise cached engine
    return _SessionLocal  # type: ignore[return-value]


@contextmanager
def get_session(engine: Optional[Engine] = None) -> Generator[Session, None, None]:
    """Context manager that yields a database session.

    Commits on success and rolls back on exception.

    Args:
        engine: Optional engine override.

    Yields:
        An active :class:`sqlalchemy.orm.Session`.

    Example::

        with get_session() as session:
            goalie = session.get(Goalie, 1)
    """
    factory = get_session_factory(engine)
    session: Session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def reset_engine() -> None:
    """Reset the cached engine (useful for testing with in-memory SQLite)."""
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None
