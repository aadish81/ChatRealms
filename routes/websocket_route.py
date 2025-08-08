from routes.protected_routes import protected_router
from routes.public_routes import public_router
from fastapi import WebSocket,Depends,status , HTTPException,WebSocketDisconnect,APIRouter
from auth import get_current_user_ws
from pydantic import BaseModel
from typing import Dict , Set
from Database.database import db_session,AsyncSessionLocal,get_db
from auth import get_group,get_current_user
from Models.models import GroupAndUser,User,HumanMessage,Group
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from Schemas.db_schemas import SendMessage,GetUsers
import json


ws_router = APIRouter(dependencies=[Depends(get_current_user_ws)])



class ConnectionManager():
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
            self.group_connections[group_name].remove(websocket)#remove the websocket passed as argument
            if not self.group_connections[group_name]:#if self.group_connections is empty i.e. None
                del self.group_connections[group_name]#deletes the "group_name":() as no sockets are present in "group_name"
        if user in self.user_groups and group_name in self.user_groups[user]:
            self.user_groups[user].remove(group_name)
            if not self.user_groups[user]:
                del self.user_groups[user]


    async def disconnect_all(self,websocket:WebSocket,user:str):
        if user in self.user_groups: 
            if self.user_groups[user]:#if self.user_groups is not empty
                for group in self.user_groups[user]:#select groups of the user one-by-one
                    if group in self.group_connections: # if selected group is in self.group_connection 
                        if websocket in self.group_connections[group]:
                            await websocket.close(code=status.WS_1008_POLICY_VIOLATION,reason="Session Invalidated.")
                            self.group_connections[group].remove(websocket)
                            if not self.group_connections[group]:
                                del self.group_connections[group]
            del self.user_groups[user]

    async def broadcast(self,sender:str,message:str,group_name:str):
        if group_name in self.group_connections:
            for websockets in self.group_connections[group_name]:
                await websockets.send_text(f"{sender}:{message}")


manager = ConnectionManager()


@ws_router.websocket("/chat/group/{group_name}")
async def websocket_group(group_name:str,websocket:WebSocket,current_user:User = Depends(get_current_user_ws),db:AsyncSession = Depends(get_db)):
    try:
        # Check if the group exists
        group = await get_group(db,group_name)
        if not group:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION,reason="No such group.")
            return
        # Check if the user is a member of the group
        query = select(GroupAndUser).where(GroupAndUser.group_id == group.id, GroupAndUser.user_id == current_user.id)
        result = await db.execute(query)
        record = result.scalars().first()
        if not record:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION,reason="You are not a member of this group yet.")
            return

    except SQLAlchemyError as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION,reason="Database error...")
        return   


    await manager.connect(websocket,group.name,current_user.name)

    try:
        # Send existing messages to the user
        # Fetch all messages in the group
        # Using selectinload to eagerly load related messages and their senders
        # This will load all human messages and their senders in one query
        # and all agent messages in another query

        query = select(Group).options(selectinload(Group.humans_messages).selectinload(HumanMessage.sender),selectinload(Group.agents_messages)).where(Group.id == group.id)
        result  = await db.execute(query)
        current_group = result.scalars().first()
        if not current_group:
            await manager.disconnect(group.name,current_user.name,websocket)
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION,reason="No such group found.")
            return
        # Send existing human messages
        for msg in current_group.humans_messages:
            await websocket.send_text(f"{msg.sender}:{msg.message}")


        while True:
            message:str = await websocket.receive_text()

            new_message = HumanMessage(message = message,user_id = current_user.id,group_id=group.id)
            db.add(new_message)
            await db.commit()

            await manager.broadcast(current_user.name,message,group.name)

    except WebSocketDisconnect as e:
        await manager.disconnect(group.name,current_user.name,websocket)

        






    


