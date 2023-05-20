from motor.motor_asyncio import AsyncIOMotorClient
from beanie import Document, Indexed, init_beanie
from typing import Optional
import os, datetime
from pydantic import BaseModel 

MONGO_URL = os.getenv('MONGO_URL')
DB_NAME = os.getenv('DB_NAME', "mozzarellabot")

db_client = AsyncIOMotorClient(MONGO_URL)

class Operation(BaseModel):
    type: str
    roles: Optional[list[int]]
    rename: Optional[str]

class Token(Document):
    token: Indexed(str, unique=True)
    guild: Indexed(int)
    email: Optional[str]
    operations: list[Operation]

def RoleOp(roles: list[int]):
    return Operation(type="role", roles=roles)

def RenameOp(name: str):
    return Operation(type="rename", rename=name.strip())

async def init_db():
    # Initialize beanie with the Product document class
    await init_beanie(database=db_client[DB_NAME], document_models=[Token])