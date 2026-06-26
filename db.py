import os
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, BigInteger
from sqlalchemy.dialects.postgresql import JSONB

POSTGRES_URL = os.getenv("POSTGRES_URL")

engine = create_async_engine(POSTGRES_URL, echo=False) if POSTGRES_URL else None
async_session = (
    sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    if engine
    else None
)
Base = declarative_base()


class Operation(BaseModel):
    type: str
    roles: None | list[int] = None
    rename: None | str = None


class Token(Base):
    __tablename__ = "tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, unique=True, index=True, nullable=False)
    guild = Column(BigInteger, index=True, nullable=False)
    email = Column(String, nullable=True)
    operations = Column(JSONB, nullable=False)
    permanent = Column(Boolean, nullable=True)


def RoleOp(roles: list[int]):
    return Operation(type="role", roles=roles).dict()


def RenameOp(name: str):
    return Operation(type="rename", rename=name.strip()).dict()


async def init_db():
    if engine is None:
        print("Warning: POSTGRES_URL is not set.")
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
