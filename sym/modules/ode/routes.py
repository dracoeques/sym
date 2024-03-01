from sqlalchemy.orm import Session

from sym.modules.ode.envelope import OdeEnvelope
from sym.modules.ode.dispatcher import OdeDispatcher

from sym.modules.db.models import MediaFeed, MediaFeedItem

from enum import Enum, auto
from functools import wraps
import re

class Action(Enum):
    CREATE = auto()
    READ = auto()
    UPDATE = auto()
    DELETE = auto()
    DISPLAY = auto()
    LOG = auto()
    ERROR = auto()
    STREAM = auto()
    # Add new actions here as needed

# Update registry to hold compiled regex patterns instead of simple route strings
action_route_registry = {}

def compile_route(route):
    type_patterns = {
        'int': r'(?P<{}>\d+)',  # Matches one or more digits, names the group
        'str': r'(?P<{}>[^/]+)' # Matches any character except '/', names the group
    }

    def replacer(match):
        param_name, param_type = match.groups()
        return type_patterns.get(param_type, type_patterns['str']).format(param_name)

    regex_pattern = re.sub(r'\{(\w+):(\w+)\}', replacer, route)
    regex_pattern = '^' + regex_pattern + '$'
    return re.compile(regex_pattern)

def action_handler(action, route=None):
    route_pattern = compile_route(route) if route else None
    
    def decorator(func):
        # Use the compiled regex pattern as the key
        action_route_registry[(action, route_pattern)] = func
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

###########
# ROUTES
###########


@action_handler(Action.CREATE, "/feed/{feed_id:int}/reply/{item_id:int}")
async def handle_reply_item(
        envelope: OdeEnvelope, 
        dispatcher: OdeDispatcher,
        session: Session,
        feed_id: int,
        item_id: int):
    
    print("feed_id", feed_id)
    print("item_id", item_id)
    payload = {
        "feed_id": feed_id,
        "item_id": item_id,
    }
    return await dispatcher.dispatch(envelope, payload)

#Read what threads you have access to
@action_handler(Action.READ, "/threads")
async def handle_read_threads(
        envelope: OdeEnvelope, 
        dispatcher: OdeDispatcher,
        session: Session):
    
    #example request payload
    example_request_payload = {}

    threads = {
        "threads":[
            {
                "id":1,
                "title":"Thread 1",
                "type":"Assesment",
                "description":"This is the first thread",
                "created_at":"2021-01-01",
                "updated_at":"2021-01-01",
                "badge":0,
            },
            {
                "id":2,
                "title":"Thread 2",
                "type":"ODE",
                "description":"This is the second thread",
                "created_at":"2021-01-01",
                "updated_at":"2021-01-01",
                "badge":0,
            },
            {
                "id":3,
                "title":"Thread 3",
                "type":"Conversation",
                "description":"This is the second thread",
                "created_at":"2021-01-01",
                "updated_at":"2021-01-01",
                "badge":0,
            },
        ]
    }
    #get the threads from the envelope payload

    #get the threads from the user

    #return the threads
    #TODO: make dataclass for threads
    #envelope.response_payload = threads
    #NOTE: for now we just use json mocks
    
    return await dispatcher.dispatch(envelope, payload=threads)

#Read a specific thread, items from the thread
@action_handler(Action.READ, "/thread-items")
async def handle_read_thread(
        envelope: OdeEnvelope, 
        dispatcher: OdeDispatcher,
        session: Session):
    

    #example request payload
    example_request_payload = {
        "id":1,
        "last_message_id":1,
        "limit":10,
    }

    thread = {
        "id": 1,
        "name":"General",
        "description":"General chat",
        "item_order": [1,2],
        "items": {
            1: {
                "id": 1,
                "item_type": "message",
                "text": "Hello, world!",
                "user": "user1",
                "timestamp": "2024-02-22T06:47:45+00:00",
                "reactions": {
                    "up": 1,
                    "down": 0,
                    "saved": 0,
                },
                "children": {
                    1: {
                        "id": 1,
                        "text": "Hello, user1!",
                        "user": "user2",
                        "timestamp": "2024-02-22T07:47:45+00:00"
                    },
                    2: {
                        "id": 2,
                        "text": "How are you?",
                        "user": "user2",
                        "timestamp": "2024-02-22T08:47:45+00:00"
                    },
                },
                "children_order": [1,2],
            },
        }
    }
    #get the threads from the envelope payload

    #get the threads from the user

    #return the threads
    #envelope.response_payload = thread
    
    return await dispatcher.dispatch(envelope, payload=thread)

##################
# ODE FEED LOGIC
#################


def me(self):
    """ Return current profile info / self info"""
    pass

def get_new_items(self):
    """ Get new items in your opportunity feed"""
    pass

def create_feed(self):
    """ create a new feed"""
    pass

def chat_with_item(self):
    """ Chat with an ODE media item"""
    pass

def scrape_new_item(self):
    """ Given a url, scrape a new item to provide insights"""
    pass