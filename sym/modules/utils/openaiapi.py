import os
from openai import OpenAI
import openai
from openai import AsyncOpenAI


from sym.modules.db.db import *
from sym.modules.db.models import *
from sqlalchemy.orm.attributes import flag_modified

from sym.modules.utils.utils import upload_image_to_s3

def resolve_client(client=None, api_key=None, org_key=None):
    """ Helper function, will initiate a client if none is provided"""
    if client is None and api_key is None:
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            organization=os.environ.get("OPENAI_ORG_KEY"),
        )
    elif client is None and api_key is not None:
        client = OpenAI(
            api_key=api_key,
            organization=org_key,
        )
    return client


def get_available_models(client=None, api_key=None):
    """ Given a client or api key, return a list of strings of all available models"""
    if client is None and api_key is None:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.organization = os.environ.get("OPENAI_ORG_KEY")
        client = OpenAI()
    elif client is None and api_key is not None:
        client = OpenAI(
            api_key=api_key,
        )

    models = client.models.list()
    model_list = []
    for m in models:
        model_list.append(m.id)
    return model_list
    

def get_openai_embedding(text, model="text-embedding-ada-002"):
    """ Given text, return an openai text embedding and the respons
    
        Parameters:
            text (string) : the text to be embedded
            model (string) : the openai model to use for embedding

        Returns:
            vector (list[float]) : the embedded text
            response (dict) : the entire response from openai
        
        Requires two environment variables to be set
            OPENAI_API_KEY : the api key for openai
            OPENAI_ORG_KEY : the organization key to use with openai

     """
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.organization = os.environ.get("OPENAI_ORG_KEY")

    response = openai.embeddings.create(
        input=[text],
        model=model,
    )
    embeddings = response.data[0].embedding
    return embeddings, response


async def prompt_openai_async(
        prompt=None,
        system=None,
        messages=None,
        model="gpt-4",
        max_context_length=4097,
        temperature=0.5,
        session=None,
        save_prompt_record=False,
        id_profile=None,
    ):

    client = AsyncOpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
        organization=os.environ.get("OPENAI_ORG_KEY"),
    )
    if prompt is None and messages is None:
        raise Exception("Prompt or previous messages must be provided")

    if messages is None:
        messages = []
    
    if system:
        messages.append(
            {"role":"system", "content":system}
        )
    
    if prompt:
        if len(prompt) > max_context_length:
            prompt = prompt[0:max_context_length]
        messages.append(
            {"role":"user", "content":prompt}
        )
    
    #truncate messages if content length is exceeded
    messages = truncate_messages(messages, max_context_length=max_context_length)
    
    #call open ai api - non streaming prompt
    response = await client.chat.completions.create(
        model=model,
        temperature=temperature, 
        messages=messages,
        stream=False,
    )
   
    
    response_text = response.choices[0].message.content

    if save_prompt_record:
        #default logic is to save A record of every prompt 
        if session is None:
            eng,factory = local_session()
            session = factory()
        
        p = Prompt()
        p.rawtext = prompt
        p.system = system
        p.id_profile = id_profile

        p.input_payload = {
            "messages":messages,
            #... additional params here eg: temp, top_k
        }

        p.output_payload = {
            "response_text":response_text,
            "payload":response,
        }

        session.add(p)
        session.commit()


    return response_text,response

def prompt_openai(
        prompt=None,
        system=None,
        messages=None,
        model="gpt-4",
        max_context_length=4097,
        temperature=0.5,
        session=None,
        save_prompt_record=False,
        id_profile=None,
    ):
    """ Query openaiapi """

    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.organization = os.environ.get("OPENAI_ORG_KEY")

    if prompt is None and messages is None:
        raise Exception("Prompt or previous messages must be provided")

    if messages is None:
        messages = []
    
    if system:
        messages.append(
            {"role":"system", "content":system}
        )
    
    if prompt:
        if len(prompt) > max_context_length:
            prompt = prompt[0:max_context_length]
        messages.append(
            {"role":"user", "content":prompt}
        )
    
    #truncate messages if content length is exceeded
    messages = truncate_messages(messages, max_context_length=max_context_length)
    
    #call open ai api - non streaming prompt
    response = openai.chat.completions.create(
                    model=model,
                    temperature=temperature, 
                    messages=messages,
                    stream=False)
    
    response_text = response.choices[0].message.content

    if save_prompt_record:
        #default logic is to save A record of every prompt 
        if session is None:
            eng,factory = local_session()
            session = factory()
        
        p = Prompt()
        p.rawtext = prompt
        p.system = system
        p.id_profile = id_profile

        p.input_payload = {
            "messages":messages,
            #... additional params here eg: temp, top_k
        }

        p.output_payload = {
            "response_text":response_text,
            "payload":response,
        }

        session.add(p)
        session.commit()


    return response_text,response


def truncate_messages(messages, max_context_length=4097, allow_partial_messages=True):
    """
    Truncate the list of messages to the last n messages with a total length not exceeding max_context_length.

    Parameters:
    - messages (list of str): List of messages to be truncated.
    - max_context_length (int, optional): Maximum combined length of messages. Defaults to 4097.

    Returns:
    - list of str: Truncated list of messages.
    """
    
    truncated_messages = []
    total_length = 0

    #remove duplicate system prompts
    deduped_system = []
    system_prompts = set()
    for m in reversed(messages):
        if m["role"] == "system":
            if m["content"] not in system_prompts:
                system_prompts.add(m["content"])
                deduped_system.append(m)
        else:
            deduped_system.append(m)
    deduped_system = list(reversed(deduped_system))

    # Loop through the messages in reverse to keep only the latest messages under the content length
    for m in reversed(deduped_system):
        message = m["content"]
        if total_length + len(message) > max_context_length:

            #optionally allow partial message if message length is too long
            if allow_partial_messages:
                diff = total_length + len(message) - max_context_length
                if diff > 0:
                    m["content"] = m["content"][:diff]
                    truncated_messages.append(m)
            break
        total_length += len(message)
        truncated_messages.append(m)

    return list(reversed(truncated_messages))


def create_dalle_image(
        model="dall-e-3", 
        prompt="a white siamese cat",
        size="1024x1024",
        quality="standard",
    ):
    
    
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.organization = os.environ.get("OPENAI_ORG_KEY")
    client = OpenAI()
    
    image_url = None
    try:
        response = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=1,
        )

        image_url = response.data[0].url
    except Exception as e:
        print(f"Error generating image: {e}")
    
    s3_url = None
    if image_url is not None:
        #print(image_url)
        s3_url = upload_image_to_s3(image_url)
    
    return s3_url