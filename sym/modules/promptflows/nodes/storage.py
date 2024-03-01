from dataclasses import dataclass, field

from sym.modules.promptflows.nodes.core import PromptNode, PromptEdge

from sym.modules.db.models import Node as NodeRecord
from sym.modules.db.models import Edge as EdgeRecord



@dataclass
class TextStorageNode(PromptNode):

    id: int = None
    node_type: str = "text_storage"

    #custom values unique to this node
    variable: str = None
    value: str = None


    async def run(self, input_payload=None, **kwargs):
        #print(f"Storage input: {input_payload}")
        if input_payload and "message" in input_payload:
            self.value = input_payload["message"]
        elif input_payload and "text" in input_payload:
            self.value = input_payload["text"]
        else:
            #TODO: reconsider this, set default payload output as text
            #in the output_payload of the run_item
            #arbitrarily set input value?
            for k in input_payload:
                self.value = input_payload[k]
        d = self.generate_output_payload(input_payload=input_payload)
        self.output_payload = d
        yield d
    
    def from_node_record(self, r):
        self.id = r.id
        payload = r.payload
        if payload:
            self.input_payload = payload
            if "variable" in payload:
                self.variable = payload["variable"]
            elif "variable_name" in payload:
                self.variable = payload["variable_name"]
        return self
    
    def generate_output_payload(self, input_payload=None):            

        d = {
            "message":"",
            "node_data":{
                "id":self.id,
                "node_type":self.node_type,
                "variable":self.variable,
            },
            "payload":{
                self.variable:self.value,
            },
            
        }
        return d
    
    def get_next_node_ids(self, edges=None):
        """ Given our edges, determine
            the next nodes to run
        """
        #NOTE: storage nodes can no longer 
        #do anything other than pass data
        return []