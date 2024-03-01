
from sym.modules.db.models import *
from sym.modules.db.db import local_session
from sym.modules.discovery.core import collect_feed_items

from sym.modules.personalization.relevant_context import get_relevant_profile_datums
from sym.modules.utils.openaiapi import prompt_openai

def media_item_opportunity(
        session=None, 
        id_profile=None, 
        id_media_item=None, 
        model="gpt-4-turbo-preview"):
    """ Given a profile and a media item, 
        generate a summary of why this would be relevant for them"""
    
    if session is None:
        engine,session_factory = local_session()
        session = session_factory()
    
    media_item = session.query(MediaItem)\
        .filter(MediaItem.id == id_media_item)\
        .first()
    if not media_item:
        return {},"Error: Media item not found"

    #get title, summary, url
    title = media_item.title
    summary = media_item.summary
    url = media_item.source_url
    body_text = media_item.body_text

    profile = session.query(Profile)\
        .filter(Profile.id == id_profile)\
        .first()
    seed_text = ""
    if profile.seed_text:
        seed_text = profile.seed_text
    

    #relevant context
    profile_datums,t = get_relevant_profile_datums(
        title+" "+summary, id_profile=id_profile, limit=10, session=session
    )
    relevant_context_str = ""
    for d in profile_datums:
        relevant_context_str += f"-{d.key}: {d.value}\n"

    #construct prompt
    prompt = f"""
        Write 3 bullet points on the top connections to opportunities or challenges that this article could help solve for the individual. Make each bullet point one sentence, and it can be a longer sentence. Align the connections and recommendations with the specific values, challenges, and opportunities of the individual. Choose the value to align with by selecting the value most relevant to the point in the article. No preamble, just 3 bullet points about why this information is relevant and how it can help the individual realize their toward and away from values and goals. Write the bullet points in second-person singular, candid professional tone. Use the words “you” and “your” to address them and align the article content with them conversationally.

        Here is some potentially relevant context for the person asking:
        {seed_text}

        {relevant_context_str}
        
        Here is the article: 
        title: {title} 
        summary: {summary}
        body text of article: {body_text}
        
       

    """

    #print(prompt)

    #system prompt
    system = f"""You are an expert at news analysis and comprehension and understanding why specific content is useful for an individual"""

    text, response = prompt_openai(prompt=prompt, system=system, model=model)

    #TODO: save the result for later reference
    #.... save_prompt_record, store prompt / response reference
    print("profile_id", id_profile,  "title", title, "personalization", text)


    return text


