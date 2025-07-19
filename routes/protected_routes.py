from fastapi import APIRouter , Depends,HTTPException,status,Response

from auth import get_current_user,get_user,get_group,get_password_hash,verify_password
from Schemas.db_schemas import GetUsers,RegisterUser,RegisterGroup,SendRequest,GetTheUser,AddToHumanGroup,OutRequest,ChangePassword
from Database.database import db_session
from Models.models import User , Group,GroupAndUser,JoinRequest
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

protected_router = APIRouter(
                            dependencies=[Depends(get_current_user)]
                            )




@protected_router.get("/users/me",response_model=GetTheUser)
async def read_users_me(current_user: User = Depends(get_current_user)):
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
async def create_group(group:RegisterGroup,db:db_session,current_user:User = Depends(get_current_user)):
    try:
        new_group = Group(name=group.name,admin_user = current_user.id ,description=group.description)
        db.add(new_group)
        await db.commit()
        await db.refresh(new_group)
        return Response(status_code=status.HTTP_201_CREATED)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail="Database Error.")




#Can be improved
@protected_router.post("/join_request")
async def send_join_request(sent_request:SendRequest,db:db_session,current_user:User = Depends(get_current_user)):
    try:
        to_user = await get_user(db,sent_request.to_name)
        group = await get_group(db,sent_request.group_name)
        if not to_user :
            raise HTTPException(status_code=404,detail="User not found.")
        if not group:
            raise HTTPException(status_code=404,detail="Group not found.")
        request = JoinRequest(from_name=current_user.name,to_name=to_user.name,group_name = group.name)
        try:
            db.add(request)
            await db.commit()
            await db.refresh(request)
            return Response(status_code=status.HTTP_201_CREATED)
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500,detail="Database Error.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=404, detail="Database Error.")



@protected_router.get("/requests",response_model=List[OutRequest])
async def get_all_requests(db:db_session,current_user:User = Depends(get_current_user)):
    all_requests = select(JoinRequest).where(JoinRequest.to_name == current_user.name)
    try:
        result = await db.execute(all_requests)
        requests =  result.scalars().all()
        if not requests:
            return Response(content="No request yet.",status_code=status.HTTP_204_NO_CONTENT)
        return requests
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Databse Error.")

    




@protected_router.post("/request_response")
async def respond_to_request(decision:AddToHumanGroup,db:db_session,current_user:User=Depends(get_current_user)):
    if decision.response:
        try:
            group = await get_group(db,decision.group_name)
            if not group:   
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Group not found.")
            new_member = GroupAndUser(group_id = group.id,user_id=current_user.id)
            request = await db.execute(select(JoinRequest).where(JoinRequest.to_name==current_user.name , JoinRequest.group_name==group.name))
            request = request.scalars().first()
            if not request:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No such request found.")

            request.accepted = True
            db.add(new_member)
            await db.commit()

            await db.refresh(new_member)      
            return Response(content="Request accepted.",status_code=status.HTTP_200_OK)
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Database error.")
       
    else:
        result = await db.execute(select(JoinRequest).where(JoinRequest.to_name==current_user.name , JoinRequest.group_name==group.name))
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No such request present in the database.")
        await db.commit()
        return Response(status_code=status.HTTP_200_OK,content="Request deleted.")
    



@protected_router.post("/change-password")
async def change_password(new_password:ChangePassword,db:db_session,current_user:User = Depends(get_current_user)):
    is_valid = verify_password(new_password.current_password,current_user.hashed_password)
    if is_valid:
        current_user.hashed_password = get_password_hash(new_password.new_password)
        try:
            db.add(current_user)
            await db.commit()
            await db.refresh(current_user)
            return Response(status_code=status.HTTP_200_OK,content="Password changed successfully.")
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Supply correct password.")






# @protected_router.get("/logout")
# async def logout(current_user:User = Depends(get_current_user)):



