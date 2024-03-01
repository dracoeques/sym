import os
import json

# from scipy import spatial
from numpy import dot
from numpy.linalg import norm
from sqlalchemy import desc


from sqlalchemy import select

from sym.modules.db.db import *
from sym.modules.db.models import *

from sym.modules.discovery.core import get_or_embed_topic

def cos_sim(a,b):
    return dot(a, b)/(norm(a)*norm(b))


def distances(topic, limit=10, max_embedding_distance=0.5):
    """ Return a list of media items, and their L2 distances"""
    eng,fact = local_session()
    session = fact()

    t = get_or_embed_topic(topic, session=session)

    tags = session.scalars(select(MediaTag)\
                                #.join(MediaItemTag, MediaItemTag.id_media_item == MediaItem.id)\
                                #.join(MediaTag, MediaTag.id == MediaItemTag.id_media_tag)\
                                .filter(MediaTag.openai_tag_embedding.l2_distance(t.openai_topic_embedding) < max_embedding_distance)\
                                .order_by(MediaTag.openai_tag_embedding.l2_distance(t.openai_topic_embedding))\
                                .limit(limit))
    
    for tag in tags:
        
        # item,tag = tup
        # print(item)
        # print(tag)
    

        dist = session.execute(
            select(MediaTag.openai_tag_embedding.l2_distance(t.openai_topic_embedding))
            .filter(MediaTag.id == tag.id)
        ).scalars().first()
        # dist = session.scalars(select(MediaTag.openai_tag_embedding.l2_distance(t.openai_topic_embedding)))\
        #     .where(MediaTag.id == tag.id)\
        #     .first()
        print(tag.tag, f"{dist:.3f}")




if __name__ == "__main__":
    topic = "neuroscience"
    #topic = "collaboration"
    #topic = "start up"
    distances(topic)