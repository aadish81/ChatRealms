from passlib.context import CryptContext
from datetime import datetime,timedelta
from jose import JWTError,jwt
from fastapi.security import OAuth2PasswordBearer     
from fastapi import Depends,HTTPException,status
from dotenv import load_dotenv
from Database.database import db_session
from sqlalchemy import select
from Models.models import User
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional , List
import os
from pydantic import BaseModel



load_dotenv()



class TokenData(BaseModel):
    username:Optional[str] = None   


    
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  



def get_password_hash(password:str):
    return pwd_context.hash(password)



def verify_password(plain_password:str,hashed_password:str):
    pwd_context.verify(plain_password,hashed_password)




async def get_user(db:AsyncSession,username:str):
    try:
        query = select(User).where(User.name==username)
        result = await db.execute(query)
        user = result.scalars().first()
        if not user:
            return False
        return user
    except SQLAlchemyError as e:
        return False  



async def authenticate_user(username:str,password:str,db:AsyncSession):
    user = await get_user(db=db,username=username)
    if not user or  verify_password(password,user.hashed_password):
        return False
    return user




def create_access_token(data:dict, expires_delta:timedelta ):
    expire = datetime.utcnow() + expires_delta  
    data.update({'exp':expire})
    encoded_jwt = jwt.encode(data, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))
    return encoded_jwt



async def get_current_user(db:db_session,token:str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials.",headers={"WWW-Authenticate":"Bearer"},)
    try:
        payload = jwt.decode(token,os.getenv('SECRET_KEY'),algorithms=os.getenv('ALGORITHM'))
        username:str = payload.get('username')
        if username is None: 
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        raise credentials_exception
    user = await get_user(db=db,username=token_data.username)
    if not user:
        raise credentials_exception
    return user

        

