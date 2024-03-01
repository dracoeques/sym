import os

from sym.modules.db.db import *
from sym.modules.db.models import *

def add_user(
        session=None,
        email=None, 
        passw=None):
    
    if email is None or passw is None:
        raise Exception("Email and password cannot be None")
    
    #check if user exists
    u  = session.query(User)\
        .filter(User.email == email)\
        .first()
    if u:
        return u

    #add user
    u = User(email=email)
    u.hash_password(passw)
    session.add(u)
    session.commit()
    return u
    
def add_default_sym(
        session=None,
        user=None,
        profile_name="default",
    ):
    """ Add our default sym profile"""
    if session is None or user is None:
        raise Exception("Session and User cannot be None")

    #check if profile exists
    p  = session.query(Profile)\
        .filter(Profile.user_id == user.id)\
        .filter(Profile.is_default == True)\
        .first()
    if p:
        return p
    #create default profile
    p = Profile(name=profile_name, user_id=user.id, is_default=True)
    session.add(p)
    session.commit()
    return p


if __name__ == "__main__":

    eng,fact = local_session()
    session = fact()

    names = [
        "blake", 
        "blake2",
        "eben", 
        "cam", 
        "ted", 
        "josh", 
        "joe", 
        "warren", 
        "alexander", 
        "charles",
        "camille",
        "sean",
        "kristin",
        "bonnie",
        "george",
        "laura",
        "alex",
    ]
    
    for name in names:
        u = add_user(
            session=session, 
            email=os.getenv(f"{name}_email"), 
            passw=os.getenv(f"{name}_pass")
        )
        print(u)
        p = add_default_sym(
            session=session,
            user=u)
        print(p)
        
    

    


