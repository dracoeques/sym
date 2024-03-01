
from sym.modules.db.db import *
from sym.modules.db.models import *

import openai

from sym.modules.utils.openaiapi import prompt_openai

def main(profile_id=8):
    eng,factory = local_session()
    session = factory()

    #given this persons values
    # provide a summary of what they value and why

    value_datums = session.query(ProfileDatum)\
        .filter(ProfileDatum.id_profile == profile_id)\
        .filter(ProfileDatum.category == 'values')\
        .all()
    
    values = []
    for d in value_datums:
        values.append((d.key, d.value))
    
    t = summarize_values_prompt(values)
    print(t)




def summarize_values_prompt(values):
    
    value_string = """"""
    for tup in values:
        k,v = tup
        value_string += f"-{k}: {v}\n"
    
    prompt = f"""given this persons values provide a summary of what they value and why
        VALUES:
        {value_string}
    """

    max_context_length = 4097
    if len(prompt) > max_context_length:
        prompt = prompt[:max_context_length]
        #TODO: summarize values iteratively in chunks when context is exceeded

    #print(prompt)
        
    response_text, r = prompt_openai(prompt=prompt)

    return response_text


if __name__ == "__main__":
    main()