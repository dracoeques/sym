from dataclasses import dataclass, field
import asyncio, threading
from typing import Dict

from jinja2 import Environment, BaseLoader

from sym.modules.promptflows.nodes.core import PromptNode, PromptEdge
from sym.modules.personalization.relevant_context import get_relevant_profile_datums

@dataclass
class ProfileDataNode(PromptNode):
    """ Use this node to provide relevant profile data given a prompt"""

    id: int = None
    node_type: str = "personalize"

    #custom values unique to this node
    id_profile: int = None
    session = None
    context_str_template: str = "" #what context should we pull data relevant to?
    context_str_generated: str = ""
    key_value_pairs: Dict = field(default_factory=dict) #any key value pairs relevant to context string
    key_value_start_char: str = "- " #the character which starts each kv line
    key_value_end_char: str = "\n" #the character which ends each kv line
    limit = 10

    async def run(self, input_payload=None, id_profile=None, session=None, **kwargs):

        print("input to personalize", input_payload)
        print("personalize id_profile", id_profile)
        print("personalize session", session)
        print(f"personalize template: {self.context_str_template}")

        if id_profile is None or session is None:
            #if running anonymously we cannot return profile information
            yield self.generate_output_payload()
        else:
            jinja_env = Environment(loader=BaseLoader)

            template_parameters = {}
            if input_payload is not None:
                for k in input_payload:
                    template_parameters[k] = input_payload[k]
            
            context_str_template = jinja_env.from_string(self.context_str_template)
            self.context_str_generated = context_str_template.render(template_parameters)
            print(f"PERSONALIZED CONTEXT: {self.context_str_generated}")
            #get relevant context
            datums,t = get_relevant_profile_datums(self.context_str_generated, id_profile=id_profile, limit=self.limit, session=session)
            self.key_value_pairs = {d.key:d.value for d in datums}

            yield self.generate_output_payload()
    
    def from_node_record(self, r):
        self.id = r.id
        
        payload = r.payload
        if payload:
            self.input_payload = payload
            if "context" in payload:
                self.context_str_template = payload["context"]
            elif "context_str_template" in payload:
                self.context = payload["context_str_template"]
        return self
    
    def generate_output_payload(self):
        key_value_str = self.render_key_value_string()
        d = {
            "id":self.id,
            "node_type":self.node_type,
            "message":key_value_str,
            "node_data":{
                "context_str_template":self.context_str_template,
                "context_str_generated":self.context_str_generated,
            },
            "payload":{
                "context":self.context_str_generated,
                "key_value_pairs":self.key_value_pairs,
                "key_value_str":key_value_str,
            }
        }

        return d
    
    def render_key_value_string(self):
        """ Render a key-value list as a string if possible
            else return an empty string
        """
        key_value_str = ""
        if len(self.key_value_pairs) > 0:
            key_value_str = """"""
            for k,v in self.key_value_pairs.items():
                key_value_str += f"{self.key_value_start_char}{k}: {v} {self.key_value_end_char}"
        return key_value_str