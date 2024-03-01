import secrets
import time
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import relationship
from sqlalchemy import func, ForeignKey
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Date, Text, SmallInteger
from sqlalchemy.dialects.postgresql import TSTZRANGE, TIMESTAMP, TSRANGE, JSONB 
from sqlalchemy.dialects.postgresql import UUID, VARCHAR, TEXT, INTEGER, DATE, NUMERIC, ARRAY
from sqlalchemy.dialects.postgresql import BOOLEAN, DOUBLE_PRECISION, BIGINT, TIME, SMALLINT, TEXT
from sqlalchemy import Enum


from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base


import bcrypt
from pgvector.sqlalchemy import Vector


dbbase = declarative_base()

class User(dbbase):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(50), unique=True, nullable=False)
    username = Column(String(50), unique=False, nullable=False)
    password_hash = Column(String(128), nullable=False)

    profiles = relationship('Profile', back_populates='user')

    tokens = relationship('Token', back_populates='user')

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())


    def from_dict(self, payload):
        self.username = payload["username"]
        self.email = payload["email"]
        return self
    
    def to_dict(self):
        return {
            "id":self.id,
            "username":self.username,
            "email":self.email,
        }
    
    def hash_password(self, 
            password:str="",
            min_len=12):
        if len(password) < min_len:
            raise Exception(f"Password must be at least {min_len} characters")
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        self.password_hash = hashed.decode('utf-8')
        return hashed

    def check_password(self, password:str=""):
        psw = password.encode('utf-8')
        hsh = self.password_hash.encode('utf-8')
        if bcrypt.checkpw(psw, hsh):
            return True
        return False



class Token(dbbase):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True)
    token = Column(String(128), nullable=False)
    key = Column(String(128), nullable=True)
    expires_on = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())


    def generate(self, user, length=32, days=7, minutes=0, key="login"):
        self.token = secrets.token_urlsafe(length)
        self.user = user
        self.user_id = user.id
        self.key = key

        ts = time.time()
        if minutes is not None:
            ts += minutes * 60
        if days is not None:
            ts += days * 24 * 60 * 60 
        self.expires_on = ts

        return self

    def to_dict(self):
        return {
            "id":self.id,
            "key":self.key,
            "token":self.token,
            "expires_on":self.expires_on,
            "user_id":self.user_id,
        }
    
    def get_user(self, session):
        u = session.query(User).filter(User.id == self.user_id).first()
        return u
    
    @staticmethod
    def authenticate(session, token):
        token_obj = session.query(Token).filter_by(token=token).first()
        if token_obj:
            return token_obj
        return None

class Profile(dbbase):
    __tablename__ = 'profiles'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    id_owner = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

    feedbacks = relationship("UserFeedback", backref="profile")

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())


class Prompt(dbbase):

    __tablename__ = 'prompts'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    id_text = Column(Integer, ForeignKey('texts.id'))
    text = relationship(Text) #actual prompt (including {variables})

    id_profile = Column(Integer, ForeignKey('users.id')) #profile that created this prompt

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

class PromptFlow(dbbase):
    __tablename__ = 'prompt_flows'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    parent_node = Column(Integer)
    nodes = relationship('Node', back_populates='prompt_flow')

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

class Node(dbbase):
    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True)
    id_prompt_flow = Column(Integer, ForeignKey('prompt_flows.id'))
    prompt_flow = relationship(PromptFlow)

    name = Column(String)
    node_type = Column(String) #prompt, storage, action etc...

    id_prompt = relationship(Integer, ForeignKey('prompts.id'))
    edges = relationship("PromptFlowEdge", backref="node")

    payload = Column(JSONB) #optional payload eg: instructions on how to execute code

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

class Edge(dbbase):
    __tablename__ = 'edges'
    id = Column(Integer, primary_key=True)
    start_node_id = Column(Integer, ForeignKey('nodes.id'))
    end_node_id = Column(Integer, ForeignKey('nodes.id'))

    start_node = relationship("Node", foreign_keys=[start_node_id])
    end_node = relationship("Node", foreign_keys=[end_node_id])

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

class PromptRun(dbbase):
    __tablename__ = 'prompt_runs'
    """ Actual instance of running a prompt flow and getting output"""
    id = Column(Integer, primary_key=True)

    id_prompt_flow = Column(Integer, ForeignKey('prompt_flows.id'))

    payload = Column(JSONB) #optional payload eg: any info on the user using the prompt

    items = relationship("PromptFlowEdge", backref="prompt_run")

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

class PromptRunItem(dbbase):
    __tablename__ = 'prompt_run_items'
    id = Column(Integer, primary_key=True)

    id_prompt_run = Column(Integer, ForeignKey('prompt_runs.id'))
    prompt_run = relationship(PromptRun)

    input_payload = Column(JSONB) 
    output_payload = Column(JSONB)

    #the node that created this item
    id_node = Column(Integer, ForeignKey('nodes.id'))

    #optional link to a text if this produces a text output
    id_text = Column(Integer, ForeignKey('texts.id'))

    feedbacks = relationship("UserFeedback", backref="prompt_run_item")

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

class UserFeedback(dbbase):
    __tablename__ = 'user_feedbacks'

    id = Column(Integer, primary_key=True)

    #prompt run item that the user interacted with and is giving feedback
    id_prompt_run_item = Column(Integer, ForeignKey('prompt_run_items.id'))
    prompt_run_item = relationship(PromptRunItem)

    #profile of the user giving the feedback, 
    #NOTE: we link profiles to feedback, so each profile can have it's own context
    id_profile = Column(Integer, ForeignKey('profiles.id'))
    profile = relationship(Profile)

    liked = Column(Boolean) #simple up / down
    rating = Column(Integer)
    rating_min = Column(Integer, default=1)
    rating_max = Column(Integer, default=10)

    #optional notes about why they liked it, or not
    id_text = Column(Integer, ForeignKey('texts.id'))
    text = relationship(Text) #actual response to the prompt

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())




class Text(dbbase):
    __tablename__ = 'texts'
    id = Column(Integer, primary_key=True)

    text = Column(String)

    openai_embedding = Column(Vector(1536)) 

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    id_textparent = Column(Integer) #if this is a sub component of the main text
    start_index = Column(Integer) #start index in parent text where this is a part
    end_index = Column(Integer) #end index in parent text where this is a part


    sentiments = relationship("SentimentScore", back_populates="text")

    def to_dict(self):
        
        d = {
            "id":self.id,
            "text":self.text,
            "created_on":self.created_on.strftime("%Y-%m-%d"),
        }
        return d


class SentimentScore(dbbase):
    __tablename__ = 'sentiment_scores'
    id = Column(Integer, primary_key=True)
    
    #source text
    text_id = Column(Integer, ForeignKey('texts.id'))
    text = relationship('Text', back_populates='sentiments')

    model_name = Column(String) #model that provided score

    score_name = Column(String) #mood, need, etc. 
    score_value = Column(Float)
    score_min = Column(Float, default=0.0)
    score_max = Column(Float, default=1.0)

    payload = Column(JSONB) #optional payload eg: list of outputs to make composite score

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

