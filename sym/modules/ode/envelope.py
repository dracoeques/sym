import logging
from typing import Any, List
from dataclasses import dataclass, field
import json
from datetime import datetime
from typing import Dict, Any

@dataclass
class OdeSender:
    """ Sender of a message"""
    username: str = None
    avatar_image: str = None
    role: str = None #user, system, etc. 
    user_id: int = None
    profile_id: int = None
    date_sent: datetime = None
    
    def to_dict(self):
        d = {
            "username": self.username,
            "avatar_image": self.avatar_image,
            "role": self.role,
            "user_id": self.user_id,
            "profile_id": self.profile_id,
            "date_sent": self.date_sent.isoformat() if self.date_sent else None
        }
        return d
    
    @classmethod
    def from_dict(cls, data):
        instance = cls()
        instance.username = data.get('username')
        instance.avatar_image = data.get('avatar_image')
        instance.role = data.get('role')
        instance.user_id = data.get('user_id')
        instance.profile_id = data.get('profile_id')
        date_sent = data.get('date_sent')
        if date_sent:
            instance.date_sent = datetime.fromisoformat(date_sent)
        return instance

@dataclass
class OdePayload:
    """ Default payload type"""
    route: str = None
    action: str = None #CRUD & display, log, error
    payload: Dict[str, Any] = None  # usually a str or a dict of str -> str | int | float | bool
    sender: OdeSender = None

    def from_dict(self, d):
        self.payload = d
        return self

    def to_dict(self):
        return self.payload


@dataclass
class OdeEnvelope:
    """ Envelope for an ODE message"""
    authtoken: str = None
    request_payload: OdePayload = None
    response_payload: OdePayload = None
    
    def from_dict(self, d):
        if "request_payload" in d:
            self.request_payload = OdePayload().from_dict(d["request_payload"])
        if "response_payload" in d:
            self.response_payload = OdePayload().from_dict(d["response_payload"])
        if "authtoken" in d:
            self.authtoken = d["authtoken"]
        return self
    
    def from_str(self, s):
        d = json.loads(s)
        self.from_dict(d)
        return self

    def to_dict(self):
        d = {
            "request_payload": self.request_payload.to_dict() if self.request_payload else None,
            "response_payload": self.response_payload.to_dict() if self.response_payload else None,
        }
        #Note: authtoken is not returned in the to_dict
        #this is because we may recieve a message which is broadcasted to all users
        #in which case, we don't want to include the authtoken
        
        return d