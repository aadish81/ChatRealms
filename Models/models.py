from sqlalchemy import Column,Boolean,String,Text,ForeignKey,Integer,UniqueConstraint,DateTime,func
import uuid
from sqlalchemy.orm import relationship
from Database.database import Base
from sqlalchemy.dialects.postgresql import UUID
from pydantic import EmailStr
from datetime import datetime




class BaseModel(Base):
    __abstract__ = True
    __allow_unmapped__ = True

    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,index=True)


class User(BaseModel):
    __tablename__ = "users"

    name = Column(String(50),unique=True,nullable=False,index=True)
    hashed_password = Column(String,nullable=False)
    email = Column(Text,unique=True,nullable=False,index=True)
    profile_picture = Column(String,nullable=True)
    description = Column(Text,nullable=True)
    #Relationships with group   
    groups = relationship('Group',secondary="group_and_user_association",back_populates='users')
    #Relationship with request table
    request_sent = relationship("User",
                                secondary="join_requests",
                                primaryjoin="JoinRequest.from_id == User.id",
                                secondaryjoin="JoinRequest.to_id == User.id",
                                cascade="all,delete-orphan",
                                single_parent=True,
                                back_populates="request_received"
                                )

    request_received = relationship("User",
                                    secondary="join_requests",
                                    primaryjoin="JoinRequest.to_id == User.id",
                                    secondaryjoin="JoinRequest.from_id == User.id",
                                    back_populates="request_sent"
                                    )


class AiAgents(BaseModel):
    __tablename__ = "ai_agents"

    name = Column(String(50),unique=True,nullable=False,index=True)
    description = Column(Text,nullable=True)
    #Relationships
    groups = relationship("Group",secondary="group_and_agent_associations",back_populates="agents")

    

class Group(BaseModel):
    __tablename__ = "groups"
    name = Column(String(50),unique=True,nullable=False,index=True)
    admin_user = Column(UUID(as_uuid=True),ForeignKey('users.id',ondelete="CASCADE"))
    description = Column(Text,nullable=True)
    #Relationships
    users = relationship("User",secondary="group_and_user_association",back_populates="groups")
    agents = relationship("AiAgents",secondary="group_and_agent_associations", back_populates="groups")

class GroupAndUser(BaseModel):
    __tablename__ = "group_and_user_association"

    group_id = Column(UUID(as_uuid=True),ForeignKey('groups.id',ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True),ForeignKey('users.id',ondelete="CASCADE"))
    specific_user_msgs_in_group = relationship("HumanMessage",back_populates="specific_user_msg_in_group",cascade="all,delete-orphan")
    #Avoid duplicate entries of (group, user)
    __table_args__ = (UniqueConstraint('group_id','user_id'),)




class GroupAndAgent(BaseModel):
    __tablename__ = "group_and_agent_associations"

    group_id = Column(UUID(as_uuid=True),ForeignKey("groups.id",ondelete="CASCADE"))
    agent_id = Column(UUID(as_uuid=True),ForeignKey("ai_agents.id",ondelete="CASCADE"))
    #Avoide duplicate entries of (group,ai_agent)
    __table_args__ = (UniqueConstraint("group_id","agent_id"),)

    specific_agent_msgs_in_group = relationship("AgentMessage",back_populates="specific_agent_msg_in_group",cascade="all,delete-orphan")

 
class HumanMessage(BaseModel):
    __tablename__ = "human_messages"

    message = Column(Text,nullable=False)
    group_and_crpnd_user = Column(UUID(as_uuid=True),ForeignKey("group_and_user_association.id",ondelete="CASCADE"))

    
    sent_at = Column(DateTime(timezone=True),server_default=func.now())
    specific_user_msg_in_group = relationship("GroupAndUser",back_populates="specific_user_msgs_in_group")


class AgentMessage(BaseModel):
    __tablename__ = "model_messages"

    message = Column(Text,nullable=False)
    group_and_crpnd_agent = Column(UUID(as_uuid=True),ForeignKey("group_and_agent_associations.id",ondelete="CASCADE"))
    sent_at = Column(DateTime(timezone=True),server_default=func.now())
    specific_agent_msg_in_group = relationship("GroupAndAgent",back_populates="specific_agent_msgs_in_group")


# class Conversation(BaseModel):
#     __tablename__ = "conversations"

    

class JoinRequest(BaseModel):
    __tablename__ = "join_requests"

    from_id = Column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"))
    to_id = Column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"))
    group_id = Column(UUID(as_uuid=True),ForeignKey("groups.id",ondelete="CASCADE"))
    accepted = Column(Boolean,default=False)#this line needs migration 

    __table_args__ = (UniqueConstraint("to_id","from_id"),)

