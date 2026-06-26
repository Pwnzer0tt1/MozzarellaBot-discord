import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, BigInteger
from sqlalchemy.dialects.postgresql import JSONB

# Connection settings
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'mozzarellabot')
POSTGRES_URL = os.getenv('POSTGRES_URL', 'postgresql+asyncpg://user:password@localhost:5432/mozzarellabot')

Base = declarative_base()

class Token(Base):
    __tablename__ = 'tokens'
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, unique=True, index=True, nullable=False)
    guild = Column(BigInteger, index=True, nullable=False)
    email = Column(String, nullable=True)
    operations = Column(JSONB, nullable=False)
    permanent = Column(Boolean, nullable=True)

async def migrate():
    print(f"Connecting to MongoDB at {MONGO_URL}...")
    mongo_client = AsyncIOMotorClient(MONGO_URL)
    mongo_db = mongo_client[DB_NAME]
    mongo_collection = mongo_db["Token"]

    print(f"Connecting to PostgreSQL at {POSTGRES_URL}...")
    engine = create_async_engine(POSTGRES_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    print("Creating tables in PostgreSQL...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Starting data migration...")
    count = 0
    async with async_session() as session:
        cursor = mongo_collection.find({})
        async for document in cursor:
            # Map MongoDB document to PostgreSQL
            operations = document.get("operations", [])
            pg_token = Token(
                token=document["token"],
                guild=document["guild"],
                email=document.get("email"),
                operations=operations,
                permanent=document.get("permanent")
            )
            session.add(pg_token)
            count += 1
            
            if count % 100 == 0:
                await session.commit()
                print(f"Migrated {count} records...")
        
        # Commit any remaining records
        await session.commit()
    
    print(f"Migration completed successfully! Total records migrated: {count}")

if __name__ == "__main__":
    asyncio.run(migrate())
