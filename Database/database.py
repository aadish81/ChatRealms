from sqlalchemy.ext.asyncio import create_async_engine ,AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
from typing import Annotated
from fastapi import Depends

load_dotenv()

DB_URL = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_MACHINE')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_async_engine(DB_URL)

AsyncSessionLocal = sessionmaker(engine,class_=AsyncSession,autoflush=False,expire_on_commit=False)

Base = declarative_base()

# async def get_db():
#     db = AsyncSessionLocal()
#     try:
#         yield db
#     finally:
#         await db.close() 

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db
        
db_session = Annotated[AsyncSession,Depends(get_db)]