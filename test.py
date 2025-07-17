# from Database.database import db_session,get_db
# from Models.models import User
# from sqlalchemy import select
# from sqlalchemy.exc import SQLAlchemyError
# import asyncio
# from fastapi import Depends
# from sqlalchemy.ext.asyncio import AsyncSession

# async def get_user(username:str,db:AsyncSession):
#     print("DB type:", type(db))
#     try:
#         query = select(User).where(User.name==username)
        

#         result = await db.execute(query)
#         user = result.scalars().first()
#         user or False
#     except SQLAlchemyError as e:
#         return False  

# async def printUser():
#     a = await get_user(db:AsyncSession=Depends(get_db),username="Mukesh")
#     print(a.name)

# asyncio.run(printUser())
from dotenv import load_dotenv
import os
load_dotenv()

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash("secret")
print(pwd_context.verify("secret", hashed_password))  # Should print True
print(pwd_context.verify("wrong", hashed_password))   # Should print False


print(os.getenv('SECRET_KEY'))