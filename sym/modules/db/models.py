import secrets
import time
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import relationship
from sqlalchemy import func, ForeignKey
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Date, SmallInteger
from sqlalchemy.dialects.postgresql import TSTZRANGE, TIMESTAMP, TSRANGE, JSONB 
from sqlalchemy.dialects.postgresql import UUID, VARCHAR, TEXT, INTEGER, DATE, NUMERIC, ARRAY
from sqlalchemy.dialects.postgresql import BOOLEAN, DOUBLE_PRECISION, BIGINT, TIME, SMALLINT, TEXT
from sqlalchemy import Enum


from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

import bcrypt
from pgvector.sqlalchemy import Vector


dbbase = declarative_base()

class User(dbbase):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(50), unique=True, nullable=False)
    username = Column(String(50))
    password_hash = Column(String(128), nullable=False)

    profiles = relationship('Profile', back_populates='user')

    tokens = relationship('Token', back_populates='user')

    #prompt_views = relationship('PromptView', back_populates='user')

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    first_name = Column(String)
    last_name = Column(String)
    avatar_image = Column(String)

    def from_dict(self, payload):
        self.username = payload.get("username")
        self.email = payload.get("email")
        self.first_name = payload.get("first_name")
        self.last_name = payload.get("last_name")
        self.avatar_image = payload.get("avatar_image")
        return self
    
    def to_dict(self):
        return {
            "id":self.id,
            "username":self.username,
            "email":self.email,
            "first_name":self.first_name,
            "last_name":self.last_name,
            "avatar_image":self.avatar_image,
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

    def __repr__(self):
        return f'User: {self.id} {self.email} {self.username}'



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


    def generate(self, user, length=32, days=30, minutes=0, key="login"):
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
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

    is_default = Column(Boolean, default=False)

    prompt_runs = relationship("PromptRun", back_populates="profile")
    prompt_run_items = relationship("PromptRunItem", back_populates="profile")
    feedbacks = relationship("UserFeedback", back_populates="profile")
    feeds = relationship("MediaFeed", back_populates="profile")

    flows = relationship("PromptFlow", back_populates="profile")

    seed_text = Column(String)

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'Sym: {self.id} {self.name}'

    def to_dict(self):
        d = {
            "id":self.id,
            "name":self.name,
            "description":self.description,
            "user_id":self.user_id,
            "created_on":self.created_on,
            "updated_on":self.updated_on,
        }
        return d
    
    @classmethod
    def from_dict(cls, data):
        instance = cls()
        instance.id = data.get('id')
        instance.name = data.get('name')
        instance.description = data.get('description')
        instance.user_id = data.get('user_id')
        instance.created_on = data.get('created_on')
        instance.updated_on = data.get('updated_on')
        return instance


class ProfileDatum(dbbase):
    __tablename__ = 'profile_datums'

    """ Profile datums are key pieces of information that can be used to 
        inform personality / style / context about this profile
    """
    id = Column(Integer, primary_key=True)

    kind = Column(String) #key-value, question-answer etc.
    category = Column(String) #values, music, food etc. What is the context for this datum?
    key = Column(String) #key or question
    value = Column(String) #value or response
    
    id_profile = Column(Integer, ForeignKey('profiles.id')) #profile that created this prompt
    profile = relationship(Profile)

    #DEFAULT IS ADA2 - TODO: setup separate embedding table & through table for model agnostic embeddings
    openai_category_embedding = Column(Vector(1536))
    openai_key_embedding = Column(Vector(1536))  
    openai_value_embedding = Column(Vector(1536))  

    #reference to the run_item where this data is being pulled from
    id_run_item = Column(Integer, ForeignKey('prompt_run_items.id'))

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self, include_vectors=False):
        d = {
            "id":self.id,
            "category":self.category,
            "key":self.key,
            "value":self.value,
            "id_profile":self.id_profile,
            "id_run_item":self.id_run_item,
            "created_on":self.created_on,
            "updated_on":self.updated_on,
        }

        if include_vectors == True:
            d["openai_category_embedding"] = self.openai_category_embedding
            d["openai_key_embedding"] = self.openai_key_embedding
            d["openai_value_embedding"] = self.openai_value_embedding

        return d

