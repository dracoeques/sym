import re


from sym.modules.db.db import *
from sym.modules.db.models import *

from sqlalchemy.orm.attributes import flag_modified

from sym.modules.utils.openaiapi import get_openai_embedding



async def run_kv_etl_async(id_profile=None):

    # instantiate session
    #TODO
    eng,factory = local_session()
    session = factory()

    #print("Extracting KV")

    personality_nodes = {
        1094:"values", #part of prompt_flow 162 - value insight extractor
        1100:"interests", #prompt_flow 163 - Interests insight extractor
        1107:"personality", #prompt_flow 164 - Personality insights
        1470:"opportunity", #prompt_flow 202 - opportunity discovery extractor
        1473:"personality", #196
        1472:"interests", #200
        1471:"values", #201 

    }

    total_new_kvs = 0

    for node_id, category in personality_nodes.items():
        
        items = extract_key_values(session, node_id=node_id, category=category, id_profile=id_profile)
        
        print(node_id, category, len(items))
        cached_embeddings = get_cached_embeddings(session, limit=1000)
        kvs = transform_load_key_values(session, items, category=category, cached_embeddings=cached_embeddings)

        total_new_kvs += len(kvs)
    #print("Extracting KV Completed")
    return total_new_kvs

def main(id_profile=None):

    # instantiate session
    #TODO
    eng,factory = local_session()
    session = factory()

    #print("Extracting KV")

    personality_nodes = {
        1094:"values", #part of prompt_flow 162 - value insight extractor
        1100:"interests", #prompt_flow 163 - Interests insight extractor
        1107:"personality", #prompt_flow 164 - Personality insights
        1470:"opportunity", #prompt_flow 202 - opportunity discovery extractor
        1473:"personality", #196
        1472:"interests", #200
        1471:"values", #201 

    }

    for node_id, category in personality_nodes.items():
        
        items = extract_key_values(session, node_id=node_id, category=category, id_profile=id_profile)
        
        print(node_id, category, len(items))
        cached_embeddings = get_cached_embeddings(session, limit=1000)
        kvs = transform_load_key_values(session, items, category=category, cached_embeddings=cached_embeddings)

    #print("Extracting KV Completed")


#TODO: extract key values directly from prompt flows without needing the specific prompt nodes

def extract_key_values(session,
        node_id=1094,
        category=None,
        limit=None,
        id_profile=None,
    ):
    """
        Given a node_id and a category
        Extract key value pairs for this profile which haven't been processed
        
    """

    #query items which haven't been processed
    items_to_process = session.query(PromptRunItem)\
        .outerjoin(ProfileDatum, ProfileDatum.id_run_item == PromptRunItem.id)\
        .filter(PromptRunItem.id_node == node_id)\
        .filter(ProfileDatum.id == None)

    if id_profile == None:
        items_to_process.filter(PromptRunItem.id_profile != None)
    else:
        items_to_process.filter(PromptRunItem.id_profile == id_profile)
    
    if limit is not None:
        items_to_process = items_to_process.limit(limit)
    
    return items_to_process.all()

def get_cached_embeddings(session, limit=1000):
    embeddings = {}

    cached_datums = session.query(ProfileDatum)\
        .limit(limit).all()

    for d in cached_datums:
        embeddings[d.category] = d.openai_category_embedding
        embeddings[d.key] = d.openai_key_embedding
        embeddings[d.value] = d.openai_value_embedding
    
    return embeddings

def transform_load_key_values(session, items, category=None, cached_embeddings=None):
    """ 
        Transform & load run_items into category / key / value pairs
        Vectorize the items 
    """

    new_kvs = []

    #cached embeddings reduce redundant api calls
    if cached_embeddings is None:
        cached_embeddings = {}

    cat_embed = None
    if category in cached_embeddings:
        cat_embed = cached_embeddings[category]

    for item in items:
        #get their output_payload data and parse responses into tuples of key / values
        text = item.output_payload["message"]
        
        #search for snippets of text that follow pattern
        #- Key : Value
        tups = parse_kv_text(text)
        kvs = []
        for tup in tups:
            t = (tup[0].strip(), tup[1].strip())
            kvs.append(t)

        if len(kvs) == 0:
            #print("skipping, no kvs")
            continue
        if item.id_profile is None:
            #print("skipping, no profile id")
            continue

        #print(text)

        print(item.id, item.id_profile)
        
        #now we create N profile datums 
        for kv in kvs:
            
            k, v = kv

            #print(k, v)

            #check for an existing datum, if exists skip
            #NOTE: this will ignore the same data provided from a different node
            p = session.query(ProfileDatum)\
                .filter(ProfileDatum.key == k)\
                .filter(ProfileDatum.value == v)\
                .filter(ProfileDatum.id_profile == item.id_profile)\
                .filter(ProfileDatum.kind == "key-value")\
                .first()
            if p is not None:
                print(k,v, p.id)
                continue
            
            p = ProfileDatum()
            p.category = category
            p.key = k
            p.value = v
            p.kind = "key-value"
            p.id_profile = item.id_profile
            p.id_run_item = item.id

            #get embeddings
            if k in cached_embeddings:
                k_embed = cached_embeddings[k]
            else:
                k_embed,r = get_openai_embedding(k)
                cached_embeddings[k] = k_embed
            
            if v in cached_embeddings:
                v_embed = cached_embeddings[v]
            else:
                v_embed,r = get_openai_embedding(v)
                cached_embeddings[v] = v_embed
            
            if cat_embed is None:
                if category in cached_embeddings:
                    cat_embed = cached_embeddings[category]
                else:
                    cat_embed,r = get_openai_embedding(category)
            
            #set embeddings
            p.openai_category_embedding = cat_embed
            p.openai_key_embedding = k_embed
            p.openai_value_embedding = v_embed
            
            #add this to our session
            session.add(p)
            new_kvs.append(p)
        
    
    #save our new profile datums
    session.commit()
    return new_kvs

def parse_ckv_text(text):
    """ Pattern to match '-Category Key: Value' in the given text."""
    pattern = re.compile(r'^- (\w+): ([^:]+): (.+)$', re.MULTILINE)
    matches = pattern.findall(text)

    for match in matches:
        category, key, value = match
        print(f"Category: {category}, Key: {key}, Value: {value}")
    

def parse_kv_text(text):
    # Pattern to match '-Key: Value' in the given text.
     # Pattern to match '-Key: Value' in the given text with multiline-awareness.
    pattern = r'-([\w\s]+):\s*([\w\s]+?(?=-[\w\s]+:|\Z))'
    
    # Using re.findall() to get all matches.
    matches = re.findall(pattern, text, re.DOTALL)
    
    # Stripping any extraneous whitespace from the matches
    matches = [(k.strip(), v.strip()) for k, v in matches]
    return matches



def load_key_values(items):
    """ 
    """
    pass

def prompt_key_values(text):
    prompt = """Given piece of text find any relevant key-value pairs which are interesting facts about an individual, output only the key value pairs denoted with the `-` character for each pair. 

            For example: 

            Input:
            "I am a 40 year male who likes to bike ride with my family in Zurich on the weekends. "

            Output:
            - Age: 40
            - Sex: Male
            - Hobbies: Bike riding with family"""
    
    #TODO: prompt LLM to produce key value pairs in markdown format
    #then parse them into a list of tuples

if __name__ == "__main__":
    #parse_kv_text("- Person admired: Nikola Tesla\n- Reason: Brilliant scientist and inventor")
    #parse_ckv_text("- Values: Person admired: Nikola Tesla\n- Values: Reason: Brilliant scientist and inventor")
    #_ = await main()
    main(id_profile=8)