from fastapi import FastAPI,Depends,HTTPException,status
from Database.database import Base,AsyncSessionLocal,engine,db_session
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from routes.protected_routes import protected_router
from routes.public_routes import public_router
from Schemas.db_schemas import RegisterUser,RegisterGroup,GetUsers,SendRequest
from Models.models import User,Group,JoinRequest
from routes.websocket_route import ws_router



   



app = FastAPI()

app.include_router(public_router, prefix="")
app.include_router(protected_router, prefix="/api")
app.include_router(ws_router,prefix="/ws")








# @app.get("/requests/{user_id}")
# async def get_requests(user_id:UUID,db:db_session):
#     try:
#         query = select(User).