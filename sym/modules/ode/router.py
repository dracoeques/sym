from enum import Enum, auto
from functools import wraps

class Action(Enum):
    CREATE = auto()
    READ = auto()
    UPDATE = auto()
    DELETE = auto()
    # Add new actions here as needed



# Registry to hold action (and route) to function mappings
action_route_registry = {}

def action_handler(action, route=None):
    def decorator(func):
        # Register the function for the given action and route
        action_route_registry[(action, route)] = func
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator