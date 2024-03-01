from dataclasses import dataclass, field
import copy

from jinja2 import Environment, BaseLoader


from sym.modules.promptflows.nodes.core import PromptNode, PromptEdge

from sym.modules.db.models import Node as NodeRecord
from sym.modules.db.models import Edge as EdgeRecord


@dataclass
class QuestionNode(PromptNode):

    id: int = None
    node_type: str = "question"

    #custom values unique to this node
    question: str = ""
    variable: str = ""
    user_response: str = ""

    question_rendered: str = ""

    input_payload = None
    output_payload = None

    async def run(self, input_payload=None, **kwargs):
        """ 
            Question Node
        """

        #print("Question input", input_payload)

        jinja_env = Environment(loader=BaseLoader)
        
        #run any formatting on question_text
        self.question_rendered = self.question
        if input_payload and "payload" in input_payload:
            template = jinja_env.from_string(self.question)
            self.question_rendered = template.render(input_payload["payload"])
            
            #self.question_rendered = self.question.format(**input_payload["payload"]) 

        #return values
        d = self.generate_output_payload()
        self.output_payload = d
        yield d
        
        
    
    def update_payload(self, envelope=None, previous_output=None):
        """
            Given the new envelope and the previous output 
            stored in the run item, update / overwrite 
            any new values from the envelope

        """
        new_payload = envelope.payload
        if "payload" in previous_output:
            updated_payload = previous_output["payload"]
        else:
            updated_payload = {}
        
        #overwrite / add new data to payload
        for k in new_payload:
            #eg: user_response -> would be added here
            #NOTE: this will overwrite any previous data keys
            #if needed, we can limit this to only specific things
            updated_payload[k] = new_payload[k]
        
        #update our output data payload
        updated_output = copy.deepcopy(previous_output)
        updated_output["payload"] = updated_payload
        return updated_output

    
    def from_node_record(self, r):
        self.id = r.id
        
        payload = r.payload
        if payload:
            self.input_payload = payload
            if "question" in payload:
                self.question = payload["question"]
            if "variable" in payload:
                self.variable = payload["variable"]
        return self

    def to_dict(self):
        return {
            "id":self.id,
            "question":self.question,
            "node_type":self.node_type,
        }
    
    def from_dict(self, payload):
        if "id" in payload:
            self.id = payload["id"]
        if "intro_text" in payload:
            self.intro_text = payload["intro_text"]
        return self

    def generate_output_payload(self, input_payload=None):

        #check for any input_data from a user
        if input_payload and "user_data" in input_payload:
            if "user_response" in input_payload["user_data"]:
                self.user_response = input_payload["user_data"]["user_response"]


        d = {
            "id":self.id,
            "node_type":self.node_type,
            "action":"display",
            "node_data":{
                "question":self.question,
                "question_rendered":self.question_rendered,
                "variable":self.variable,
                "user_response":self.user_response,
            },
            "message":self.question_rendered,
            "payload":{
                "variable":self.variable,
                "user_response":self.user_response,
            }
        }

        d["payload"] = {
            self.variable:self.user_response,
        }

        return d
    
    def get_variables(self):
        return {self.variable: self.user_response}

    def to_messages(self, output_payload=None):
        messages = []
        if "payload" in output_payload:
            if "question_text" in output_payload["payload"]:
                question_text = output_payload["payload"]["question_text"]
                messages.append({"role":"assistant", "content":question_text})
            elif "node_data" in output_payload:
                if "question" in output_payload["node_data"]:
                    question_text = output_payload["node_data"]["question"]
                    messages.append({"role":"assistant", "content":question_text})
            
            if "user_response" in output_payload["payload"]:
                user_response = output_payload["payload"]["user_response"]
                messages.append({"role":"user", "content":user_response})
        return messages