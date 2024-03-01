import asyncio
from dataclasses import dataclass, field
from typing import Dict, List
import copy


from sym.modules.db.models import PromptFlow, PromptRun, PromptRunItem

from sym.modules.db.models import Edge as EdgeRecord
from sym.modules.db.models import Node as NodeRecord

from sym.modules.promptflows.nodes.core import PromptEdge, PromptNode
from sym.modules.promptflows.nodes.start import StartNode
from sym.modules.promptflows.nodes.question import QuestionNode
from sym.modules.promptflows.nodes.prompt import PromptLLMNode
from sym.modules.promptflows.nodes.storage import TextStorageNode
from sym.modules.promptflows.nodes.classify import ClassifyLLMNode
from sym.modules.promptflows.nodes.display import DisplayTextNode
from sym.modules.promptflows.nodes.loop import PromptLoopNode 
from sym.modules.promptflows.nodes.decision import BinaryNumericDecisionNode
from sym.modules.promptflows.nodes.personalize import ProfileDataNode
from sym.modules.promptflows.nodes.pdfnode import PDFNode
from sym.modules.promptflows.nodes.variable import TextVariableNode
from sym.modules.promptflows.nodes.finish import FinishNode

@dataclass
class NodeQueue:
    items: List[int] = field(default_factory=list)
    
    def get(self):
        if len(self.items) > 0:
            return self.items.pop(0)
        return None
    
    def put(self, item):
        self.items.append(item)
    
    def empty(self):
        if len(self.items) > 0:
            return False
        return True

