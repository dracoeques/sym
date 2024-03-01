import openai
import os

def run_openai_prompt(
        message, 
        system=None, 
        prev_messages=None,
        model="gpt-4",
        temperature=1.0,
        ):
    
    #set org key / API key
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.organization = os.environ.get("OPENAI_ORG_KEY")

    #add any previous messages
    messages = []
    if prev_messages:
        messages = prev_messages

    #add our system message
    if system:
        messages.append({"role":"system", "content":system})

    #add our message
    messages.append({"role":"user", "content":message})

    #return the result
    
    completion = openai.ChatCompletion.create(
        messages=messages,
        model=model,
        temperature=temperature,
    )

    return completion.choices[0].message["content"], completion

