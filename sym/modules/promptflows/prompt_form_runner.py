import json
from dataclasses import dataclass, field

from sym.modules.db.models import *

from sym.modules.promptflows.envelope import PromptFormEnvelope
from sym.modules.promptflows.dispatcher import MessageDispatcher
from sym.modules.promptflows.persistence import PromptFlowPersistence
from sym.modules.promptflows.prompt_graph import PromptGraph


@dataclass
class PromptFormRunner:

    """ Prompt form attempts to run a prompt flow 
        from a single POST request. 

        The idea being that a separate UI engagement provided
        variables and other values, so we just need to set those
        and run the flow to complete the output

        NOTE: looping should not be possible here, or only 1 loop should occur per post 
    """

    session = None
    rawmsg = None
    input_envelope: PromptFormEnvelope = None
    persistence: PromptFlowPersistence = None
    dispatcher: MessageDispatcher = None
    prompt_flow: PromptFlow = None
    prompt_run: PromptRun = None
    prompt_graph: PromptGraph = None

    #A reference to any nodes which have been ran
    node2run_items: dict = None

    async def run(self, requires_input=None):
        """ Run the entire prompt flow 
        """

        #these node types will be skipped
        if requires_input is None:
            requires_input = set(["question", "loop"])

        #main loop
        while True:

            self.build_node2run_items()
            
            #get the next node to run
            node_to_run = self.prompt_graph.get_next()
            
            if node_to_run is None:
                break

            #if we require input, skip
            if node_to_run.node_type in requires_input:
                continue

            #print(f"Next node to run: {node_to_run.id} {node_to_run.node_type}")
            
            #generate a run_item to save our data to
            run_item = self.persistence.generate_run_item(node_to_run)

            #get any input data for this node to run
            input_payload = self.collect_input_payload(node_to_run, node2run_items=self.node2run_items)

            #print("INPUT_PAYLOAD: ", input_payload)

            #if we require input, skip
            if node_to_run.node_type in requires_input:
                continue

            #run the node
            async for output_payload in node_to_run.run(
                    input_payload=input_payload, 
                    id_profile=self.input_envelope.profile_id, #optional sym profile
                    session=self.session):
                
                #generate an output envelope
                output_envelope = self.build_envelope(
                        run_item=run_item,
                        node=node_to_run, 
                        node_output=output_payload)

                #dispatch that payload
                msg = await self.dispatcher.send_message(output_envelope)
                
                #TODO: check for an error in dispatch
                #msg == 'error'
                #...
            
            #node has finished, persist outputs to our run_item
            run_item.input_payload =  input_payload
            run_item.output_payload = output_payload
            
            #TODO: store convenience parameters to run_item
            # run_item.message = output_envelope.message
            # run_item.action = output_envelope.action
            #TODO: how to understand which item is coming from a person vs a bot
            self.persistence.update_run_item(run_item)

            #print("OUTPUT_PAYLOAD: ", json.dumps(output_payload, indent=2))

            #add our next nodes to our queue
            next_node_ids = node_to_run.get_next_node_ids(edges=self.prompt_graph.edges)
            for node_id in next_node_ids:
                self.prompt_graph.queue.put(node_id)

            #special case, if our run item is a finish node, mark the run finished
            if node_to_run.node_type == "finish":
                self.persistence.mark_run_completed(prompt_run=self.prompt_run)
            
        #cleanup, and persist any data for the next run
        self.cleanup()
    
    async def build(self, payload=None):
        """ Build our prompt_flow
            add any variables from our payload
        """
        #parse the raw message into a prompt form envelope
        if self.input_envelope is None:
            self.input_envelope = self.parse_rawmsg(rawmsg=self.rawmsg)
          
        #load the prompt flow data including nodes and edges
        if self.prompt_flow is None:
            self.prompt_flow = self.load_prompt_flow(envelope=self.input_envelope)

        #load any run data
        if self.prompt_run is None:
            self.prompt_run = self.load_prompt_run(envelope=self.input_envelope)
        
        #Build our graph given the prompt flow and prompt_run
        self.prompt_graph = self.build_graph(
            prompt_flow=self.prompt_flow,
            prompt_run=self.prompt_run,
        )

        #pre-run any question nodes
        self.set_variables()

    def set_variables(self):
        """ Given our input_payload, set any variables from the post request"""

        variables = self.input_envelope.variables

        for nid in self.prompt_graph.nodes:
            node = self.prompt_graph.nodes[nid]

            if node.node_type == "question":

                if node.variable in variables:
                    node.user_response = variables[node.variable]

                    #generate a run_item to save our data to
                    run_item = self.persistence.generate_run_item(node)
                    output_payload = node.generate_output_payload()
                    #run_item.input_payload =  input_payload
                    run_item.output_payload = output_payload
                    self.persistence.update_run_item(run_item)

    
    def parse_rawmsg(self, rawmsg=None):
        """ parse the raw message into a prompt form envelope"""
        if rawmsg is None:
            if self.rawmsg is not None:
                rawmsg = self.rawmsg
            else:
                raise Exception("Raw message is not defined")
        
        envelope_json = json.loads(rawmsg)
        envelope = PromptFormEnvelope().from_dict(envelope_json)
        self.input_envelope = envelope
        return envelope
    
    def load_prompt_flow(self, envelope=None):
        if envelope is None:
            if self.input_envelope is not None:
                envelope = self.input_envelope
            else:
                raise Exception("Prompt Flow Envelope is None")
        prompt_flow_id = envelope.prompt_flow_id 
        prompt_flow = self.persistence.load_prompt_flow(prompt_flow_id=prompt_flow_id)
        self.prompt_flow = prompt_flow
        return prompt_flow
    
    def load_prompt_run(self, envelope=None):
        if envelope is None:
            if self.input_envelope is not None:
                envelope = self.input_envelope
            else:
                raise Exception("Prompt Flow Envelope is None")
        
        prompt_run_id = envelope.prompt_run_id 
        prompt_run = self.persistence.load_prompt_run(prompt_run_id=prompt_run_id)
        self.prompt_run = prompt_run
        return prompt_run
    
    def build_graph(self, 
            prompt_flow=None,
            prompt_run=None):
        if prompt_flow is None:
            if self.prompt_flow is not None:
                prompt_flow = self.prompt_flow
            else:
                raise Exception("Prompt flow is none")
        if prompt_run is None:
            if self.prompt_run is not None:
                prompt_run = self.prompt_run
            else:
                #instantiate a new prompt run
                prompt_run = PromptRun()
        
        g = PromptGraph()
        g.prompt_flow = prompt_flow
        g.prompt_run = prompt_run
        g.build()
        self.prompt_graph = g
        return g
    
    def collect_input_payload(self, node, node2run_items=None):

        #special case for a continuation node, 
        # just supply the entire flow as a message list
        if node.node_type == "loop":

            return {
                "messages":self.generate_message_list(),
                "message":self.input_envelope.message,
            }

        #get all nodes which feed this node by their edges
        source_node_ids = self.prompt_graph.get_source_node_ids(node)

        payload = {}
        #generate a payload from each node which targets this node
        for node_id in source_node_ids:
            
        
            #generate any default node output - ie: nodes which don't have to be ran to produce valid output
            node_to_generate = self.prompt_graph.nodes[node_id]
            default_output = node_to_generate.generate_output_payload()
            #print(f"Source node: {node_id} {node_to_generate.node_type}")
            if "payload" in default_output:
                for k in default_output["payload"]:
                    if k == "null":
                        continue
                    v = default_output["payload"][k]
                    if v:
                        payload[k] = v
            
            if node_id in node2run_items:
                #if there's been a previous run of this node, overwrite any values
                for run_item in node2run_items[node_id]:
                    
                    output_payload =  run_item.output_payload
                    if "payload" in output_payload:
                        #NOTE: this will overwrite any variables which are using the same name
                        for k in output_payload["payload"]:
                            if k == "null":
                                continue
                            v = output_payload["payload"][k]
                            if v:
                                payload[k] = v
        
        #special case with prompts, we can include previous messages
        if node.node_type == "prompt":
            payload["messages"] = self.generate_message_list()
        
        #check if message exists, if not, add envelope message as text input
        if "text" not in payload:
            payload["text"] = self.input_envelope.message

        return payload
    
    def build_node2run_items(self):
        """ Keep a running log of each time a node was 
            ran, what was the output
        """
        node2run_items = {}
        #add our run items
        if self.prompt_run and self.prompt_run.items:
            for item in self.prompt_run.items:
                if item.id_node not in node2run_items:
                    node2run_items[item.id_node] = []
                node2run_items[item.id_node].append(item)

        #TODO: sort run items to maintain most recent run item
        for k in node2run_items:
            node2run_items[k].sort(key=lambda x: x.created_on)

        self.node2run_items = node2run_items