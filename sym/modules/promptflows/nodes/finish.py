from dataclasses import dataclass, field
import asyncio, threading


from jinja2 import Environment, BaseLoader

from sym.modules.promptflows.nodes.core import PromptNode, PromptEdge


@dataclass
class FinishNode(PromptNode):

    id: int = None
    node_type: str = "finish"

    #custom values unique to this node
    message_template: str = ""
    message_generated: str = ""

    async def run(self, input_payload=None, **kwargs):

        print("Finish node")

        jinja_env = Environment(loader=BaseLoader)

        template_parameters = {}
        if input_payload is not None:
            for k in input_payload:
                template_parameters[k] = input_payload[k]
        
        message_template = jinja_env.from_string(self.message_template)
        self.message_generated = message_template.render(template_parameters)
        
        yield self.generate_output_payload()
    
    def from_node_record(self, r):
        self.id = r.id
        
        payload = r.payload
        if payload:
            self.input_payload = payload
            if "message_template" in payload:
                self.message_template = payload["message_template"]

        return self
    
    def generate_output_payload(self):
        d = {
            "id":self.id,
            "node_type":self.node_type,
            "message":self.message_generated,
            "action":"finish",
            "node_data":{
                "message_template":self.message_template,
                "message_generated":self.message_generated,
            },
            "payload":{
                "message":self.message_generated,
            }
        }
        return d