class ProfileDatumContextResponse(dbbase):
    __tablename__ = 'profile_datum_context_responses'

    """ Based on the context of the topic,
        a user can rate how relevant these profile datums were
    """
    id = Column(Integer, primary_key=True)

    
    id_ranker = Column(Integer, ForeignKey('profiles.id')) 
    ranker_profile = relationship(Profile)

    #if the ranker is a model, include the model name
    model = Column(String)

    #original context that started this query
    id_text = Column(Integer, ForeignKey('texts.id'))
    #text = relationship(Text)

    #datum that was returned
    id_profile_datum = Column(Integer, ForeignKey('profile_datums.id')) 
    profile_datum = relationship(ProfileDatum)

    liked = Column(Boolean) #simple up / down was this relevant to the context?

    def to_dict(self):

        d = {
            "id":self.id,
            "id_ranker":self.id_ranker,
            "id_text":self.id_text,
            "id_profile_datum":self.id_profile_datum,
            "liked":self.liked,
        }

        return d
    

class Text(dbbase):
    __tablename__ = 'texts'
    id = Column(Integer, primary_key=True)

    text = Column(String)

    #TODO: setup separate embedding table & through table for model agnostic embeddings
    openai_embedding = Column(Vector(1536)) 

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    id_textparent = Column(Integer) #if this is a sub component of the main text
    start_index = Column(Integer) #start index in parent text where this is a part
    end_index = Column(Integer) #end index in parent text where this is a part


    sentiments = relationship("SentimentScore", back_populates="text")

    def to_dict(self, include_vectors=False):
        
        d = {
            "id":self.id,
            "text":self.text,
            "created_on":self.created_on.strftime("%Y-%m-%d"),
        }

        if include_vectors == True:
            d["openai_embedding"] = self.openai_embedding

        return d


class Prompt(dbbase):

    __tablename__ = 'prompts'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    category = Column(String)
    subcategory = Column(String)
    

    #Note: it's too cumbersome to keep text separate at this point
    #a potential refactor might make sense, but for now we're leaving the fk
    #but utilizing the text column
    id_text = Column(Integer, ForeignKey('texts.id'))
    #text = relationship(Text) #actual prompt (including {variables})

    rawtext = Column(String) #the text, not parsed, can have options such as {variable|a,b,c,}
    text = Column(String) #parsed text, can have {variable} but shouldn't have options {variable|a,b,c,} etc.
    openai_embedding = Column(Vector(1536))  #embeds the text 

    system = Column(String)
    openai_embedding_system = Column(Vector(1536))  #embeds the system message

    variables = relationship("PromptVariable", back_populates="prompt")

    #TODO: move from users -> profiles 
    id_profile = Column(Integer, ForeignKey('users.id')) #profile that created this prompt

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    #TODO: finish migration
    #payload sent to prompt - should include messages key
    #input_payload = Column(JSONB)
    
    #payload returned, - should include response_text key and payload key (original json response)
    #output_payload = Column(JSONB)

    def to_dict(self):
        
        d = {
            "id":self.id,
            "name":self.name,
            "text":self.text,
            "rawtext":self.rawtext,
            "created_on":self.created_on.strftime("%Y-%m-%d"),
            "category":self.category,
            "subcategory":self.subcategory,
            "description":self.description,
            "system":self.system,
        }

        variables = {}
        for v in self.variables:
            variables[v.name] = v.to_dict()
        d["variables"] = variables
        return d
    
    def from_dict(self, d):
        if "name" in d:
            self.name = d["name"]
        if "description" in d:
            self.description = d["description"]
        if "category" in d:
            self.category = d["category"].lower().strip()
        if "subcategory" in d:
            self.subcategory = d["subcategory"].lower().strip()
        if "rawtext" in d:
            self.rawtext = d["rawtext"]
        if "text" in d:
            self.text = d["text"]  
        if "system" in d:
            self.system = d["system"]      
        return self


