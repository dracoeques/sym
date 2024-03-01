from dataclasses import dataclass, field
import asyncio, threading

from typing import List
import json
import openai
from jinja2 import Environment, BaseLoader

from sym.modules.promptflows.nodes.core import PromptNode


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
class PromptLoopNode(PromptNode):

    id: int = None
    node_type: str = "loop"

    #custom values unique to this node
    model: str = "gpt-4"
    temperature: float = 0.5
    max_tokens: int = None
    temperature: float = 0.5
    stream: bool = True

    prompt: str = ""
    generated_prompt: str = "" #prompt after template is ran
    system: str = ""
    generated_system: str = "" #system after template is ran

    response_text: str = "" #resulting text from running the prompt

    messages: List = field(default_factory=list)

    mock: bool = False
    mocked_response: str = None

    async def run(self, input_payload=None, **kwargs):

        print("Input to Loop", json.dumps(input_payload, indent=2))

        jinja_env = Environment(loader=BaseLoader)

        messages = []
        if input_payload is not None and "messages" in input_payload:
            messages = input_payload["messages"]
        
        #TODO: define template parameters as a separate component of the input_payload
        template_parameters = {}
        if input_payload is not None and "template_parameters" in input_payload:
            for k in input_payload["template_parameters"]:
                template_parameters[k] = input_payload[k]
        
        if self.system:
            system_template = jinja_env.from_string(self.system)
            self.generated_system = system_template.render(template_parameters)
            messages.append(
                {"role":"system", "content":self.generated_system}
            )

            #one option:
            #since we have a system message, remove all other system messages?

        if input_payload is not None and "user_data" in input_payload:
            if "user_response" in input_payload["user_data"]:
                self.prompt = input_payload["user_data"]["user_response"]
                messages.append(
                    {"role":"user", "content":input_payload["user_data"]["user_response"]}
                )
        if input_payload is not None and "message" in input_payload:
            self.prompt = input_payload["message"]
            messages.append(
                {"role":"user", "content":input_payload["message"]}
            )

        #TODO: add as a debug statement
        #print("Loop input: \n", json.dumps(messages, indent=2))
        print("Loop System", self.generated_system)
        
        if self.mock == True:
            if self.mock_response:
                self.response_text = self.mock_response
            else:
                self.response_text = f"""Mock default response: {self.generated_prompt} - {self.generated_system}"""
            yield self.generate_output_payload()
        
        else:
            response = openai.chat.completions.create(
                    model=self.model,
                    temperature=self.temperature, 
                    messages=messages,
                    stream=self.stream)

            
            if self.stream:
                async for resp in async_wrap_iter(response):
                    #responses.append(resp)
                    chunk = resp.choices[0].delta.content
                    if chunk:
                        self.response_text += chunk
                        yield self.generate_output_payload()
            else:
                self.response_text = response.choices[0].message.content
                yield self.generate_output_payload()
            
        
    
    def from_node_record(self, r):
        self.id = r.id
        
        payload = r.payload
        if payload:
            self.input_payload = payload
            if "prompt" in payload:
                self.prompt = payload["prompt"]
            if "system" in payload:
                self.system = payload["system"]
            if "temperature" in payload:
                self.temperature = payload["temperature"]
            if "model" in payload:
                self.model = payload["model"]
            if "stream" in payload:
                self.stream = payload["stream"]
            if "mock" in payload:
                self.mock = payload["mock"]

        return self

    def to_dict(self):
        return {
            "id":self.id,
            "prompt":self.prompt,
            "node_type":self.node_type,
        }
    
    def from_dict(self, payload):
        if "id" in payload:
            self.id = payload["id"]
        if "intro_text" in payload:
            self.intro_text = payload["intro_text"]
        return self

    def generate_output_payload(self, input_payload=None):

        d = {
            "id":self.id,
            "node_type":self.node_type,
            "message":self.response_text,
            "node_data":{
                "model":self.model,
                "temperature":self.temperature,
                "max_tokens":self.max_tokens,
                "stream":self.stream,

                "prompt":self.prompt,
                "generated_prompt":self.generated_prompt,
                "system":self.system,
                "generated_system":self.generated_system,

                "response_text":self.response_text,
            },
            "payload":{
                "prompt":self.prompt,
                "system":self.system,
                "response_text":self.response_text,
            }
        }

        return d
    
    def get_next_node_ids(self, edges=None):
        """ Given our edges, determine
            the next nodes to run
        """
        #looping, just return this node id
        return [self.id]

    def to_messages(self, output_payload=None):
        messages = []
        if "payload" in output_payload:
            #NOTE: we omit system since it can effect prompts
            #use it only in the call
            # if "system" in output_payload["payload"]:
            #     if output_payload["payload"]["system"]:
            #         messages.append(
            #             {"role":"system", "content":output_payload["payload"]["system"]}
            #         )
            if "prompt" in output_payload["payload"]:
                if output_payload["payload"]["prompt"]:
                    messages.append(
                        {"role":"user", "content":output_payload["payload"]["prompt"]}
                    )
            if "response_text" in output_payload["payload"]:
                if output_payload["payload"]["response_text"]:
                    messages.append(
                        {"role":"assistant", "content":output_payload["payload"]["response_text"]}
                    )
                
            
        return messages