from fastapi import FastAPI,Depends,HTTPException,status
from Database.database import Base,AsyncSessionLocal,engine,db_session
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from Schemas.db_schemas import RegisterUser,RegisterGroup,GetUsers,SendRequest
from Models.models import User,Group,JoinRequest


   



app = FastAPI()



@app.get('/hello')
async def say_hello():
    return {"message":"Hello Everyone!!"}

@app.get("/users/",response_model=List[GetUsers])
async def get_users(db:db_session):
    try:
        query = select(User)
        result = await db.execute(query)
        users = result.scalars().all()
        if not users:
            raise HTTPException(status_code=404,detail="No user found")
        return users
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail="Databse error")



@app.post('/add_user',response_model=GetUsers)
async def create_user(user:RegisterUser,db:db_session):
    new_user = User(name = user.name,email= user.email,hashed_password = user.password,description=user.description)
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail="Database Error.")
    
@app.post('/add_group')
async def create_group(group:RegisterGroup,db:db_session):
    try:
        query = select(User).where(User.name==group.admin_user)
        result = await db.execute(query)
        admin_exist = result.scalars().first()
        if not admin_exist:
            raise HTTPException(status_code=404,detail="Admin not found.")
        new_group = Group(name=group.name,admin_user = admin_exist.id ,description=group.description)
        return
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail="Database Error.")


@app.post("/request/")
async def send_request(sent_request:SendRequest,db:db_session):
    try:
        query = select(User).where(User.name == sent_request.to_name)
        result = await db.execute(query)
        user_exist = result.scalar().first()
        if not user_exist:
            raise HTTPException(status_code=404,detail="User not found.")
        request = JoinRequest(from_id=sent_request.from_id,to_id=user_exist.id,group_id = sent_request.group_id)
        try:
            db.add(request)
            await db.commit()
            await db.refresh(request)
            return
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500,detail="Database Error.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=404, detail="Database Error.")


# @app.get("/requests/{user_id}")
# async def get_requests(user_id:UUID,db:db_session):
#     try:
#         query = select(User).