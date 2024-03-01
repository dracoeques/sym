
from sym.modules.db.models import Profile

def get_profiles(session, user_id):
    """ Given a user_id, get all available profiles
        
    """

    profiles = session.query(Profile)\
        .filter(Profile.user_id == user_id)\
        .all()

    return profiles
    
def validate_user_profile(session, user_id, profile_id):
    """ Validate that this user has access to this profile"""
    #TODO: setup ACL logic
    profile = session.query(Profile)\
        .filter(Profile.user_id == user_id)\
        .filter(Profile.id == profile_id)\
        .first()
    if profile and profile.user_id == user_id:
        return profile
    return None

def get_default_profile(session, user_id):
    """ Gets default profile for this user
        if one doesn't exist, then create one
    """
    default_profile = session.query(Profile)\
        .filter(Profile.user_id == user_id)\
        .filter(Profile.is_default == True)\
        .first()
    
    if default_profile is None:
        default_profile = Profile()
        default_profile.name = "default"
        default_profile.user_id = user_id
        default_profile.is_default = True
        session.add(default_profile)
        session.commit()
    
    return default_profile

def set_default_profile(session, user_id, profile_id):
    profile = session.query(Profile)\
        .filter(Profile.id == profile)\
        .filter(Profile.user_id == user_id)\
        .first()
    
    if profile is None:
        raise Exception(f"Profile {profile_id} does not exist") 
    

    profiles = session.query(Profile)\
        .filter(Profile.user_id == user_id)\
        .all()
    
    #set this profile as default, 
    #set all other profiles as not default
    default_profile = None
    for p in profiles:
        if p.user_id == user_id and profile.id == profile_id:
            p.is_default = True
            default_profile = p
        else:
            p.is_default = False
    
    session.commit()

    return default_profile.to_dict()

#TODO:
#CRUD operations on profiles

def get_sym_sender(date_sent=None):
    """ Get the default SYM sender json object"""
    d = {   
            "user_id":0,
            "username": "Sym",
            "role": "AI",
            "avatar_image": "https://sym-public-assets.s3.us-west-2.amazonaws.com/icons/sym-avatar_medium.png",
            "date_sent":None,
        }
    if date_sent is not None:
        d["date_sent"] = date_sent.isoformat()
    return d