class PromptVariable(dbbase):
    __tablename__ = 'prompt_variables'
    id = Column(Integer, primary_key=True)

    prompt_id = Column(Integer, ForeignKey('prompts.id'))
    prompt = relationship('Prompt', back_populates='variables')

    name = Column(String)

    options = relationship("PromptVariableOption", back_populates="prompt_variable")

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        
        d = {
            "id":self.id,
            "name":self.name,
        }
        options = []
        for o in self.options:
            options.append(o.to_dict())
        d["options"] = options
        return d

    def from_dict(self, d, prompt_id=None):
        if "name" in d:
            self.name = d["name"]
        elif "variable_name" in d:
            self.name = d["variable_name"]
        
        if prompt_id is not None:
            self.prompt_id = prompt_id
        if "prompt_id" in d:
            self.prompt_id = d["prompt_id"]
        return self
    


class PromptVariableOption(dbbase):
    __tablename__ = 'prompt_variable_options'
    id = Column(Integer, primary_key=True)

    prompt_variable_id = Column(Integer, ForeignKey('prompt_variables.id'))
    prompt_variable = relationship('PromptVariable', back_populates='options')

    value = Column(String)
    label = Column(String)

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        
        d = {
            "id":self.id,
            "label":self.label,
            "value":self.value,
        }
        return d

    def from_dict(self, d, prompt_variable_id=None):
        if "prompt_variable_id" in d:
            self.prompt_variable_id = d["prompt_variable_id"]
        elif prompt_variable_id is not None:
            self.prompt_variable_id = prompt_variable_id
        if "value" in d:
            self.value = d["value"]
        if "label" in d:
            self.value = d["label"]
        return self


class PromptFlow(dbbase):
    __tablename__ = 'prompt_flows'

    #TODO: 
    #when editing a prompt flow if it has had a run already, it should 
    #be cloned which will preserve previous runs integrity
    #ancestor_id = Column(Integer, index=True)

    #TODO: 
    #add an owner sym
    id_owner = Column(Integer, ForeignKey('profiles.id'))
    profile = relationship(Profile)

    #TODO: how to disambiguate prompt flows by project?
    #ie: two users make a prompt flow with the same name, category, subcategory


    #TODO: how to assign an owner to a prompt flow
    #ie: user X created this flow and would like to share it with you

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    category = Column(String)
    subcategory = Column(String)

    parent_node = Column(Integer) #start node
    nodes = relationship('Node', back_populates='prompt_flow')

    edges = relationship("Edge", back_populates='prompt_flow')

    payload = Column(JSONB) #additional configuration such as frontend datastructure

    hidden = Column(Boolean, default=False) #hidden prompt flows won't show up in views

    version = Column(Integer, default=2) #version 2 is now default

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self, deep=False):
        d = {
            "id":self.id,
            "name":self.name,
            "title":self.name, #TODO: remove title and use name (requires front end checks)
            "description":self.description,
            "category":self.category,
            "subcategory":self.subcategory,
            "parent_node":self.parent_node,
            "payload":self.payload,
            "version":self.version,
            
        }
        if self.category:
            d["category"] = self.category
        else:
            d["category"] = ""
        
        if self.subcategory:
            d["subcategory"] = self.subcategory
        else:
            d["subcategory"] = ""
        
        if self.description:
            d["description"] = self.description
        else:
            d["description"] = ""

        if self.created_on:
            d["created_on"] = self.created_on.strftime("%Y-%m-%d")
        if self.updated_on:
            d["updated_on"] = self.updated_on.strftime("%Y-%m-%d")

        if deep:
            pass
            #TODO: add nodes and to_dict method
            # nodes =[]
            # for node in nodes:
            #     pass

        return d

    def from_dict(self, d):

        if "id" in d:
            self.id = d["id"]
        if "name" in d:
            self.name = d["name"]
        if "descripton" in d:
            self.description = d["description"]
        if "category" in d:
            self.category = d["category"]
        if "subcategory" in d:
            self.subcategory = d["subcategory"]
        if "parent_node" in d:
            self.parent_node = d["parent_node"]
        if "payload" in d:
            self.payload = d["payload"]
        if "version" in d:
            self.version = d["version"]
        return self


