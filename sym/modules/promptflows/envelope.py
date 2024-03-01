

from typing import Any
from dataclasses import dataclass, field

@dataclass
class PromptFlowEnvelope:
    
    #Node
    message: str = "" #optional text to display
    action: str = None #init, get_user_input, set_user_input, continue, finish etc.
    payload: dict[str, Any] = None #data sent back and forth
    
    node_id: int = None
    node_type: str = None
    node_data:  dict[str, Any] = None #optional data confguration for node

    #State
    authtoken: str = None
    profile_id: int = None #sym profile sending message
    prompt_flow_id: int = None
    prompt_run_id: int = None
    prompt_run_item_id: int = None
    

    def from_dict(self, payload):
        if "authtoken" in payload:
            self.authtoken = payload["authtoken"]
        if "message" in payload:
            self.message = payload["message"]
        if "action" in payload:
            self.action = payload["action"]
        if "payload" in payload:
            self.payload = payload["payload"]
        if "prompt_flow_id" in payload:
            self.prompt_flow_id = payload["prompt_flow_id"]
        if "prompt_run_id" in payload:
            self.prompt_run_id = payload["prompt_run_id"]
        if "prompt_run_item_id" in payload:
            self.prompt_run_item_id = payload["prompt_run_item_id"]
        if "node_id" in payload:
            self.node_id = payload["node_id"]
        if "node_type" in payload:
            self.node_type = payload["node_type"]
        if "profile_id" in payload:
            self.profile_id = payload["profile_id"]
        
        return self
    
    def to_dict(self, emit_authtoken=False):
        d = {
            
            #node information
            "message":self.message,
            "action":self.action,
            "payload":self.payload,
            
            "node_id":self.node_id,
            "node_type":self.node_type,
            "node_data":self.node_data,
            
            #stateful information
            "profile_id":self.profile_id,
            "prompt_flow_id":self.prompt_flow_id,
            "prompt_run_id":self.prompt_run_id,
            "prompt_run_item_id":self.prompt_run_item_id,
            
        }
        #note we omit authtoken in response by default
        if self.authtoken and emit_authtoken == True:
            d["authtoken"] = self.authtoken
        return d



@dataclass
class PromptFormEnvelope:
    
    #Node
    message: str = "" #optional text to display
    action: str = None #init, get_user_input, set_user_input, continue, finish etc.
    payload: dict[str, Any] = None #data sent back and forth
    
    node_id: int = None
    node_type: str = None
    node_data:  dict[str, Any] = None #optional data confguration for node

    #State
    authtoken: str = None
    profile_id: int = None #sym profile sending message
    prompt_flow_id: int = None
    prompt_run_id: int = None
    prompt_run_item_id: int = None
    
    #prompt forms expect a dictionary of variables
    variables: dict[str, Any] =  field(default_factory=dict)

    def from_dict(self, payload):
        if "authtoken" in payload:
            self.authtoken = payload["authtoken"]
        if "message" in payload:
            self.message = payload["message"]
        if "action" in payload:
            self.action = payload["action"]
        if "payload" in payload:
            self.payload = payload["payload"]
        if "prompt_flow_id" in payload:
            self.prompt_flow_id = payload["prompt_flow_id"]
        if "prompt_run_id" in payload:
            self.prompt_run_id = payload["prompt_run_id"]
        if "prompt_run_item_id" in payload:
            self.prompt_run_item_id = payload["prompt_run_item_id"]
        if "node_id" in payload:
            self.node_id = payload["node_id"]
        if "node_type" in payload:
            self.node_type = payload["node_type"]
        if "profile_id" in payload:
            self.profile_id = payload["profile_id"]

        if "variables" in payload:
            variables = {}
            for v in payload["variables"]:
                variables[v] = payload["variables"][v]
            self.variables = variables
        else:
            self.variables = {}

        
        return self
    
    def to_dict(self, emit_authtoken=False):
        d = {
            
            #node information
            "message":self.message,
            "action":self.action,
            "payload":self.payload,
            
            "node_id":self.node_id,
            "node_type":self.node_type,
            "node_data":self.node_data,
            
            #stateful information
            "profile_id":self.profile_id,
            "prompt_flow_id":self.prompt_flow_id,
            "prompt_run_id":self.prompt_run_id,
            "prompt_run_item_id":self.prompt_run_item_id,

            "variables":self.variables,
            
        }
        #note we omit authtoken in response by default
        if self.authtoken and emit_authtoken == True:
            d["authtoken"] = self.authtoken
        return d



