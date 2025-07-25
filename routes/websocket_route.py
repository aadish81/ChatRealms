from routes.protected_routes import protected_router
from fastapi import WebSocket,Depends,status , HTTPException,WebSocketException
from auth import get_current_user_ws
from pydantic import BaseModel
from typing import Dict , Set
from Database.database import db_session
from auth import get_group,get_current_user
from Models.models import GroupAndUser,User,HumanMessage
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from Schemas.db_schemas import SendMessage,GetUsers



async def ConnectionManager():
    def __init__(self):
        self.group_connections: Dict[str,Set[WebSocket]]  = {}
        self.user_groups : Dict[str,Set[str]] = {}

    async def connect(self,websocket:WebSocket,group_name:str,user:str):
        await websocket.accept()
        if user not in self.user_groups:
            self.user_groups[user] = set()
        self.user_groups[user].add(group_name)
        if group_name not in self.group_connections:
            self.group_connections[group_name] = set()
        self.group_connections[group_name].add(websocket)



    async def disconnect(self,group_name:str,user:str,websocket:WebSocket):
        if group_name in self.group_connections:
            self.group_connections[group_name].discard(wbesocket)#remove the websocket passed as argument
            if not self.group_connections[group_name]:#if self.group_connections is empty i.e. None
                del self.group_connections[group_name]#deletes the "group_name":() as no sockets are present in "group_name"
        if user in self.user_groups and group_name in self.user_groups[user]:
            self.user_groups[user].discard(group_name)
            if not self.user_groups[user]:
                del self.user_groups[user]


    async def disconnect_all(self,websocket:WebSocket,user:str):
        if user in self.user_groups: 
            if self.user_groups[user]:#if self.user_groups is not empty
                for group in self.user_groups[user]:#select groups of the user one-by-one
                    if group in self.group_connections: # if selected group is in self.group_connection 
                        if websocket in self.group_connections[group]:
                            await websocket.close(code=status.WS_1008_POLICY_VIOLATION,reason="Session Invalidated.")
                            self.group_connections[group].discard(websocket)
                            if not self.group_connections[group]:
                                del self.group_connections[group]
            del self.user_groups[user]

    async def broadcast(self,sender:str,message:str,group_name:str):
        if group_name in self.group_connections:
            for websockets in self.group_connections[group_name]:
                await websockets.send_text({'sender':sender,'message':message})


manager = await ConnectionManager()


@protected_router.websocket("/ws/chat/group/{group_name}")
async def websocket_group(group_name:str,websocket:WebSocket,db:db_session,current_user:User = Depends(get_current_user_ws)):
    try:
        group = get_group(db,group_name)
        
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No such group.")
        
        query = select(GroupAndUser).where(GroupAndUser.group_id == group.id, GroupAndUser.user_id == current_user.id )
        result = await query.execute(query)
        record = result.scalars().first()
        if not record:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="You are not a member of this group yet.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED,detail="Databse error.")
    
    

    try:
        await manager.connect(websocket,group.name,current_user.name)
        query = select(Group).options(selectionload(Group.humans_messages),selectionload(Group.agents_messages)).where(Group.id ==group.id)
        result  = await db.execute(query)
        all_messages = result.scalars().all()
        for msg in all_messages:
            await websocket.send_text(f"{msg.sender}:{msg.message}")
        while True:
            message = await websocket.receive_text()
            new_message = HumanMessage(message = message,user_id = current_user.id,group_id=group.id)
            db.add(new_message)
            await ab.commit()
            await manager.broadcast(current_user.name,message,group.name)
    except WebSocketException as e:
        await manager.disconnect(group.name,current_user.name,websocket)



@protected_router.get("/namaskar",response_model=GetUsers)
async def say_Namaskar(db:db_session,user:User = Depends(get_current_user)):
    query = select(USer).where(User.id == user.id)
    result = await execute(query)
    user_exit = result.scalars().first()
    if not user_exit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found....")
    return user_exit



    


