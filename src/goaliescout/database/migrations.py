"""Schema creation and migration utilities for GoalieScout.

Handles initial database schema creation and simple version-based
migrations.  For production use, Alembic is recommended for incremental
migrations; this module is the lightweight bootstrapper.
"""

import logging
from typing import Optional

from sqlalchemy import Engine, text

from .connection import get_engine
from .models import Base

logger = logging.getLogger(__name__)

# Current schema version stored in the database
_CURRENT_VERSION = 1


def create_schema(engine: Optional[Engine] = None) -> None:
    """Create all tables defined in the ORM models.

    This is idempotent — existing tables are not modified.

    Args:
        engine: Optional engine.  Defaults to the cached engine.
    """
    eng = engine or get_engine()
    Base.metadata.create_all(bind=eng)
    _set_schema_version(eng, _CURRENT_VERSION)
    logger.info("GoalieScout database schema created / verified.")


def drop_schema(engine: Optional[Engine] = None) -> None:
    """Drop all GoalieScout tables.

    **Destructive operation** — use only in development / testing.

    Args:
        engine: Optional engine.
    """
    eng = engine or get_engine()
    Base.metadata.drop_all(bind=eng)
    logger.warning("GoalieScout database schema dropped.")


def get_schema_version(engine: Optional[Engine] = None) -> int:
    """Return the current schema version stored in the database.

    Returns 0 if the version table does not yet exist.

    Args:
        engine: Optional engine.

    Returns:
        Schema version integer.
    """
    eng = engine or get_engine()
    try:
        with eng.connect() as conn:
            result = conn.execute(
                text("SELECT version FROM _schema_version LIMIT 1")
            )
            row = result.fetchone()
            return row[0] if row else 0
    except Exception:
        return 0


def _set_schema_version(engine: Engine, version: int) -> None:
    """Write the schema version to the database.

    Args:
        engine: Active engine.
        version: Version integer to store.
    """
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS _schema_version "
                "(version INTEGER NOT NULL)"
            )
        )
        existing = conn.execute(
            text("SELECT COUNT(*) FROM _schema_version")
        ).scalar()
        if existing == 0:
            conn.execute(
                text("INSERT INTO _schema_version (version) VALUES (:v)"),
                {"v": version},
            )
        else:
            conn.execute(
                text("UPDATE _schema_version SET version = :v"),
                {"v": version},
            )


def migrate(engine: Optional[Engine] = None) -> None:
    """Run any pending schema migrations.

    Currently handles the initial migration (version 0 → 1).  Future
    migrations can be added as additional ``elif`` branches.

    Args:
        engine: Optional engine.
    """
    eng = engine or get_engine()
    current = get_schema_version(eng)
    logger.info(f"Database schema version: {current} (target: {_CURRENT_VERSION})")

    if current < 1:
        logger.info("Applying migration: 0 → 1 (initial schema)")
        create_schema(eng)
        logger.info("Migration complete: schema at version 1")
    else:
        logger.info("Database schema is up to date.")