class Node(dbbase):
    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True)
    id_prompt_flow = Column(Integer, ForeignKey('prompt_flows.id'))
    prompt_flow = relationship(PromptFlow)

    id_str = Column(String) #front end logic uses string ids, this allows 2-way binding

    name = Column(String)
    node_type = Column(String) #prompt, storage, action etc...

    id_prompt = Column(Integer, ForeignKey('prompts.id'))
    #start_edges = relationship("Edge", back_populates="start_node")
    #end_edges = relationship("Edge", back_populates="end_node")

    payload = Column(JSONB) #optional payload eg: instructions on how to execute code

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())
    deleted = Column(Boolean, default=False)

    def from_dict(self, d):
        if "id" in d:
            self.id = d["id"]
        if "id_prompt_flow" in d:
            self.id_prompt_flow = d["id_prompt_flow"]
        if "prompt_flow" in d:
            self.prompt_flow = d["prompt_flow"]
        if "name" in d:
            self.name = d["name"]
        if "node_type" in d:
            self.node_type = d["node_type"]
        if "id_prompt" in d:
            self.id_prompt = d["id_prompt"]
        if "payload" in d:
            self.payload = d["payload"]
        if "created_on" in d:
            self.created_on = d["created_on"]
        if "updated_on" in d:
            self.updated_on = d["updated_on"]
        return self
    
    def to_dict(self):
        d = {
            "id":self.id,
            "id_prompt_flow":self.id_prompt_flow,
            "prompt_flow":self.prompt_flow,
            "name":self.name,
            "node_type":self.node_type,
            "id_prompt":self.id_prompt,
            "payload":self.payload,   
        }

        if self.created_on:
            d["created_on"] = self.created_on.strftime("%Y-%m-%d")
        if self.updated_on:
            d["updated_on"] = self.created_on.strftime("%Y-%m-%d")

        return d



class Edge(dbbase):
    __tablename__ = 'edges'
    id = Column(Integer, primary_key=True)
    start_node_id = Column(Integer, ForeignKey('nodes.id'))
    end_node_id = Column(Integer, ForeignKey('nodes.id'))

    id_str = Column(String) #front end logic uses string ids, this allows 2-way binding

    #start_node = relationship("Node", foreign_keys=[start_node_id])
    #end_node = relationship("Node", foreign_keys=[end_node_id])

    name = Column(String)

    #Payload for additional edge metadata such as edge weights
    payload = Column(JSONB) 

    id_prompt_flow = Column(Integer, ForeignKey('prompt_flows.id'))
    prompt_flow = relationship(PromptFlow)

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())
    deleted = Column(Boolean, default=False)

    def from_dict(self, d):
        if "id" in d:
            self.id = d["id"]
        if "start_node_id" in d:
            self.start_node_id = d["start_node_id"]
        if "end_node_id" in d:
            self.end_node_id = d["end_node_id"]
        if "payload" in d:
            self.payload = d["payload"]
        if "id_prompt_flow" in d:
            self.id_prompt_flow = d["id_prompt_flow"]
        if "prompt_flow" in d:
            self.prompt_flow = d["prompt_flow"]
        if "created_on" in d:
            self.created_on = d["created_on"]
        if "updated_on" in d:
            self.updated_on = d["updated_on"]
        return self

    def to_dict(self):
        d = {
            "id":self.id,
            "start_node_id":self.start_node_id,
            "end_node_id":self.end_node_id,
            "id_prompt_flow": self.id_prompt_flow,
            "prompt_flow":self.prompt_flow,
        }

        if self.payload:
            d["payload"] = self.payload
        
        if self.created_on:
            d["created_on"] = self.created_on.strftime("%Y-%m-%d")
        if self.updated_on:
            d["updated_on"] = self.updated_on.strftime("%Y-%m-%d")
        return d

class PromptRun(dbbase):
    __tablename__ = 'prompt_runs'
    """ Actual instance of running a prompt flow and getting output"""
    id = Column(Integer, primary_key=True)

    id_prompt_flow = Column(Integer, ForeignKey('prompt_flows.id'))

    #sym who did the prompt run
    #profile of the user giving the feedback, 
    #NOTE: we link profiles to prompt runs, so each profile can have it's own context
    id_profile = Column(Integer, ForeignKey('profiles.id'))
    profile = relationship(Profile)

    payload = Column(JSONB) #the payload and data at the time of running

    items = relationship("PromptRunItem", back_populates="prompt_run")

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    #did this user successfully hit a finish node?
    completed = Column(Boolean, default=False)

