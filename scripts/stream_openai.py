import openai
import os
import asyncio, threading

from sym.modules.utils.openaiapi import truncate_messages



def async_wrap_iter(it):
    """Wrap blocking iterator into an asynchronous one
    
        see: https://stackoverflow.com/questions/62294385/synchronous-generator-in-asyncio
    """
    loop = asyncio.get_event_loop()
    q = asyncio.Queue(1)
    exception = None
    _END = object()

    async def yield_queue_items():
        while True:
            next_item = await q.get()
            if next_item is _END:
                break
            yield next_item
        if exception is not None:
            # the iterator has raised, propagate the exception
            raise exception

    def iter_to_queue():
        nonlocal exception
        try:
            for item in it:
                # This runs outside the event loop thread, so we
                # must use thread-safe API to talk to the queue.
                asyncio.run_coroutine_threadsafe(q.put(item), loop).result()
        except Exception as e:
            exception = e
        finally:
            asyncio.run_coroutine_threadsafe(q.put(_END), loop).result()

    threading.Thread(target=iter_to_queue).start()
    return yield_queue_items()


async def stream_openai_prompt(
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
                    stream=True)
    
    response_text = ""
    async for resp in async_wrap_iter(response):
        #responses.append(resp)
        #print(resp.choices[0].delta.content)
        chunk = resp.choices[0].delta.content
        if chunk:
            response_text += chunk
            yield chunk

    #response_text = response.choices[0].message.content


async def main():

    async for msg in stream_openai_prompt(
        prompt="Create an itinerary for 5 places to visit in Italy for wine tasting",
        system=None,
        messages=None,
        model="gpt-4",
        max_context_length=4097,
        temperature=0.5,
        session=None,
        save_prompt_record=False,
        id_profile=None,
            ):
        print(msg)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())