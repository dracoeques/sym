from dataclasses import dataclass, field
import openai

from typing import List

from sym.modules.misc.client_getting_secrets import client_getting_secrets

import asyncio, threading

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


@dataclass
class StartNode:

    id: str = None
    intro_text: str = None
    node_type: str = "start"
    finished: bool = False

    async def run(self, payload=None):
        yield self.intro_text, "continue"
        self.finished = True
    
    def to_dict(self):
        return {
            "id":self.id,
            "intro_text":self.intro_text,
            "finished":self.finished,
            "node_type":self.node_type,
        }
    
    def from_dict(self, payload):
        if "id" in payload:
            self.id = payload["id"]
        if "introText" in payload:
            self.intro_text = payload["introText"]
        return self

    async def get(self):
        return {}

@dataclass
class TextInputNode:
    id: str = None
    question: str = None
    hint: str = None
    text: str = None
    node_type: str = "text_input"
    finished: bool = False


    async def run(self, payload=None):
        print("TextInputNode", payload)
        try:
            self.question = self.question.format(**payload)
        except Exception as e:
            print(e)
            
        if self.text is None and self.finished is False:


            
            if self.hint:
                yield self.question, "continue"
                yield self.hint, "get_user_input"
            else:
                yield self.question, "get_user_input"
        else:
            #somehow we re-ran this node
            yield None,"continue"
    
    def set(self, text):
        self.text = text
    
    async def get(self):
        return {"text":self.text}

    def to_dict(self):
        return {
            "id":self.id,
            "question":self.question,
            "hint":self.hint,
            "text":self.text,
            "finished":self.finished,
            "node_type":self.node_type,
        }

    def from_dict(self, payload):
        if "id" in payload:
            self.id = payload["id"]
        if "question" in payload:
            self.question = payload["question"]
        if "hint" in payload:
            self.hint = payload["hint"]
        return self
    
@dataclass
class PromptNode:
    id: str = None
    prompt: str = None #template
    generated_prompt: str = None #prompt after template is ran
    system: str = None
    response: str = None
    node_type: str = "prompt"
    model: str = "gpt-4" #"gpt-3.5-turbo" # TODO: see why default model always shows

    finished: bool = False

    max_tokens: int = None
    temperature: float = 0.5
    stream: bool = True

    async def run(self, payload=None, prev_messages=None):
        
        if not prev_messages:
            prev_messages = []
        
        messages = []
        for msg in prev_messages:
            messages.append(msg)

        if self.system:
            messages.append(
                {"role":"system", "content":self.system.format(**payload)}
            )
        
        #print(self.prompt, payload)
        if self.prompt:
            self.generated_prompt = self.prompt.format(**payload)
            messages.append(
                {"role":"user", "content":self.generated_prompt}
            )

        
        response_str = ""
        responses = []
        response = openai.chat.completions.create(
                model=self.model, 
                messages=messages,
                temperature=self.temperature,
                stream=self.stream)


        async for resp in async_wrap_iter(response):
            #responses.append(resp)
            chunk = resp.choices[0].delta.content
            if chunk:
                #print(chunk["content"])
                response_str += chunk
                yield chunk, "stream" #resp.choices[0].text
        
    
        self.response = response_str 
        self.finished = True
    
    def to_dict(self):
        return {
            "id":self.id,
            "prompt":self.prompt,
            "system":self.system,
            "text":self.response,
            "finished":self.finished,
            "node_type":self.node_type,
            "generated_prompt":self.generated_prompt,
        }

    def from_dict(self, payload):
        if "id" in payload:
            self.id = payload["id"]
        if "prompt" in payload:
            self.prompt = payload["prompt"]
        if "system" in payload:
            self.system = payload["system"]
        if "model" in payload:
            self.model = payload["model"]
        if "max_tokens" in payload:
            self.max_tokens = payload["max_tokens"]
        if "temperature" in payload:
            self.temperature = payload["temperature"]
        # if "stream" in payload:
        #     self.stream = payload["stream"]
        return self
    
    async def get(self):
        return {"text":self.response}
    
    def set(self, payload):
        #TODO: see if prompt should have sett-able variables
        pass
    

@dataclass
class StorageNode:
    id: str = None
    variable_name: str = "text"
    value: str = None
    node_type: str = "storage"
    finished: bool = False

    async def run(self, payload=None):
        print("Set Storage", payload)
        if payload:
            if "text" in payload:
                self.value = payload["text"]
        self.finished = True
        yield None,"continue"
    
    def to_dict(self):
        return {
            "id":self.id,
            "variable_name":self.variable_name,
            "value":self.value,
            "finished":self.finished,
            "node_type":self.node_type,
        }
    
    def from_dict(self, payload):
        if "id" in payload:
            self.id = payload["id"]
        if "variable_name" in payload:
            self.variable_name = payload["variable_name"]
        if "value" in payload:
            self.value = payload["value"]
        return self

    async def get(self):
        return {self.variable_name:self.value}



@dataclass
class FinishNode:
    id: str = None
    node_type: str = "finish"
    type: str = "finish" #TODO: see why this is getting set
    outro_message: str = None
    outroMessage: str = None #TODO: remove and regenerate
    finished: bool = False

    makepdf: bool = False 

    async def run(self, payload=None):
        
        if payload and self.outro_message:
            if self.outroMessage:
                self.outro_message = self.outroMessage
            self.outro_message = self.outro_message.format(**payload)
        final_message = self.outro_message


        if self.makepdf == True:
            final_message = client_getting_secrets(self.outro_message)

        self.finished = True
        yield final_message,"finish"
    
    def to_dict(self):
        return {
            "id":self.id,
            "outro_message":self.outro_message,
            "finished":self.finished,
            "node_type":self.node_type,
            "makepdf":self.makepdf,
        }

    def from_dict(self, payload):
        if "id" in payload:
            self.id = payload["id"]
        if "outro_message" in payload:
            self.outro_message = payload["outro_message"]
        if "makepdf" in payload:
            self.makepdf = payload["makepdf"]
        return self
    
    async def get(self):
        return {}

@dataclass
class ContinueNode:
    id: str = None
    node_type: str = "continue"

    model: str = "gpt-4" 

    finished: bool = False

    max_tokens: int = None
    temperature: float = 0.5
    stream: bool = True
    
    messages: List[PromptNode] = field(default_factory=list) #list of PromptNode

    async def run(self, payload=None):
        #add a new prompt node
        #yield responses from prompt node including previous data

        #add payload defaults
        payload["model"] = self.model
        payload["prompt"] = payload["prompt"]
        #TODO

        new_node = PromptNode().from_dict(payload)

        async for msg,new_action in new_node.run(payload=payload):
            yield msg,new_action

        
        self.messages.append(new_node)

        yield None,"finish"
    
    def to_dict(self):
        return {
            "id":self.id,
            "messages":[x.to_dict() for x in self.messages],
            "node_type":self.node_type,
        }

    def from_dict(self, payload):
        if "id" in payload:
            self.id = payload["id"]
        if "messages" in payload:
            self.messages = [x.from_dict() for x in payload["messages"]]
        if "model" in payload:
            self.model = payload["model"]
        return self
    
    async def get(self):
        return {}