class PromptRunItem(dbbase):
    __tablename__ = 'prompt_run_items'
    id = Column(Integer, primary_key=True)

    id_prompt_run = Column(Integer, ForeignKey('prompt_runs.id'))
    prompt_run = relationship(PromptRun)

    input_payload = Column(JSONB) #any data that initialized the node
    output_payload = Column(JSONB) #any resulting data from running the node

    #the node that created this item
    id_node = Column(Integer, ForeignKey('nodes.id'))

    #optional link to a text if this produces a text output
    id_text = Column(Integer, ForeignKey('texts.id'))

    #Give feedback to a run item
    feedbacks = relationship("UserFeedback", back_populates="prompt_run_item")

    #Associate a single run item with a single profile who ran this node
    id_profile = Column(Integer, ForeignKey('profiles.id'))
    profile = relationship(Profile)

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    #TODO: convenience columns added for simplicity when pulling data
    # node_type = Column(String) #node_ype
    # message = Column(String) #actual text sent
    # action = Column(String) #display, silent etc.
    # sender = Column(String) #user / bot

    def from_prompt_node(self, n=None, id_prompt_run=None):
        self.id_prompt_run = id_prompt_run
        self.input_payload = n.input_payload
        self.output_payload = n.output_payload
        self.node_type = n.node_type
        if n.id:
            self.id_node = n.id
            print("self.id_node", self.id_node)
        return self

    


class UserFeedback(dbbase):
    __tablename__ = 'user_feedbacks'

    id = Column(Integer, primary_key=True)

    #prompt run overall that the user interacted with and is giving feedback
    id_prompt_run = Column(Integer, ForeignKey('prompt_runs.id'))
    prompt_run = relationship(PromptRun)

    #optional - prompt run item that the user interacted with and is giving feedback
    id_prompt_run_item = Column(Integer, ForeignKey('prompt_run_items.id'))
    prompt_run_item = relationship(PromptRunItem)

    #profile of the user giving the feedback, 
    #NOTE: we link profiles to feedback, so each profile can have it's own context
    id_profile = Column(Integer, ForeignKey('profiles.id'))
    profile = relationship(Profile)

    payload = Column(JSONB) #payload to store additional information

    liked = Column(Boolean) #simple up / down
    rating = Column(Integer)
    rating_min = Column(Integer, default=1)
    rating_max = Column(Integer, default=10)

    #optional notes about why they liked it, or not
    id_text = Column(Integer, ForeignKey('texts.id'))
    text = relationship(Text) #actual user feedback response to the prompt run lives here

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())




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


class PromptDeck(dbbase):
    __tablename__ = 'prompt_decks'
    """ Prompt decks are ways to organize LLM tasks and contexts together in columns"""

    id = Column(Integer, primary_key=True)
    id_owner = Column(Integer, ForeignKey('users.id'))
    name = Column(String)

    emoji = Column(String)

    ## archetypes are uneditable prompt-decks that are made for prebuilt purposes
    is_archetype = Column(Boolean, default=False)
    category = Column(String)
    subcategory = Column(String)
    description = Column(String)

    columns = relationship('PromptDeckColumn', back_populates='deck')

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        d = {
            "id":self.id,
            "id_owner":self.id_owner,
            "name":self.name,
            "emoji":self.emoji,
            "is_archetype":self.is_archetype,
            "category":self.category,
            "subcategory":self.subcategory,
            "description":self.description,
            "columns":[],
            "created_on":self.created_on.strftime("%Y-%m-%d"),
            "updated_on":self.created_on.strftime("%Y-%m-%d")
        }
        if self.columns:
            columns = [x.to_dict() for x in self.columns]
            columns.sort(key=lambda x: x["order"])
            d["columns"] = columns
        return d


