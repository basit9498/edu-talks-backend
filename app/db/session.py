from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings


# engine

engine = create_engine(settings.DATABASE_URL, future=True)

async_engine = create_async_engine(settings.DATABASE_URL_ASYNC, future=True, echo=True)


# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# db
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


async def async_get_db():
    async with AsyncSessionLocal() as session:
        yield session
