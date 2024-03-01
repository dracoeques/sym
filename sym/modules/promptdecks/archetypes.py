from collections import defaultdict
import logging

from sym.modules.db.models import PromptDeck



def read_archetype_categories(
        session,
    ):
    #get's all archetype prompt type categories
    decks = session.query(PromptDeck)\
        .filter(PromptDeck.is_archetype == True)\
        .all()
    
    data = {}
    for deck in decks:
        
        cat,sub = deck.category, deck.subcategory
        if cat not in data:
            data[cat] = {}
        if sub not in data[cat]:
            data[cat][sub] = deck.to_dict()
        else:
            #what to do, we have duplicate archetypes
            logging.error(f"Duplicate archetype decks found {cat} : {sub}")
    return data

def format_archetype_categories_flower(data):

    topics = []
    for category in data:

        if category is None:
            continue

        topic = {
            "name":category,
            "children":[],
        }
        subtopics = []
        for subcategory in data[category]:
            deck = data[category][subcategory]

            if subcategory is None:
                continue
            url = f"/app/prompt-deck/{deck['id']}"
            
            sub = {
                "name":subcategory,
                "url":url,
            }
            subtopics.append(sub)
        topic["children"] = subtopics
        topics.append(topic)
    return topics
    
def format_archetype_categories_d3(data, default_value=10):
    """ Format our dictionary into the expected format
        for the d3 frontend
    """
    d = {
        "name":"topics",
        "children":[],
    }
    topics = []
    for category in data:

        if category is None:
            continue

        topic = {
            "name":category,
            "children":[],
        }
        subtopics = []
        for subcategory in data[category]:
            deck = data[category][subcategory]

            if subcategory is None:
                continue
            url = f"/app/prompt-deck/{deck['id']}"
            default_url = "/app/prompt-deck-archetype"
            sub = {
                "name":subcategory,
                "url":default_url,
                "children":[
                    {
                        "name":subcategory,
                        "value":default_value,
                    }
                ],
            }
            subtopics.append(sub)
        topic["children"] = subtopics
        topics.append(topic)
    d["children"] = topics
    return d