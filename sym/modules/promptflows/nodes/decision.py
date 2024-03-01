from dataclasses import dataclass, field
from typing import Dict
import asyncio, threading

import re

from jinja2 import Environment, BaseLoader

from sym.modules.promptflows.nodes.core import PromptNode, PromptEdge

@dataclass
class LabelDecisionNode(PromptNode):
    id: int = None
    node_type: str = "numeric_decision"

    #maps from text input to the desired next node
    options: Dict[str, int] = field(default_factory=dict)
    
    #TODO: create label -> decision mappings


@dataclass
class BinaryNumericDecisionNode(PromptNode):

    #NEXT STEPS:
    #add in the choose next nodes based on decision logic
    #TODO: have a payload or key on the edge which denotes which edge is which

    id: int = None
    node_type: str = "binary_numeric_decision"

    operator: str = "<"
    threshold: int = 5
    decision: str = None #'next-a' or 'next-b'
    default: str = "next-a" #default value to take

    value: float = None
    
    error: str = None

    async def run(self, input_payload=None, **kwargs):
        print("Input to decision", input_payload)
        #get input value & try to cast to a number
        if "text" in input_payload:
            value,err = self.extract_float(input_payload["text"])
            self.value = value
            self.error = err
            if err:
                #print(f"Error parsing decision: {err}")
                pass
        
        if self.value is not None:
            self.decision = self.make_decision()
        else:
            self.decision = self.default
        
        yield self.generate_output_payload()

    def extract_float(self, s):
        cleaned_string = ''.join(char for char in s if char.isdigit() or char == '.')

        # Attempt to cast the cleaned string to a float
        try:
            return float(cleaned_string), None
        except ValueError:
            # If casting fails, return a graceful message or handle the error as needed
            return None, f"Failed to convert: {s} to float"


    def make_decision(self):
        o = self.operator
        meets_threshold = False
        if o == "<":
            if self.value < self.threshold:
                meets_threshold = True
        elif o == "<=":
            if self.value <= self.threshold:
                meets_threshold = True
        elif o == ">=":
            if self.value >= self.threshold:
                meets_threshold = True
        elif o == ">":
            if self.value > self.threshold:
                meets_threshold = True
        
        print(f"{self.value} {o} {self.threshold} is {meets_threshold}")

        if meets_threshold:
            return "next-a"
        else:
            return "next-b"

    
    def from_node_record(self, r):
        self.id = r.id
        
        payload = r.payload
        if payload:
            self.input_payload = payload
            if "operator" in payload:
                o = payload["operator"]
                if o in ["<", "<=", ">", ">="]:
                    self.operator = o
            if "threshold" in payload:
                self.threshold = payload["threshold"]
            if "default" in payload:
                self.default = payload["default"]

        return self
    
    def generate_output_payload(self):
        d = {
            "id":self.id,
            "node_type":self.node_type,
            "node_data":{
                "id":self.id,
                "node_type":self.node_type,
                "operator":self.operator,
                "threshold":self.threshold,
                "decision":self.decision,
                "default":self.default,
                "value":self.value,
                "error":self.error,

            },
            "payload":{
                "decision":self.decision,
            }
        }
        return d
    
    def get_next_node_ids(self, edges=None):
        """ Given our edges, determine
            the next nodes to run
        """


        if edges is None:
            return []
        
        target_node_ids = []
        chosen_node_ids = []
        for _,edge in edges.items():
            if edge.start_node_id == self.id:

                #TODO: based on edge value
                #only include edges which fall under the decision branch
                edge_branch = None
                if "source_handle" in edge.payload:
                    edge_branch = edge.payload["source_handle"] 
                if self.decision == edge_branch:
                    chosen_node_ids.append(edge.end_node_id)
                target_node_ids.append(edge.end_node_id)
        return chosen_node_ids