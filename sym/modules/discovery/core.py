
from sqlalchemy import select

import random 
from sym.modules.db.models import *
from sym.modules.db.db import local_session

from sym.modules.auth.profile import get_sym_sender
from sym.modules.utils.openaiapi import get_openai_embedding, prompt_openai, prompt_openai_async

from sym.modules.personalization.relevant_context import get_relevant_profile_datums

def get_default_discovery_feed(profile_id=None, session=None, page=1):

    if session is None:
        engine,session_factory = local_session()
        session = session_factory()
    
    feed = session.query(MediaFeed)\
            .filter(MediaFeed.id_profile == profile_id)\
            .filter(MediaFeed.is_default == True)\
            .first()
    if feed is None:
        return None,f"Error, no default discovery feed for user found"
    return feed,None


def get_discovery_feeds(profile_id=None, session=None):
    """Get all discovery feeds for the specified user.

    Args:
        profile_id (int): The ID of the user's profile.
        session (Session, optional): The database session. If not provided, a new session will be created.
        

    Returns:
        tuple: A tuple containing a list of discovery feeds and an error message. If successful, the error message will be None.
    """
    if session is None:
        engine, session_factory = local_session()
        session = session_factory()

    feeds = session.query(MediaFeed)\
        .filter(MediaFeed.id_profile == profile_id)\
        .all()

    if feeds is None:
        return None, "Error: No discovery feeds for user found"

    return feeds, None


def get_feed_items(feed_id, session=None, page=1, limit=10,
                   before_id=None, after_id=None, sort_by="personalization",
                   query_builder=None):
    """ Get a list of media items in a discovery feed.
    """

    # Set the default query builder if not provided
    if query_builder is None:
        query_builder = get_feed_items_query_builder

    # Create a new session if not provided
    if session is None:
        engine,session_factory = local_session()
        session = session_factory()

    # Set the limit to 10 if not provided
    if limit is None:
        limit = 10
    
    # Set the limit to 50 if it is greater than 50
    if limit > 50:
        limit = 50
    
    # Get the feed
    feed = session.query(MediaFeed)\
            .filter(MediaFeed.id == feed_id)\
            .first()
    
    # Return an error if the feed is not found
    if feed is None:
        return None,f"Error, feed: {feed_id} not found"
    
    # Build the query
    query = query_builder(feed, feed_id, session=session, page=page, limit=limit,
                   before_id=before_id, after_id=after_id, sort_by=sort_by)
   
    # Execute the query
    try:
        results = query.all()
    except Exception as e:
        return None, f"Error: {e}"
    

    return results, None

def get_feed_items_query_builder(feed, feed_id, session=None, page=1, limit=10,
                   before_id=None, after_id=None, sort_by="personalization"):
    """ Create the query to get a list of media items in a discovery feed."""
    if before_id is not None:
        query = session.query(MediaItem, MediaItemPersonalization).join(
            MediaFeedItem, MediaItem.id == MediaFeedItem.id_media_item
        ).join(
            MediaItemPersonalization, MediaItem.id == MediaItemPersonalization.id_media_item
        ).filter(
            MediaFeedItem.id_media_feed == feed_id,
            MediaItemPersonalization.id_profile == feed.id_profile,
            MediaItemPersonalization.id < before_id
        ).order_by(
            MediaItemPersonalization.id.desc()
        ).limit(limit)
    elif after_id is not None:
        query = session.query(MediaItem, MediaItemPersonalization).join(
            MediaFeedItem, MediaItem.id == MediaFeedItem.id_media_item
        ).join(
            MediaItemPersonalization, MediaItem.id == MediaItemPersonalization.id_media_item
        ).filter(
            MediaFeedItem.id_media_feed == feed_id,
            MediaItemPersonalization.id_profile == feed.id_profile,
            MediaItemPersonalization.id > after_id
        ).order_by(
            MediaItemPersonalization.id.asc()
        ).limit(limit)
    else:

        # Calculate the offset based on the page and limit
        offset = (page - 1) * limit
        
        # Query to get all media items and personalizations in a specific feed for a given profile
        query = session.query(MediaItem, MediaItemPersonalization).join(
            MediaFeedItem, MediaItem.id == MediaFeedItem.id_media_item
        ).join(
            MediaItemPersonalization, MediaItem.id == MediaItemPersonalization.id_media_item
        ).filter(
            MediaFeedItem.id_media_feed == feed_id,
            MediaItemPersonalization.id_profile == feed.id_profile
        ).order_by(
            MediaItemPersonalization.id.desc()
        ).offset(offset).limit(limit)
    
    return query

