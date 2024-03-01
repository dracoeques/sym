import graphlib
import json
import logging
from uuid import uuid4

from dataclasses import dataclass
from sym.modules.db.models import PromptFlow 
from sym.modules.db.models import PromptRun
from sym.modules.autolib.main import update_model_record

from sym.modules.promptflow.nodes import *

class AsyncIterator:
    def __init__(self, seq):
        self.iter = iter(seq)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration


@dataclass
class PromptFlowPayload:
    message: str = ""
    action: str = None #init, get_user_input, set_user_input, continue, finish

    prompt_flow_id: int = None
    prompt_run_id: int = None
    node_id: int = None
    node_type: str = None
    node_data = None 

    def from_dict(self, payload):
        if "message" in payload:
            self.message = payload["message"]
        if "action" in payload:
            self.action = payload["action"]
        if "prompt_flow_id" in payload:
            self.prompt_flow_id = payload["prompt_flow_id"]
        if "prompt_run_id" in payload:
            self.prompt_run_id = payload["prompt_run_id"]
        if "node_id" in payload:
            self.node_id = payload["node_id"]
        if "node_type" in payload:
            self.node_type = payload["node_type"]
        self.node_data = payload
        return self
    
    def to_dict(self):
        return {
            "message":self.message,
            "action":self.action,
            "prompt_flow_id":self.prompt_flow_id,
            "prompt_run_id":self.prompt_run_id,
            "node_id":self.node_id,
            "node_type":self.node_type,
            "node_data":self.node_data,
        }

@dataclass
class PromptFlowEnvelope:
    authtoken: str = None
    payload: PromptFlowPayload = None

    def from_dict(self, payload):
        if "authtoken" in payload:
            self.authtoken = payload["authtoken"]
        if "payload" in payload:
            self.payload = PromptFlowPayload().from_dict(payload["payload"])
        
        return self

    async def to_dict(self):
        d = {
            "authtoken":self.authtoken,
            "payload":None,
        }
        if self.payload:
            d["payload"] = self.payload.to_dict()
        return d

