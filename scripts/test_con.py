from sym.modules.db.db import *
from sym.modules.db.models import *

eng,fact = local_session()
session = fact()

u  = session.query(User).all()
print(u)