def convert_feed_items_to_json(feed_items):
    """ Convert a list of feed items to JSON format."""
    response = {}
    items_json = []
    for media_item, personalization in feed_items:
        item_json = media_item.to_dict()
        item_json["personalization"] = personalization.to_dict()

        #TODO: consider strategies for sender logic
        #if there's an item from not SYM what would it be, how do we maintain this in a 'mixed' feed
        item_json["sender"] = get_sym_sender(date_sent=personalization.created_on)

        #TODO: TAGS need to be added to the media item
        #item_json["tags"] = media_item.tags
        item_json["tags"] = ["tag1", "tag2", "tag3"]

        items_json.append(item_json)
    return {"items": items_json}

def topics_discovery(topics, session=None, topic_limit=None):
    """ Given multiple topics, return any relevant items"""

    item_set = set()
    items = []
    for topic in topics:
        for item in topic_discovery(topic, session=session, limit=topic_limit):

            #deduplicate
            if item.id not in item_set:
                item_set.add(item.id)
                items.append(item)
    return items

def topic_discovery(topic, session=None, limit=None, max_embedding_distance=1.0):
    """ Given a topic return items which are similar"""

    #get a topic embedding
    t = get_or_embed_topic(topic, session=session)

    if limit is None:
        limit = 10

    items = session.scalars(select(MediaItem)\
                            .join(MediaItemTag, MediaItemTag.id_media_item == MediaItem.id)\
                            .join(MediaTag, MediaTag.id == MediaItemTag.id_media_tag)\
                            .filter(MediaTag.openai_tag_embedding.l2_distance(t.openai_topic_embedding) < max_embedding_distance)\
                            .order_by(MediaTag.openai_tag_embedding.l2_distance(t.openai_topic_embedding))\
                            .limit(limit))
    
    #todo distances
    # distances = session.scalars(select(MediaItem)\
    #                         .join(MediaItemTag, MediaItemTag.id_media_item == MediaItem.id)\
    #                         .join(MediaTag, MediaTag.id == MediaItemTag.id_media_tag)\
    #                         .filter(MediaTag.openai_tag_embedding.l2_distance(t.openai_topic_embedding) < 5)\
    #                         .order_by(MediaTag.openai_tag_embedding.l2_distance(t.openai_topic_embedding))\
    #                         .limit(limit))
    
    return items


def get_or_embed_topic(topic, session=None):
    topic = topic.lower().strip()
    t = session.query(MediaTopic)\
        .filter(MediaTopic.topic == topic)\
        .first()
    if t is None:
        t = MediaTopic()
        t.topic = topic
        topic_embed,response = get_openai_embedding(topic)
        t.openai_topic_embedding = topic_embed
        session.add(t)
        session.commit()
    return t

def get_or_create_media_feed_topic(feed_id, topic_id, session=None):
    mft = session.query(MediaFeedTopic)\
        .filter(MediaFeedTopic.id_media_feed == feed_id)\
        .filter(MediaFeedTopic.id_media_topic == topic_id)\
        .first()
    if mft is None:
        mft = MediaFeedTopic()
        mft.id_media_feed = feed_id
        mft.id_media_topic = topic_id
        session.add(mft)
        session.commit()
    return mft

def delete_media_feed_topic(media_feed_topic_id, session=None):
    mft = session.query(MediaFeedTopic)\
        .filter(MediaFeedTopic.id == media_feed_topic_id)\
        .first()
    print("deleting", mft, media_feed_topic_id)
    if mft is not None:
        session.delete(mft)
        session.commit()
    return True

