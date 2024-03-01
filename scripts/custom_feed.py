from sqlalchemy import select

from sym.modules.db.models import *

#custom feed
#add interests / topics
#use vector semantic similarity with tags to find similar tagged items


def main(topics=None):
    """ Given a set of topics, find the most relevant items"""


    for topic in topics:
        items = get_relevant_items()

def get_relevant_items(topic, session=None):
    #get any media items which are relevant to this topic

    #first embed the topic if it doesnt exist yet
    t = get_or_create_media_topic(topic, session=session)

    #then get the most relevant tags,rank by distance
    #session.scalars(select(MediaItem.embedding.l2_distance([3, 1, 2])))
    tags = get_relevant_tags_by_topic(t, session=session)

    # pull in any media_items which match those tags
    #and aren't yet part of the feed
    items = get_media_items_by_tags(tags, session=session)

    



    pass

def get_or_create_media_topic(topic, session=None):
    pass

def get_relevant_tags_by_topic(t, session=None):
    pass

def get_media_items_by_tags(tags, session=None):
    pass