class PromptDeckColumn(dbbase):
    __tablename__ = 'prompt_deck_columns'
    """ Prompt column is a container around a set of PromptDeckColumnItem"""

    id = Column(Integer, primary_key=True) 
    id_deck = Column(Integer, ForeignKey('prompt_decks.id'))
    deck = relationship(PromptDeck)

    name = Column(String)
    key = Column(String) #useful for defining the type of column / version

    order = Column(Integer)  #what preference is this in the view (TODO: dynamically allocate this)

    items = relationship('PromptDeckColumnItem', back_populates='column')
    
    #prompt run items, a historical reference to the interaction in this column

    def to_dict(self):
        return {
            "id":self.id,
            "id_deck":self.id_deck,
            "name":self.name,
            "key":self.key,
            "order":self.order,
            "items":[x.to_dict() for x in self.items],
            #"created_on":self.created_on.strftime("%Y-%m-%d"),
            #"updated_on":self.created_on.strftime("%Y-%m-%d")
        }


class PromptDeckColumnItem(dbbase):
    __tablename__ = 'prompt_deck_column_items'
    """ Prompt Associate N Items with Prompt Deck Columns"""
    
    id = Column(Integer, primary_key=True) 
    
    id_column = Column(Integer, ForeignKey('prompt_deck_columns.id'))
    column = relationship(PromptDeckColumn)

    key = Column(String) #flow, prompt lib, prompt_runs, prompt
    
    order = Column(Integer)  #what preference is this in the view (TODO: dynamically allocate this)

    #optional values (can be null)
    id_prompt = Column(Integer, ForeignKey('prompts.id'))
    id_prompt_flow = Column(Integer, ForeignKey('prompt_flows.id'))
    
    def to_dict(self):
        d = {
            "id":self.id,
            "id_column":self.id_column,
            "key":self.key,
            "order":self.order,
            "id_prompt":self.id_prompt,
            "id_prompt_flow":self.id_prompt_flow,
        }

        #optionally get values here
        # if self.key == "prompt_flow":
        #     pass

        return d

class MediaSource(dbbase):
    __tablename__ = 'media_sources'
    """ A place to get relevant media sources """
    id = Column(Integer, primary_key=True) 
    name = Column(String) #reddit, ycombinator, google, etc.
    url = Column(String) #source url / homepage

    media_items = relationship("MediaItem", back_populates="source")

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

class MediaItem(dbbase):
    __tablename__ = 'media_items'
    """ A post, article, event or other item"""
    id = Column(Integer, primary_key=True) 

    id_source = Column(Integer, ForeignKey('media_sources.id'))
    source = relationship("MediaSource", back_populates="media_items")
    
    kind = Column(String) #article, video, event, post, etc.
    source_url = Column(String) #source url
    title = Column(String) #title / headline
    summary = Column(String) #summary / blurb about the item
    image = Column(String) #optional image for media
    payload = Column(JSONB) #optional payload eg: video url etc. 
    body_text = Column(String) #scraped text for this item

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        d = {
            "id":self.id,
            "id_source":self.id_source,
            "kind":self.kind,
            "source_url":self.source_url,
            "title":self.title,
            "summary":self.summary,
            "image":self.image,
            "payload":self.payload,

            "created_on":self.created_on.isoformat(),
        }
        if self.updated_on:
            d['updated_on'] = self.updated_on.isoformat()
        return d


class MediaTag(dbbase):
    __tablename__ = 'media_tags'

    id = Column(Integer, primary_key=True)

    tag = Column(String) #lowercase string
    raw_tag = Column(String) #maintains capitalization
    
    openai_tag_embedding = Column(Vector(1536)) # ADA2 embedding of raw_tag column

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())


class MediaItemTag(dbbase):
    __tablename__ = 'media_item_tags'
    """ Associate a media item with a tag """
    id = Column(Integer, primary_key=True)

    id_media_item = Column(Integer, ForeignKey('media_items.id'))
    item = relationship(MediaItem)

    id_media_tag = Column(Integer, ForeignKey('media_tags.id'))
    item = relationship(MediaItem)

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())



