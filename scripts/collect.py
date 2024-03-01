import os
import json

# from scipy import spatial
from numpy import dot
from numpy.linalg import norm
from sqlalchemy import desc


from sqlalchemy import select

from sym.modules.db.db import *
from sym.modules.db.models import *

from sym.modules.discovery.core import get_or_embed_topic, get_discovery_feed



def get_new_items(feed_id, topic, limit=10, max_embedding_distance=0.5):
    """ Return a list of media items, and their L2 distances"""
    eng,fact = local_session()
    session = fact()

    t = get_or_embed_topic(topic, session=session)

    feed,err = get_discovery_feed(feed_id, session=session)

    # Subquery to find MediaItem IDs already in the MediaFeed
    subquery = select(MediaFeedItem.id_media_item).filter(MediaFeedItem.id_media_feed == feed.id).subquery()

    
    new_items = session.scalars(select(MediaItem)\
                            .join(MediaItemTag, MediaItemTag.id_media_item == MediaItem.id)\
                            .join(MediaTag, MediaTag.id == MediaItemTag.id_media_tag)\
                            .outerjoin(subquery, MediaItem.id == subquery.c.id_media_item)
                            .filter(subquery.c.id_media_item == None)\
                            .filter(MediaTag.openai_tag_embedding.l2_distance(t.openai_topic_embedding) < max_embedding_distance)\
                            .order_by(MediaTag.openai_tag_embedding.l2_distance(t.openai_topic_embedding))\
                            .limit(limit))
                                

    
    for item in new_items:
        
        # item,tag = tup
        print(item.title)
        # print(tag)
    

        # dist = session.execute(
        #     select(MediaTag.openai_tag_embedding.l2_distance(t.openai_topic_embedding))
        #     .filter(MediaTag.id == tag.id)
        # ).scalars().first()
        # # dist = session.scalars(select(MediaTag.openai_tag_embedding.l2_distance(t.openai_topic_embedding)))\
        # #     .where(MediaTag.id == tag.id)\
        # #     .first()
        # print(tag.tag, f"{dist:.3f}")




if __name__ == "__main__":

    topic = "neuroscience"
    #topic = "collaboration"
    #topic = "start up"
    get_new_items(1, topic)