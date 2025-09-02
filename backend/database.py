from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Railway-provided DATABASE_URL or fallback local DB
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:CQMXtkOxxXBTGNFUBnUEFeQoMqQhvftZ@trolley.proxy.rlwy.net:37648/railway"
)

# Create async engine with connection safeguards
engine = create_async_engine(
    DATABASE_URL,
    echo=True,            # Set to False in production
    future=True,
    pool_pre_ping=True,   # Ensure connections are alive before use
    pool_recycle=1800     # Recycle connections every 30 min
)

# Session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Declarative base
Base = declarative_base()

# Dependency to get DB session per request
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
