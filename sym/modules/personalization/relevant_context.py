
from sym.modules.db.db import *
from sym.modules.db.models import *

from sym.modules.utils.openaiapi import get_openai_embedding, prompt_openai

from sqlalchemy import select

from sym.modules.personalization.kv_etl import parse_kv_text

def relevant_profile_context_v1(context_string,
            evaluator_model="gpt-4",
            context_model="gpt-4",
            id_profile=None, 
            limit=10, 
            session=None):
    """ Get relevant Key-Value pairs from a given context for this profile 
        Given a context_string perform a vector search to retrieve similar items
        Use an evaluator agent to filter the items
        Store the results from the evaluator for later use

    """

    if id_profile is None:
        raise Exception("id_profile cannot be None")

    #get relevant kv topics via semantic similarity search
    datums,t = get_relevant_profile_datums(context_string, id_profile=id_profile, limit=limit, session=session)

    #use evaluator
    evaluator_datums,r1 = relevant_datums_evaluator(context_string, datums, model=evaluator_model)

    #save results to ProfileDatumContextResponse for later use
    eval_ids = set([d.id for d in evaluator_datums])

    #Save a reference to this for later use
    for d in datums:
        
        liked = False
        if d.id in eval_ids:
            liked = True

        pdr = ProfileDatumContextResponse()
        pdr.model = evaluator_model
        pdr.id_text = t.id
        pdr.id_profile_datum = d.id
        pdr.liked = liked
        session.add(pdr)
    session.commit()

    #query and return a response
    relevant_context_str = ""
    for d in evaluator_datums:
        relevant_context_str += f"-{d.key}: {d.value}\n"
    context_prompt = context_string + f"""\n\nHere is some relevant context for this individual: \n{relevant_context_str}"""
    context_response,r2 = prompt_openai(
        prompt=context_prompt,
        system="""You are a helpful AI assistant""",
        model=context_model,
        session=session, 
        id_profile=id_profile
    )

    return evaluator_datums,t,context_response


def relevant_datums_evaluator(context_string, datums, model="gpt-4", session=None, id_profile=None):
    """ Given a context string and a list of data points
        Ask an LLM to evaluate which of these are data points are relevant
        for the context
    """
    
    value_string = """"""
    for d in datums:
        value_string += f"- {d.key}: {d.value}\n"
    
    prompt = f"""Context: {context_string}\n\nValues: {value_string}"""

    system = f"""You are an evaluator bot that when given a piece of context text and a list of key value pairs, only return the relevant key value pairs for this context 
    
    Example 1:

    Context: "What is this person's favorite food?"
    Values: -Favorite cuisine: French\n-Cuisine interest: Moroccan dishes\n-Person admired: Albert Einstein\n
    Response: -Favorite cuisine: French\n-Cuisine interest: Moroccan dishes\n


    Example 2:

    Context: "Who does this person like"
    Values: -Person admired: Albert Einstein\n-Person disliked:Elon Musk\n-Admired Person:Nikola Tesla\n
    Response: -Person admired: Albert Einstein\n-Admired Person:Nikola Tesla\n

    Example 3:

    Context: "Who does this person dislike"
    Values: -Person admired: Albert Einstein\n-Person disliked:Elon Musk\n-Admired Person:Nikola Tesla\n
    Response: -Person disliked:Elon Musk\n

    """

    text,r = prompt_openai(
        prompt=prompt,
        system=system,
        model=model,
        session=session,
        id_profile=id_profile,

    )

    #Parse output 
    values = set()
    items = []
    for kv in parse_kv_text(text):
        k,v = kv
        items.append({"key":k, "value":v}) 
        values.add(v)
    
    #match output with datums
    filtered_datums = []
    for d in datums:
        if d.value in values:
            filtered_datums.append(d)

    return filtered_datums,r

def get_relevant_profile_datums(context_string, id_profile=None, limit=10, session=None):
    if session is None:
        eng,factory = local_session()
        session = factory()
    t = get_or_embed_text(session, context_string)
    items = get_relevant_items(session, t.openai_embedding, limit=limit, id_profile=id_profile)
    datums = [x for x in items] #unpack into a list to prevent sqlalchemy error when iterating it loses the data
    return datums, t

def get_or_embed_text(session, context_string):
    """ Given a context string check for an existing 
        embedding, if it exists return that, otherwise
        create a new text embedding
    """
    #check for an existing text record
    t = session.query(Text)\
        .filter(Text.text == context_string)\
        .first()
    if t is None:
        t = Text()
        t.text = context_string
        e,r = get_openai_embedding(context_string)
        t.openai_embedding = e
        session.add(t)
        session.commit()
    return t


def get_relevant_items(session, context_vector, id_profile=None, limit=5):

    #TODO: order by most recent and the lowest distance

    #distinct values subquery
    subquery = session.query(ProfileDatum.id)\
        .filter(ProfileDatum.id_profile == id_profile)\
        .distinct(ProfileDatum.value)


    items = session.scalars(select(ProfileDatum)\
        .filter(ProfileDatum.id.in_(subquery))\
        .order_by(ProfileDatum.openai_key_embedding.l2_distance(context_vector))\
        .limit(limit))

    return items



def save_user_response_ranking(
        session, 
        id_text, 
        id_profile_datum, 
        id_profile_ranker,
        liked=True,
    ):

    r = ProfileDatumContextResponse()
    r.id_ranker = id_profile_ranker
    r.id_text = id_text
    r.id_profile_datum = id_profile_datum

    r.liked = liked

    session.add(r)
    session.commit()
    return r





if __name__ == "__main__":
    context = input("What do you want to know? eg: 'What kind of people does this person admire?' ")
    items, t = get_relevant_profile_datums(context)
    
    for i,item in enumerate(items):
        print(f"{i} {item.key}: {item.value}")
    