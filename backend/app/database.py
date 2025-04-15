from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.future import select  
from sqlalchemy import and_
from app.config import settings
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

Base = declarative_base()

engine = create_async_engine(settings.DB_URL, echo=True)
#engine = create_async_engine(
#    settings.DB_URL.replace("mysql+asyncmy", "mysql+aiomysql"),
#    echo=True
#)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Добавьте явные импорты для моделей
    from app.models import SprintPeriodicity
    
    async with async_session() as session:
        periodicities = [
            "1 неделя", "2 недели", "3 недели", 
            "1 месяц", "2 месяца", 
            "1 квартал", "2 квартала", "3 квартала", 
            "1 год"
        ]
        
        for period in periodicities:
            result = await session.execute(
                select(SprintPeriodicity).where(SprintPeriodicity.name == period)
            )
            if not result.scalars().first():
                session.add(SprintPeriodicity(name=period))
        
        await session.commit()