@dataclass
class PromptGraph:

    nodes: Dict[int, PromptNode] = None
    edges: Dict[int, PromptEdge] = None

    #optionally we could use a string id to discover a node
    #because: front end javascript

    prompt_flow: PromptFlow = None
    prompt_run: PromptRun = None

    #node -> run_items in order of run 
    node2run_items: Dict[int, List[PromptRunItem]] = None

    #queue to maintain next nodes to run
    #queue: asyncio.Queue = None
    queue: NodeQueue = None

    #nodes ran - A list of all nodes which were ran with their data
    nodes_ran: List[PromptNode] = field(default_factory=list)
    
    #a list of all nodes which recieved any updated input from frontend
    run_items_updated: List[PromptNode] = field(default_factory=list)

    def build(self, payload=None):
        #print("Building graph")

        self.nodes = {}
        self.edges = {}

        #validate that a prompt_flow is provided
        if self.prompt_flow is None:
            raise Exception("Prompt flow cannot be none")
        
        self.nodes_ran = []

        if self.queue is None:
            self.queue = NodeQueue()
        
        #re-hydrate our queue if next_nodes is provided
        if self.prompt_run.payload and "next_nodes" in self.prompt_run.payload:
            for item in self.prompt_run.payload["next_nodes"]:
                self.queue.put(item)

        #build our nodes
        for node_record in self.prompt_flow.nodes:
            if node_record.deleted:
                continue
            node = self.build_node_from_record(node_record)
            self.nodes[node.id] = node

        #build our edges
        for edge_record in self.prompt_flow.edges:
            if edge_record.deleted:
                continue
            edge = self.build_edge_from_record(edge_record)
            self.edges[edge.id] = edge

    def set_user_input(self, envelope):
        """ Pre-step before running, update any values in previous run_items
            if necessary
        """

        #if there's a user_message with values for a node set that now
        if envelope.node_id and envelope.message is not None:
            
            run_item_to_update = None
            if envelope.run_item_id:
                #update the provided run item
                for item in self.node2run_items[envelope.node_id]:
                    if item.id == envelope.run_item_id:
                        run_item_to_update = item
                        break
            else:
                #default to the most recently ran item
                run_item_to_update = self.node2run_items[envelope.node_id][-1]
            
            #get the node config and regenerate the output_payload
            prev_node = self.nodes[envelope.node_id]
            updated_payload = prev_node.update_payload(
                envelope=envelope,
                previous_output=run_item_to_update.output_payload,
            )
            #print("updating payload", updated_payload)
            run_item_to_update.output_payload = updated_payload
            self.run_items_updated.append(run_item_to_update)

    



    def get_next(self):
        """ Return the next node to be run
            any relevant input data so they can be ran

            generator yields:
                node, input_payload

                Node: 
                    - Instance of Prompt Node
                    - InputPayload Dictionary, any output from source nodes
        """
        #check if queue is empty
        if self.queue.empty() != True:
            #not empty, return next node
            return self.get_item_from_queue()
            
        #has this been run yet? 
        last_run_item = None
        if self.prompt_run and self.prompt_run.items:
            last_run_item = self.prompt_run.items[-1]
        
        if last_run_item is None:
            #First run - return the start node
            start_node = self.get_start_node()
            if start_node is None:
                raise Exception("Error: Graph has no start node")
            return start_node
        
        #no nodes to be ran
        #ie: queue is empty and not the first run
        return None
    
    

    def get_item_from_queue(self):
        node_id = self.queue.get()
        if node_id not in self.nodes:
            raise Exception(f"Queue referenced node id: {node_id} but it is not defined in graph")
        return self.nodes[node_id]

    def get_start_node(self):
        for node_id in self.nodes:
            node = self.nodes[node_id]
            if node.node_type == "start":
                return node
        return None
    
    def get_next_nodes(self, last_node):

        target_node_ids = []
        #TODO: special case with decision nodes
        #decide next node based on input
        if last_node.node_type == "decision":
            
            return last_node.get_next_node_ids(edges=self.edges)
        elif last_node.node_type == "loop":
            #this node is now looping, always return the same id
            return [last_node.id]
        else:
            target_node_ids = self.get_target_node_ids(last_node)

        
        return target_node_ids

    def get_source_node_ids(self, node):
        """ Given this node, get all nodes which feed into it via an edge (ie: source nodes)"""
        source_node_ids = []

        #collect any node ids which send data to this node
        for edge_id in self.edges:
            edge = self.edges[edge_id]
            if edge.end_node_id == node.id:
                source_node_ids.append(edge.start_node_id)
        

        # special case, if this node is a variable node, 
        # by default it pushes it's data to each node
        # ie: like a global variable
        for node_id in self.nodes:
            node = self.nodes[node_id]
            if node.node_type == "variable":
                source_node_ids.append(node.id)
            elif node.node_type == "question":
                #questions have a variable feature
                #TODO: decouple question into two nodes
                source_node_ids.append(node.id)

        return source_node_ids
    
    def get_target_node_ids(self, node):
        """ Given this node, get all nodes which are recieved by it via an edge (ie: target nodes)"""
        target_node_ids = []
        for edge_id in self.edges:
            edge = self.edges[edge_id]
        
            if edge.start_node_id == node.id:
                target_node_ids.append(edge.end_node_id)
        return target_node_ids


    def build_node_from_record(self, node_record):
        """ Build a node from the 'Node' ie: NodeRecord db model provided"""
        t = node_record.node_type
        node = self.build_node_from_type(t)
        return node.from_node_record(node_record)
        

    def build_edge_from_record(self, edge_record):
        return PromptEdge().from_edge_record(edge_record)
    
    
    
    def build_node_from_type(self, node_type):
        """ Map node_type to class instantiation"""
        if node_type == "start":
            return StartNode()
        elif node_type == "question":
            return QuestionNode()
        elif node_type == "prompt":
            return PromptLLMNode()
        elif node_type == "text_storage" or node_type == "storage":
            return TextStorageNode()
        elif node_type == "loop":
            return PromptLoopNode()
        elif node_type == "binary_numeric_decision":
            return BinaryNumericDecisionNode()
        elif node_type == "personalize":
            return ProfileDataNode()
        elif node_type == "pdf":
            return PDFNode()
        elif node_type == "variable":
            return TextVariableNode()
        elif node_type == "display_text":
            return DisplayTextNode()
        elif node_type == "finish":
            return FinishNode()
        # elif node_type == "prompt_classify":
        #     return Promp
        else:
            raise Exception(f"PromptGraph.build_node_from_type - node type: {node_type} not implmented")
    


    
            
                


