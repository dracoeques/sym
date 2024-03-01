import json, logging
from dataclasses import dataclass


from sym.modules.db.models import *
from sym.modules.promptflows.envelope import PromptFlowEnvelope
from sym.modules.promptflows.dispatcher import MessageDispatcher
from sym.modules.promptflows.persistence import PromptFlowPersistence
from sym.modules.promptflows.prompt_graph import PromptGraph






@dataclass
class PromptFlowRunner:
    """ Main Class to instantiate and run a prompt flow 

    """

    session = None
    rawmsg = None 
    input_envelope: PromptFlowEnvelope = None
    
    persistence: PromptFlowPersistence = None
    dispatcher: MessageDispatcher = None

    prompt_flow: PromptFlow = None
    prompt_run: PromptRun = None
    prompt_graph: PromptGraph = None

    #user profile


    #run variables
    MAX_ITERS = 0 

    #A reference to any nodes which have been ran
    node2run_items: dict = None

    async def run(self, requires_input=None):
        """ Run the next iteration in the graph 
        """

        #accept user input, save to a prompt_run item 

        #accept any user input step - if our envelope has data to upate
        #get previous run item & update the values now
        self.update_user_input()

        #these node types will cause the runner to pause and wait for input
        if requires_input is None:
            requires_input = set(["question", "loop"])

        #print(self.input_envelope.message)

        
        #main loop
        while True:

            self.build_node2run_items()
            
            #get the next node to run
            node_to_run = self.prompt_graph.get_next()
            
            if node_to_run is None:
                break
            #print(f"Next node to run: {node_to_run.id} {node_to_run.node_type}")
            
            #generate a run_item to save our data to
            run_item = self.persistence.generate_run_item(node_to_run)

            #get any input data for this node to run
            input_payload = self.collect_input_payload(node_to_run, node2run_items=self.node2run_items)

            #print("INPUT_PAYLOAD: ", input_payload)

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
            
            #if we require input, break
            if node_to_run.node_type in requires_input:
                break

            
        #cleanup, and persist any data for the next run
        self.cleanup()

    def update_user_input(self, envelope=None):
        """ """
        
        #TODO: remove this step, any user input should just go to the next node in the graph
        #ie: message is sent in the envelope and any following nodes recieve it
        #to implement a question node, it would consist of two nodes, text_input and storage
        

        if envelope is None and self.input_envelope:
            envelope = self.input_envelope
        
        #if there's a user_message with values for a node set that now
        if envelope.node_id and envelope.prompt_run_item_id and envelope.payload:
            
            node = self.prompt_graph.nodes[envelope.node_id]

            #TODO: rebuild question as three separate nodes (Requires PromptNodeGroup)
            #text_display, text_input and a variable
            #and then remove update option so that run items
            #are immutable
            if node.node_type == "question":
                #print("Found a user input payload !!!")
                run_item_to_update = None
                #find the run item to update
                for item in self.node2run_items[envelope.node_id]:
                    if item.id == envelope.prompt_run_item_id:
                        run_item_to_update = item
                        break
                
                if run_item_to_update is None:
                    #updating a run_item that doesn't exist, throw an error
                    #print(self.node2run_items)
                    raise Exception(f"Run item id: {envelope.prompt_run_item_id} is not found")
            
            
                input_payload = run_item_to_update.input_payload
                #add user_data
                if "user_data" not in input_payload:
                    input_payload["user_data"] = {}
                
                #update any user_data provided variables
                for k in envelope.payload:
                    input_payload["user_data"][k] = envelope.payload[k]

                #re-run the node output step
                output_payload =  node.generate_output_payload(input_payload=input_payload)

                #print("updating input payload", input_payload)
                #print("updating output payload", output_payload)
                #now update the runitem
                run_item_to_update.input_payload = input_payload
                run_item_to_update.output_payload = output_payload
                self.persistence.update_run_item(run_item=run_item_to_update)
            
            

    async def recieve_message(self, message=None):
        """ Recieve a message from our dispatcher
        
            Note: message parameter will most likely be none, 
            but is provided to simulate recieving messages during tests
        """
        envelope = await self.dispatcher.recieve_message(message=message)
        return envelope

    def build(self):
        """ Load our prompt flow data graph

            Initialize any data from a previous run
        """
        print("Build runner")
        print("Envelope", self.input_envelope.to_dict())

        #parse the raw message into a prompt flow envelope
        if self.input_envelope is None:
            self.input_envelope = self.parse_rawmsg(rawmsg=self.rawmsg)
          
        #load the prompt flow data including nodes and edges
        if self.prompt_flow is None:
            self.prompt_flow = self.load_prompt_flow(envelope=self.input_envelope)

        #load any run data
        if self.prompt_run is None:
            self.prompt_run = self.load_prompt_run(envelope=self.input_envelope)
        
        self.build_node2run_items()

        #Build our graph given the prompt flow and prompt_run
        self.prompt_graph = self.build_graph(
            prompt_flow=self.prompt_flow,
            prompt_run=self.prompt_run,
        )

        #generate our list of envelopes from previous runs if they exist
        return self.generate_envelope_list()

    
    def parse_rawmsg(self, rawmsg=None):
        """ parse the raw message into a prompt flow envelope"""
        if rawmsg is None:
            if self.rawmsg is not None:
                rawmsg = self.rawmsg
            else:
                raise Exception("Raw message is not defined")
        
        envelope_json = json.loads(rawmsg)
        envelope = PromptFlowEnvelope().from_dict(envelope_json)
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

        #generate a payload from each node which targets this node
        payload = {}
        all_items_ran = [] #any previous runs of these nodes
        
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
                #if there's been a previous run of this node, concat any values
                all_items_ran += node2run_items[node_id]


        #re-sort our all_items_ran in order to maintain variable ordering / overwriting 
        #when multiple nodes reference the same variable
        #TODO:see if there is a way to use a reverse list and skip any repeats for a quicker iteration
        all_items_ran = sorted(all_items_ran, key= lambda x: x.created_on)
        for run_item in all_items_ran:
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

    def build_envelope(self,
                        run_item=None,
                        node=None, 
                        node_output=None):
        """ """
        output_envelope = PromptFlowEnvelope()
        
        output_envelope.prompt_flow_id = self.prompt_flow.id
        output_envelope.prompt_run_id = self.prompt_run.id
        output_envelope.node_id = node.id
        output_envelope.prompt_run_item_id = run_item.id
        output_envelope.node_type = node.node_type
        

        if "message" in node_output:
            output_envelope.message = node_output["message"]
        if "action" in node_output:
            output_envelope.action = node_output["action"]
        if "payload" in node_output:
            output_envelope.payload = node_output["payload"]
        if "node_data" in node_output:
            output_envelope.node_data = node_output["node_data"]
        
        return output_envelope

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

        #sort run items to maintain most recent run item first
        for k in node2run_items:
            node2run_items[k] = sorted(node2run_items[k], key=lambda x: x.created_on)

        self.node2run_items = node2run_items

    def cleanup(self, run_items=None):
        #persist output
        # new_run_items = []
        # for node in self.prompt_graph.nodes_ran:
        #     run_item = PromptRunItem().from_prompt_node(n=node, id_prompt_run=self.prompt_run.id)
        #     new_run_items.append(run_item)

        # self.persistence.save_run_items(items=new_run_items, id_prompt_run=self.prompt_run.id)
        # self.persistence.update_run_items(items=self.prompt_graph.run_items_updated, id_prompt_run=self.prompt_run.id)
        
        run_payload = self.prompt_run.payload
        run_payload["next_nodes"] = self.prompt_graph.queue.items
        #print("cleanup, next items", run_payload["next_nodes"] )
        self.persistence.save_run_payload(payload=run_payload)
        
    
    def generate_message_list(self, format="openai"):
        """ Generates a list output from the run as if it was
            just a continuous conversation in a chat
        """
        messages = []

        assistant_role = "assistant"
        user_role = "user"
        system_role = "system"
        
        
        for item in self.prompt_run.items:
            
            payload = item.output_payload
            if payload is None:
                continue
            if item.id_node in self.prompt_graph.nodes:
                node = self.prompt_graph.nodes[item.id_node]
                for msg in node.to_messages(output_payload=payload):
                    if "content" in msg and msg["content"]:
                        messages.append(msg)
        
        return messages
    
    def generate_envelope_list(self):
        """ Generates a list output from the run
        """

        envelopes = []
        for item in self.prompt_run.items:
            
            payload = item.output_payload
            if payload is None:
                continue
            if item.id_node in self.prompt_graph.nodes:
                node = self.prompt_graph.nodes[item.id_node]
                output_envelope = self.build_envelope(
                            run_item=item,
                            node=node, 
                            node_output=payload)
                envelopes.append(output_envelope)
        
        return envelopes