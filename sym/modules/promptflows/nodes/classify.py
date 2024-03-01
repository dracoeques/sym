from dataclasses import dataclass, field
import asyncio, threading


import openai
from jinja2 import Environment, BaseLoader


from sym.modules.promptflows.nodes.core import PromptNode, PromptEdge

from sym.modules.db.models import Node as NodeRecord
from sym.modules.db.models import Edge as EdgeRecord



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
class ClassifyLLMNode(PromptNode):

    id: int = None
    node_type: str = "prompt_classify"
    input_payload = None
    output_payload = None

    #custom values unique to this node
    model: str = "gpt-4"
    temperature: float = 0.5
    max_tokens: int = None
    temperature: float = 0.5
    stream: bool = True
    mock: bool = False #whether to mock a response, useful for testing

    prompt: str = ""
    generated_prompt: str = "" #prompt after template is ran
    system: str = ""
    generated_system: str = "" #system after template is ran

    response_text: str = "" #resulting text from running the prompt

    

    async def run(self, input_payload=None):

        jinja_env = Environment(loader=BaseLoader)
        
        template_parameters = {}
        if input_payload is not None:
            for k in input_payload:
                template_parameters[k] = input_payload[k]
            
        messages = []
        
        if self.system:
            system_template = jinja_env.from_string(self.system)
            self.generated_system = system_template.render(template_parameters)
            messages.append(
                {"role":"system", "content":self.generated_system}
            )
    
        if self.prompt:
            prompt_template = jinja_env.from_string(self.prompt)
            self.generated_prompt = prompt_template.render(template_parameters)
            messages.append(
                {"role":"user", "content":self.generated_prompt}
            )

        #print(messages)
        
        if self.mock == True:
            text = f"""prompt: {self.generated_prompt} \nSystem:{self.generated_system} """
            self.response_text = text
            yield self.generate_output_payload()
        
        else:
            response = openai.ChatCompletion.create(
                    model=self.model,
                    temperature=self.temperature, 
                    messages=messages,
                    stream=self.stream)

            
            if self.stream:
                async for resp in async_wrap_iter(response):
                    #responses.append(resp)
                    chunk = resp.choices[0]["delta"]
                    if "content" in chunk and chunk["content"]:
                        self.response_text += chunk["content"]
                        yield self.generate_output_payload()
            else:
                self.response_text = response.choices[0].message["content"]
                yield self.generate_output_payload()
            
            #save our final output payload to this node instance
            self.output_payload = self.generate_output_payload()
            self.finished = True
    
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

            #testable responses
            if "mock" in payload:
                self.mock = payload["mock"]
            if "mock_response" in payload:
                self.mock_response = payload["mock_response"]

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

    def generate_output_payload(self):
        d = {
            "id":self.id,
            "node_type":self.node_type,
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
                "prompt":self.generated_prompt,
                "system":self.system,
                "message":self.response_text,
            }
        }
        return d