@dataclass
class PromptFlowRunner:
    """ Class to instantiate and run a prompt flow """

    session = None
    rawmsg = None
    envelope: PromptFlowEnvelope = None

    prompt_flow_id: int = None
    prompt_flow: PromptFlow = None

    prompt_run_id: int = None
    prompt_run: PromptRun = None

    #built components
    nodeid2node = {}
    graph = {}
    reversed_graph = {}
    node_order = []
    current_idx = 0

    def init(self):
        envelope_json = json.loads(self.rawmsg)
        logging.debug(json.dumps(envelope_json, indent=2))
        self.envelope = PromptFlowEnvelope().from_dict(envelope_json)
        pfm = self.envelope.payload

        if pfm.prompt_flow_id:
            self.prompt_flow_id = pfm.prompt_flow_id
        
        if pfm.prompt_run_id:
            self.prompt_run_id = pfm.prompt_run_id
        
        # if pfm.action == "prompt":
        #     #free form prompting
        #     self.

        if pfm.action == "init":
            self.init_records()
            self.build()
        else:
            self.load_records()
            self.build(self.prompt_run.payload)

        return self
    
    def init_records(self):
        #load our prompt flow record
        pf = self.session.query(PromptFlow)\
            .filter(PromptFlow.id == self.prompt_flow_id)\
            .first()
        if pf is None:
            raise Exception(f"Prompt flow: {self.prompt_flow_id} not found")
        self.prompt_flow = pf
        #instantiate a prompt_flow_run
        pfr = PromptRun()
        pfr.id_prompt_flow = self.prompt_flow.id
        pfr.payload = self.prompt_flow.payload
        self.session.add(pfr)
        self.session.commit()
        self.prompt_run = pfr
        self.prompt_run_id = pfr.id
        logging.info(f"Created Prompt Run {pfr.id}")
    
    def load_records(self):
        #load our prompt flow record
        pf = self.session.query(PromptFlow)\
            .filter(PromptFlow.id == self.prompt_flow_id)\
            .first()
        if pf is None:
            raise Exception(f"Prompt flow: {self.prompt_flow_id} not found")
        self.prompt_flow = pf

        #load prompt run record
        pfr = self.session.query(PromptRun)\
            .filter(PromptRun.id == self.prompt_run_id)\
            .first()
        if pfr is None:
            raise Exception(f"Prompt Run: {self.prompt_run_id} not found")
        self.prompt_run = pfr
        self.prompt_run_id = pfr.id
        logging.info(f"Loaded Prompt Run {pfr.id}")

    def build(self, flow_payload=None):
        """ Build and create a sequential flow from the dag
        """

        #on first run, flow_payload is the prompt_flow
        #on subsequent runs, we use the flow_run payload
        if flow_payload is None:
            if self.prompt_flow is None:
                raise Exception("prompt_flow is None")
            flow_payload = self.prompt_flow.payload
        print("Build step")
        #print(json.dumps(flow_payload, indent=2))

        #TODO: define node_data not nodeData
        node_data = {}
        if "node_data" in flow_payload:
            node_data = flow_payload["node_data"]
        #print("node_data", json.dumps(node_data, indent=2))

        
        #instantiate nodes
        default_order = []
        for n in flow_payload["network"]["nodes"]:
            node_id = n["id"]
            default_order.append(node_id)
            nodetype = n["type"]
            data = {"id":node_id}
            if node_id in node_data:
                data = node_data[node_id]
            else:
                print(f"{node_id} not found in node_data")
                print("node_data", json.dumps(node_data, indent=2))
            
            if nodetype == "start":
                node = StartNode().from_dict(data)
            elif nodetype == "text_input":
                node = TextInputNode().from_dict(data)
            elif nodetype == "storage":
                node = StorageNode().from_dict(data)
            elif nodetype == "prompt" or nodetype == "continue":
                node = PromptNode().from_dict(data)
            elif nodetype == "finish":
                node = FinishNode().from_dict(data)
            elif nodetype == "continue":
                node = ContinueNode().from_dict(data)
            else:
                raise Exception(f"Error, nodetype: {nodetype} not implemented")

            self.nodeid2node[node.id] = node

        graph = {}
        for e in flow_payload["network"]["edges"]:
            source = e["source"]
            target = e["target"]
            
            if source not in graph:
                graph[source] = set()
            graph[source].add(target)
        self.graph = graph

        reversed_graph = {}
        for k,s in graph.items():
            for v in s:
                if v not in reversed_graph:
                    reversed_graph[v] = set()
                reversed_graph[v].add(k)
        self.reversed_graph = reversed_graph
        
        try:
            ts = graphlib.TopologicalSorter(graph)
            self.node_order = tuple(ts.static_order())[::-1]
        except Exception as e:
            self.node_order = default_order
            logging.exception(e)
            

        

        #todo update current_idx based on answered items
        if "current_idx" in flow_payload:
            self.current_idx = flow_payload["current_idx"]
        else:
            self.current_idx = 0

    async def next(self, continue_after_finish=True):
        """ Run the next item in the node order 
        """

        stop_actions = set(["get_user_input", "finished"])
        action = self.envelope.payload.action

        # #special case, we want to continue chatting after the flow has ran
        # #add a new prompt node and execute that with the previous history
        # if action == "continue":
        #     self.

        while action not in stop_actions:
            print(f"Action: {action}")
            #special case, if we have recieved user input, add it here
            if action == "set_user_input":
                
                node_id = self.envelope.payload.node_id
                node = self.nodeid2node[node_id]
                node.set(self.envelope.payload.message)
                print("Setting user input", node)

            current_idx = self.current_idx
            #print(current_idx, len(self.node_order))
            if current_idx > len(self.node_order)-1:
                action = "out of items"
                break
            
            node_id = self.node_order[current_idx]

            #
            if node_id in self.nodeid2node:
                node = self.nodeid2node[node_id]
            else:
                print(f"node_id: {node_id} not found")
                #d = {k:self.nodeid2node[k].to_dict() for k in self.nodeid2node}
                #print("nodeid2node", json.dumps(d, indent=2))
                new_payload = PromptFlowPayload()
                new_payload.node_id = -1
                new_payload.message = f"node_id: {node_id} not found"
                new_payload.action = "error"
                new_payload.prompt_flow_id = self.prompt_flow_id
                new_payload.prompt_run_id = self.prompt_run_id
                new_envelope = PromptFlowEnvelope()
                new_envelope.authtoken = self.envelope.authtoken
                new_envelope.payload = new_payload
                yield new_envelope
                return

            #print(f"Node Id: {node_id}")
            print(f"Running Node: {node}")

            #gather inputs if any
            node_payload = {}
            
            if node_id in self.reversed_graph:
                inputs = self.reversed_graph[node_id]
                for other_node_id in inputs:
                    print(f"Inputs: {other_node_id}")
                    other_node = self.nodeid2node[other_node_id]
                    #todo add inputs to kwargs
                    d = await other_node.get()
                    for k in d:
                        node_payload[k] = d[k]
            
            #special case, continue node with previous node histories
            if node.node_type == "continue":
                prev_messages = self.to_messages()
                node_payload["prev_messages"] = prev_messages
                node_payload["prompt"] = self.envelope.payload.message

                
            #run the node
            async for msg,new_action in node.run(payload=node_payload):
                
                new_payload = PromptFlowPayload()
                new_payload.node_id = node.id
                new_payload.message = msg
                new_payload.node_type = node.node_type
                new_payload.action = new_action
                new_payload.prompt_flow_id = self.prompt_flow_id
                new_payload.prompt_run_id = self.prompt_run_id
                new_payload.node_data = node.to_dict()
                new_envelope = PromptFlowEnvelope()
                new_envelope.authtoken = self.envelope.authtoken
                new_envelope.payload = new_payload
                yield new_envelope
                if new_action in stop_actions:
                    break
            
            action = new_action
            if node.node_type != "continue": #we don't increment if it's continue, just loop on that node
                self.current_idx += 1

        self.cleanup()


    def cleanup(self):
        #save the responses to the promptflowrun
        #get ready for the next run
        
        prompt_run_payload = self.prompt_run.payload

        #print("node_order", json.dumps(self.node_order, indent=2))
        #d = {k:self.nodeid2node[k].to_dict() for k in self.nodeid2node}
        #print("nodeid2node", json.dumps(d, indent=2))

        node_data = {}
        for node_id in self.node_order:

            node = self.nodeid2node[node_id]
            node_data[node_id] = node.to_dict()
            prompt_run_payload["node_data"] = node_data
            prompt_run_payload["current_idx"] = self.current_idx
        
        #update the payload in our prompt_run
        update_model_record(self.session, self.prompt_run, {"payload":prompt_run_payload})
    
    def to_dict(self):
        """ Produce a dictionary representation of this model and it's data"""
        #TODO
        raise Exception("Not implemented")
    
    def to_messages(self, style="openai"):
        """ Converts our prompt flow into a list of messages which are compatible 
            with a model style
        """
        if style == "openai":
            prompt_run_payload = self.prompt_run.payload
            return None #TODO
        else:
            raise Exception(f"Model style {style} is not implemented")

    def continue_prompting(self, message):
        """ Continue prompting with this flow after this ran"""
        pass

    def generate_uuid(self):
        return str(uuid4())