class MediaItemPrediction(dbbase):
    __tablename__ = 'media_item_predictions'
    """ Given a media item and a profile, how likely is this user to find this relevant / interesting """
    id = Column(Integer, primary_key=True)

    id_media_item = Column(Integer, ForeignKey('media_items.id'))
    item = relationship(MediaItem)
    
    id_profile =  Column(Integer, ForeignKey('profiles.id'))
    profile = relationship(Profile)

    model = Column(String) #model key which provided the prediction
    prediction_name = Column(String, default="relevant") #prediction could be along multiple axes, like: actionable, interesting, relevant 
    prediction_score = Column(Float) #normalized from 0 -> 1.0


    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

class MediaItemPersonalization(dbbase):
    __tablename__ = 'media_item_personalizations'
    """ Given a media item and a profile, provide personalized insights for this individual """
    id = Column(Integer, primary_key=True)

    id_media_item = Column(Integer, ForeignKey('media_items.id'))
    item = relationship(MediaItem)
    
    id_profile =  Column(Integer, ForeignKey('profiles.id'))
    profile = relationship(Profile)

    model = Column(String) #model key which provided the personalization
    text = Column(String) #any personalized insights are stored here

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    #additional personalizations
    personalized_image_url = Column(String)
    personalized_title = Column(String)
    personalized_summary = Column(String)
    personalized_payload = Column(JSONB)
    personalized_tags = Column(ARRAY(String))

    def to_dict(self):
        d = {
            'id': self.id,
            'id_media_item': self.id_media_item,
            'id_profile': self.id_profile,
            'model': self.model,
            'text': self.text,
            'created_on': self.created_on.isoformat(),
            
            'personalized_image_url': self.personalized_image_url,
            'personalized_title': self.personalized_title,
            'personalized_summary': self.personalized_summary,
            'personalized_payload': self.personalized_payload,
            'personalized_tags': self.personalized_tags,
        }
        if self.updated_on:
            d['updated_on'] = self.updated_on.isoformat()
        return d

class MediaInteraction(dbbase):
    __tablename__ = 'media_interactions'
    id = Column(Integer, primary_key=True)
    kind = Column(String)  # e.g., "view" "upvote", "save", "downvote", "click"
    
    id_profile = Column(Integer, ForeignKey('profiles.id'))
    profile = relationship(Profile)
    
    id_media_item = Column(Integer, ForeignKey('media_items.id'))
    item = relationship(MediaItem)

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())


class MediaFeed(dbbase):
    __tablename__ = 'media_feeds'
    id = Column(Integer, primary_key=True)

    name = Column(String)
    description = Column(String)
    is_default = Column(Boolean, default=False)

    items = relationship('MediaFeedItem', back_populates='feed')
    topics = relationship('MediaFeedTopic', back_populates='feed')

    #optional owner of feed
    id_profile =  Column(Integer, ForeignKey('profiles.id'))
    profile = relationship(Profile)

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        d = {
            "id":self.id,
            "name":self.name,
            "description":self.description,
            "id_profile":self.id_profile,
        }

        #topics
        topics = []
        for mft in self.topics:
            topics.append(mft.topic.to_dict())
        d["topics"] = topics
        return d


class MediaTopic(dbbase):
    __tablename__ = 'media_topics'
    id = Column(Integer, primary_key=True)

    topic = Column(String) #lowercase / stripped name
    openai_topic_embedding = Column(Vector(1536)) # ADA2 embedding of topic column

    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "id":self.id,
            "topic":self.topic,
        }

class MediaFeedTopic(dbbase):
    __tablename__ = 'media_feed_topics'
    id = Column(Integer, primary_key=True)

    id_media_feed = Column(Integer, ForeignKey('media_feeds.id'))
    feed = relationship(MediaFeed)

    id_media_topic = Column(Integer, ForeignKey('media_topics.id'))
    topic = relationship(MediaTopic)
    
    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    

class MediaFeedItem(dbbase):
    __tablename__ = 'media_feed_items'
    id = Column(Integer, primary_key=True)

    id_media_item = Column(Integer, ForeignKey('media_items.id'))
    item = relationship(MediaItem)

    id_media_feed = Column(Integer, ForeignKey('media_feeds.id'))
    feed = relationship(MediaFeed)


    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

