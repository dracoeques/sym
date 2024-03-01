from dataclasses import dataclass, field
import asyncio, threading
import json

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
class PromptLLMNode(PromptNode):

    id: int = None
    node_type: str = "prompt"

    #custom values unique to this node
    model: str = "gpt-4"
    temperature: float = 0.5
    max_tokens: int = None
    temperature: float = 0.5
    stream: bool = True #stream token by token or if false, don't
    history: bool = True #whether or not to use historical messages as input to prompt
    display: bool = True #whether or not to display the output, when set to false will not show in chat

    prompt: str = ""
    generated_prompt: str = "" #prompt after template is ran
    system: str = ""
    generated_system: str = "" #system after template is ran

    response_text: str = "" #resulting text from running the prompt

    mock: bool = False #whether to mock a response, useful for testing
    mock_response: str = None

    max_context_length = 4097

    async def run(self, input_payload=None, **kwargs):

        #print("Input to Prompt", json.dumps(input_payload, indent=2))

        jinja_env = Environment(loader=BaseLoader)
        
        template_parameters = {}
        if input_payload is not None:
            for k in input_payload:
                if type(k) != str:
                    print(f"Error: k is not str: {k}")
                else:
                    template_parameters[k] = input_payload[k]
        
        print("template_parameters", json.dumps(template_parameters, indent=2))

        messages = []

        if "messages" in input_payload and self.history:
            messages = self.truncate_messages(input_payload["messages"])
        
        if self.system:
            system_template = jinja_env.from_string(self.system)
            try:
                self.generated_system = system_template.render(template_parameters)
                messages.append(
                    {"role":"system", "content":self.generated_system}
                )
            except Exception as e:
                print("Exception: ", e)
        
    
        if self.prompt:
            prompt_template = jinja_env.from_string(self.prompt)
            self.generated_prompt = prompt_template.render(template_parameters)
            messages.append(
                {"role":"user", "content":self.generated_prompt}
            )

        print("Prompt Messages", json.dumps(messages, indent=2))

        
        if self.mock == True:
            if self.mock_response:
                self.response_text = self.mock_response
            else:
                self.response_text = f"""Mock default response: {self.generated_prompt} - {self.generated_system}"""
            yield self.generate_output_payload()
        
        else:
            #TODO: adapt to new api design
            #see utils
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
            if "history" in payload:
                self.history = payload["history"]
            if "display" in payload:
                self.display = payload["display"]

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
                "prompt":self.generated_prompt,
                "system":self.system,
                "text":self.response_text,
            }
        }
        action = "display"
        if not self.display:
            action = "silent"
        d["action"] = action
        return d

    def to_messages(self, output_payload=None):
        messages = []
        if "payload" in output_payload:
            if "prompt" in output_payload["payload"]:
                prompt_text = output_payload["payload"]["prompt"]
                messages.append({"role":"user", "content":prompt_text})
            #NOTE: we omit system since it can mess up other downstream prompts
            # if "system" in output_payload["payload"]:
            #     system_text = output_payload["payload"]["system"]
            #     messages.append({"role":"system", "content":system_text})
            if "text" in output_payload["payload"]:
                text = output_payload["payload"]["text"]
                messages.append({"role":"assistant", "content":text})
        return messages


    def truncate_messages(self, messages, max_context_length=4097):
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

        #remove other system prompts
        deduped_system = []
        system_prompts = set()
        for m in reversed(messages):
            if m["role"] == "system":
                continue
            else:
                deduped_system.append(m)
        deduped_system = list(reversed(deduped_system))

        # Loop through the messages in reverse to get the latest messages
        for m in reversed(deduped_system):
            message = m["content"]
            if total_length + len(message) > max_context_length:
                break
            total_length += len(message)
            truncated_messages.append(m)

        return list(reversed(truncated_messages))