def create_or_update_discovery_feed(
        feed_id=None,
        profile_id=None, 
        session=None, 
        topics=None,
        name=None,
        description=None):
    """ Create a new discovery feed based on the topics provided"""
    
    feed = None
    if feed_id is not None:
        feed = session.query(MediaFeed)\
            .filter(MediaFeed.id == feed_id)\
            .first()
        if feed is None:
            return None,f"Error, feed: {feed_id} not found"
    else:
        feed = MediaFeed()
    
    feed.id_profile = profile_id
    feed.name = name
    feed.description = description

    if feed_id is None:
        session.add(feed)
    
    session.commit()

    topic_check = {} 
    topic_id2feedtopic = {x.id_media_topic:x for x in feed.topics }

    #add topics and connect to feed
    if topics is not None:
        for topic in topics:
            #print(topic)
            t = get_or_embed_topic(topic, session=session)
            topic_check[t.id] = True #mark this item to maintain in feed topics
            if t.id not in topic_id2feedtopic:
                #add this topic via a new MediaFeedTopic record
                mft = get_or_create_media_feed_topic(feed.id, t.id, session=session)
    
    #now any topics missing are now pruned
    for mft_id in topic_id2feedtopic:
        mft = topic_id2feedtopic[mft_id]
        if mft.id_media_topic not in topic_check:
            delete_media_feed_topic(mft_id, session=session)
    return feed,None

def get_discovery_feed(feed_id, session=None):
    feed = session.query(MediaFeed)\
            .filter(MediaFeed.id == feed_id)\
            .first()
    if feed is None:
        return None,f"Error, feed: {feed_id} not found"
    return feed,None

def get_discovery_feed_items(
        feed_id, 
        session=None, 
        per_topic_limit=10, 
        max_embedding_distance=0.5, 
        page=1,
    ):
    
    #TODO: build feed async on schedule
    #TODO: show only new items in feed by recording previous interactions

    feed = session.query(MediaFeed)\
            .filter(MediaFeed.id == feed_id)\
            .first()
    if feed is None:
        return None,f"Error, feed: {feed_id} not found"
    
    id2item = {} #used to prevent duplicates
    all_items = []
    offset = (page-1)*per_topic_limit
    item2topics = {}

    for media_topic in feed.topics:
        t = media_topic.topic
       
        new_items = session.scalars(select(MediaItem)\
                                .join(MediaItemTag, MediaItemTag.id_media_item == MediaItem.id)\
                                .join(MediaTag, MediaTag.id == MediaItemTag.id_media_tag)\
                                .filter(MediaTag.openai_tag_embedding.l2_distance(t.openai_topic_embedding) < max_embedding_distance)\
                                .order_by(MediaTag.openai_tag_embedding.l2_distance(t.openai_topic_embedding))\
                                .offset(offset)\
                                .limit(per_topic_limit))
        
        for item in new_items:

            if item.id not in item2topics:
                item2topics[item.id] = [t.topic]
            else:
                item2topics[item.id].append(t.topic)

            if item.id not in id2item:
                id2item[item.id] = item
    
    for i in id2item:
        item = id2item[i]
        all_items.append(item)

    random.shuffle(all_items)

    #add topics to items for reference
    items_json = []
    for item in all_items:
        topics = list(set(item2topics[item.id]))
        item_j = item.to_dict()
        item_j["topics"] = topics
        items_json.append(item_j)

    return items_json, None

