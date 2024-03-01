import time
from sym.modules.db.models import Token


class InvalidAuth(Exception):
    pass


def authenticate_api_user(session, request):
    """ Authenticate a user by the headers in the api request"""
    headers = request.headers
    if "X-Api-Key" not in headers:
        raise InvalidAuth("X-Api-Key not in headers")
    token  = headers["X-Api-Key"]
    now = time.time()
    
    token_obj = session.query(Token) \
        .filter(Token.token==token, Token.expires_on>=now) \
        .first()
    
    if token_obj is None:
        raise InvalidAuth("No valid token found")
    u = token_obj.get_user(session)
    return u

def authenticate_ws_user(session, envelope):
    """ Authenticate a user by the authtoken in the websocket envelope"""
    if not envelope or envelope.authtoken is None:
        raise InvalidAuth("No authtoken provided in envelope")
    token = envelope.authtoken
    now = time.time()
    
    token_obj = session.query(Token) \
        .filter(Token.token==token, Token.expires_on>=now) \
        .first()
    
    if token_obj is None:
        raise InvalidAuth("No valid token found")
    u = token_obj.get_user(session)
    return u