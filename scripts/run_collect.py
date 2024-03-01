
from sym.modules.db.db import *
from sym.modules.db.models import *

from sym.modules.discovery.core import collect_feed_items

eng,fact = local_session()
session = fact()

# feeds = session.query(Feed)

feed_id = 9

collect_feed_items(feed_id, session=session)