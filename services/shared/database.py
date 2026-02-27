"""
Shared database configuration for all microservices.
Uses async SQLAlchemy with PostgreSQL + PostGIS.
"""

from typing import Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from shared.config import get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def create_engine(database_url: Optional[str] = None):
    """Create an async SQLAlchemy engine."""
    url = database_url or get_settings().DATABASE_URL
    return create_async_engine(
        url,
        echo=False,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,
    )


def create_session_factory(engine):
    """Create an async session factory."""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


# Default engine and session factory
engine = create_engine()
AsyncSessionFactory = create_session_factory(engine)


async def get_db() -> AsyncSession:
    """Dependency injection for database sessions."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