def get_personalized_feed_items(
        feed_id, 
        id_profile=None,
        session=None, 
        per_topic_limit=10, 
        max_embedding_distance=0.5, 
        page=1,
    ):

    print(f"get_personalized_feed_items: {feed_id} {id_profile}")

    feed = session.query(MediaFeed)\
            .filter(MediaFeed.id == feed_id)\
            .first()
    if feed is None:
        return None,f"Error, feed: {feed_id} not found"
    
    # Query to get all media items and personalizations in a specific feed for a given profile
    query = session.query(MediaItem, MediaItemPersonalization).join(
        MediaFeedItem, MediaItem.id == MediaFeedItem.id_media_item
    ).join(
        MediaItemPersonalization, MediaItem.id == MediaItemPersonalization.id_media_item
    ).filter(
        MediaFeedItem.id_media_feed == feed_id,
        MediaItemPersonalization.id_profile == feed.id_profile
    ).order_by(
        MediaItemPersonalization.created_on.desc()
    )

    # Execute the query
    results = query.all()

    # Processing the results
    items_json = []
    for media_item, personalization in results:
        #print("Media Item:", media_item.title, "Personalization:", personalization.text)
        j = media_item.to_dict()
        j["personalized_summary"] = personalization.text
        items_json.append(j)

    return items_json, None


def collect_feed_items(
        feed_id, 
        session=None, 
        per_topic_limit=100, 
        max_embedding_distance=0.5, 
        page=1,
    ):
    
    # build feed async on schedule

    feed = session.query(MediaFeed)\
            .filter(MediaFeed.id == feed_id)\
            .first()
    if feed is None:
        return None,f"Error, feed: {feed_id} not found"
    
    id2item = {} #used to prevent duplicates
    all_items = []
    offset = (page-1)*per_topic_limit
    item2topics = {}

    for media_topic in feed.topics:
        t = media_topic.topic

        # Subquery to find MediaItem IDs already in the MediaFeed
        subquery = select(MediaFeedItem.id_media_item).filter(MediaFeedItem.id_media_feed == feed.id).subquery()

        new_items = session.scalars(select(MediaItem)\
                                .join(MediaItemTag, MediaItemTag.id_media_item == MediaItem.id)\
                                .join(MediaTag, MediaTag.id == MediaItemTag.id_media_tag)\
                                .outerjoin(subquery, MediaItem.id == subquery.c.id_media_item)
                                .filter(subquery.c.id_media_item == None)\
                                .filter(MediaTag.openai_tag_embedding.l2_distance(t.openai_topic_embedding) < max_embedding_distance)\
                                .order_by(MediaTag.openai_tag_embedding.l2_distance(t.openai_topic_embedding))\
                                .limit(per_topic_limit))
        
        for item in new_items:
            if item.id not in id2item:
                id2item[item.id] = item
    
    new_feed_items = []
    for i in id2item:
        item = id2item[i]
        
        #create a new media feed item
        mfi = MediaFeedItem()
        mfi.id_media_feed = feed.id
        mfi.id_media_item = item.id
        session.add(mfi)
        new_feed_items.append(mfi)
    session.commit()


    return new_feed_items, None

async def chat_with_media_item(prompt="Summarize anything relevant in this article", item_id=None, session=None, id_profile=None, messages=None):
    #given a prompt and item id, chat with this media item

    if session is None:
        engine,session_factory = local_session()
        session = session_factory()
    
    media_item = session.query(MediaItem)\
        .filter(MediaItem.id == item_id)\
        .first()
    if not media_item:
        return {},"Error: Media item not found"

    #get title, summary, url
    title = media_item.title
    summary = media_item.summary
    url = media_item.source_url


    #relevant context
    profile_datums = get_relevant_profile_datums(
        title+" "+summary, id_profile=None, limit=10, session=None
    )
    relevant_context_str = ""
    for d in profile_datums:
        relevant_context_str += f"-{d.key}: {d.value}\n"

    #construct prompt
    prompt = f"""
        Given this media item: 
        title: {title} 
        summary: {summary}

        Answer this question:
        {prompt}

        Here is some potentially relevant context for the person asking:
        {relevant_context_str}
    """

    #system prompt
    system = f"""You are an expert at news analysis and comprehension"""

    text, response = prompt_openai(prompt=prompt, system=system, messages=messages)

    #TODO: save the result for later reference
    #.... save_prompt_record, store prompt / response reference
    


    return text

async def summarize_url(profile_id=None, session=None, url=None):
    """ Summarize a web url for this individual"""

    #TODO
    #add a personalized profile specific summary

    pass

async def personalize_media_item(profile_id=None, session=None, id_media_item=None):
    """
    
    """

    pass