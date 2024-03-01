import re


from sym.modules.db.db import *
from sym.modules.db.models import *

from sqlalchemy.orm.attributes import flag_modified

from sym.modules.promptflows.prompt_flow_runner import PromptFlowRunner

import openai


def main():

    # instantiate session
    #TODO
    eng,factory = local_session()
    session = factory()

    items = extract_qa_values(session)

    for item in items:
        #TODO: create a logical ordering 
        #of question -> response
        #Q: how do I check this in the flow (via display)
        #And if there are multiple questions asked do we just concat?
        pass

def get_run_qa(session, prompt_run_id=None):

    #get each run_item in order of run, 
    #remake the values like openai messages

    # items = session.query(PromptRunItem)\
    #     .filter(PromptRunItem.id_prompt_run = prompt_run_id)\
    #     .order_by(PromptRunItem.id)\
    #     .all()
    #.order_by(PromptRunItem.created_on)\
    
    # denote user response vs previous message
    #collect into Q/A pairs

    pfr = PromptFlowRunner()
    persistence = PromptFlowPersistenceDB()
    persistence.session = session
    pfr.persistence = persistence

    #TODO: simple items on prompt_run_items to make it easier
    #node_type: 
    #message: actual text sent
    #action: (display, silent, etc.)
    #sender: user / bot

    pass

        
        



def extract_qa_values(session,
        flow_id=None,
        limit=None

    ):
    """
        Extract any question answer pairs 
        for this profile which haven't been processed into profile datums

        
    """

    # query items which haven't been processed
    items_to_process_q = session.query(PromptRunItem)\
        .join(PromptRun, PromptRunItem.id_prompt_run == PromptRun.id)\
        .outerjoin(ProfileDatum, ProfileDatum.id_run_item == PromptRunItem.id)\
        .filter(PromptRun.id_prompt_flow == flow_id)\
        .filter(PromptRunItem.id_profile != None)\
        .filter(ProfileDatum.kind == 'question-answer')\
        .filter(ProfileDatum.id == None)
        
    
    if limit is None:
        items_to_process = items_to_process_q.all()
    else:
        items_to_process = items_to_process_q.limit(limit)
    
    return items_to_process

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
            continue
        if item.id_profile is None:
            continue

        print(text)

        print(item.id, item.id_profile)
        
        #now we create N profile datums 
        for kv in kvs:
            
            k, v = kv

            print(k, v)

            #check for an existing datum, if exists skip
            #NOTE: this will ignore the same data provided from a different node
            p = session.query(ProfileDatum)\
                .filter(ProfileDatum.key == k)\
                .filter(ProfileDatum.value == v)\
                .filter(ProfileDatum.id_profile == item.id_profile)\
                .filter(ProfileDatum.kind == 'question-answer')\
                .first()
            if p is not None:
                continue
            
            p = ProfileDatum()
            p.category = category
            p.key = k
            p.value = v
            p.id_profile = item.id_profile
            p.id_run_item = item.id

            #get embeddings
            if k in cached_embeddings:
                k_embed = cached_embeddings[k]
            else:
                k_embed = get_openai_embedding(k)
                cached_embeddings[k] = k_embed
            
            if v in cached_embeddings:
                v_embed = cached_embeddings[v]
            else:
                v_embed = get_openai_embedding(v)
                cached_embeddings[v] = v_embed
            
            if cat_embed is None:
                if category in cached_embeddings:
                    cat_embed = cached_embeddings[category]
                else:
                    cat_embed = get_openai_embedding(category)
            
            #set embeddings
            p.openai_category_embedding = cat_embed
            p.openai_key_embedding = k_embed
            p.openai_value_embedding = v_embed
            
            #add this to our session
            session.add(p)
        
    
    #save our new profile datums
    session.commit()

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

def get_openai_embedding(text):
    """ Given text, return an openai text embedding """
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.organization = os.environ.get("OPENAI_ORG_KEY")

    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    embeddings = response['data'][0]['embedding']
    return embeddings

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
    main()