from dataclasses import dataclass, field

from sym.modules.promptflows.nodes.core import PromptNode, PromptEdge

from sym.modules.db.models import Node as NodeRecord
from sym.modules.db.models import Edge as EdgeRecord


@dataclass
class StartNode(PromptNode):

    id: int = None
    node_type: str = "start"

    #custom values unique to this node
    intro_text: str = None

    async def run(self, input_payload=None, **kwargs):
        d = self.generate_output_payload()
        self.output_payload = d
        yield d
    
    def from_node_record(self, r):
        self.id = r.id
        payload = r.payload
        if payload:
            self.input_payload = payload
            if "intro_text" in payload:
                self.intro_text = payload["intro_text"]

        return self
    
    def from_dict(self, payload):
        if "id" in payload:
            self.id = payload["id"]
        if "intro_text" in payload:
            self.intro_text = payload["intro_text"]
        return self

    def to_dict(self):
        return {
            "id":self.id,
            "node_type":self.node_type,
            "intro_text":self.intro_text,
        }

    def generate_output_payload(self):
        d = {
            "action":"display",
            "message":self.intro_text,
            "payload":{
                "text":self.intro_text,
            },
            "node_data":{
                "id":self.id,
                "node_type":self.node_type,
                "intro_text":self.intro_text,
            },
            
            
        }
        return d