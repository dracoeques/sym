import os
import base64
import secrets
import time
import requests

from sym.modules.db.models import Token, User

class InvalidAuth(Exception):
    pass


def authenticate_user(session, request=None, token=None):
    """ Example checks for a valid auth token in the db"""
    if token is None:
        headers = request.headers
        if "X-Api-Key" not in headers:
            raise InvalidAuth("No token provided and X-Api-Key not in headers")
        token  = headers["X-Api-Key"]
    
    now = time.time()
    
    token_obj = session.query(Token) \
        .filter(Token.token==token, Token.expires_on>=now) \
        .first()
    
    if token_obj is None:
        raise InvalidAuth("No valid tokens found")
    u = token_obj.get_user(session)
    return u


def register_user(session, payload):
    """ Given a json payload and session create a user model """
    pass

def send_user_email():
    """ """
    pass

def confirm_user_email():
    """ """
    pass