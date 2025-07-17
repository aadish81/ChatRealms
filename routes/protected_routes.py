from fastapi import APIRouter , Depends,HTTPException,status

from auth import get_current_user,get_user,get_password_hash
from Schemas.db_schemas import GetUsers,RegisterUser,RegisterGroup,SendRequest,GetTheUser
from Database.database import db_session
from Models.models import User , Group
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

protected_router = APIRouter(
                            dependencies=[Depends(get_current_user)]
                            )




@protected_router.get("/users/me", response_model=GetTheUser)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user




@protected_router.get("/users/",response_model=List[GetUsers])
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








@protected_router.post('/add_group')
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





@protected_router.post("/request/")
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