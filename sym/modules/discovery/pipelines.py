
from sym.modules.db.models import *
from sym.modules.db.db import local_session
from sym.modules.discovery.core import collect_feed_items
from sym.modules.discovery.opportunity import media_item_opportunity

from sqlalchemy.orm import aliased, sessionmaker
from sqlalchemy import create_engine, not_, exists


def associate_items_with_feeds(session=None):
    """ Given our feeds, collect items which are most relevant"""
    

    feeds = session.query(MediaFeed).all()


    for f in feeds:
        print(f"Running Feed: feed_id: {f.id}")
        new_items, err = collect_feed_items(f.id, session=session, per_topic_limit=20)
        print(f"New feed items: {len(new_items)}")
    

def run_personalizations(session=None, model="gpt-4"):
    feeds = session.query(MediaFeed).all()

    limit = 10
    ran = 0

    for f in feeds:
        
        id_profile = f.id_profile
        if id_profile is None:
            continue
        if id_profile != 26 and id_profile != 8:
            continue

        print(f"Running personalizations: feed_id: {f.id}, profile: {id_profile}")

        # Subquery to find MediaItemPersonalization for the given profile
        subquery = session.query(MediaItemPersonalization.id_media_item).filter(
            MediaItemPersonalization.id_profile == id_profile
        ).subquery()

        # Main query to find Media Items in the feed without personalization for the given profile
        query = session.query(MediaItem).join(
            MediaFeedItem, MediaItem.id == MediaFeedItem.id_media_item
        ).filter(
            MediaFeedItem.id_media_feed == f.id,
        ).outerjoin(subquery, MediaItem.id == subquery.c.id_media_item)\
        .filter(subquery.c.id_media_item == None)

        # Execute the query
        media_items = query.all()

        # Processing the results
        for item in media_items:
            #print(item.id, item.title)  # or any other fields you want to display

            text = media_item_opportunity(session=None, 
                id_profile=id_profile, 
                id_media_item=item.id)
            
            mip = MediaItemPersonalization()
            mip.id_media_item = item.id
            mip.id_profile = id_profile
            mip.model = model
            mip.text = text
            
            session.add(mip)
            session.commit()

            #print(text)
            print("personalization", mip.id)

            ran += 1

            if ran >= limit:
                break
        ran = 0
        
            
if __name__ == "__main__":
    engine,session_factory = local_session()
    session = session_factory()
    #associate_items_with_feeds(session=session)
    run_personalizations(session=session)