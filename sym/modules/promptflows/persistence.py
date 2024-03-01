import json, logging
from dataclasses import dataclass
from sqlalchemy.orm.attributes import flag_modified

from sym.modules.db.models import PromptFlow, PromptRun, PromptRunItem
from sym.modules.db.models import Node as NodeRecord
from sym.modules.db.models import Edge as EdgeRecord


@dataclass
class PromptFlowPersistence:

    #Core class to maintain persistence of prompt flow data

    prompt_run_id: int = None
    prompt_flow_id: int = None


    def load_prompt_flow(self, prompt_flow_id=None):
        pass

    def save_prompt_flow(self, prompt_flow=None):
        pass

    def load_prompt_run(self, prompt_run_id=None):
        pass

    def save_run(self, prompt_run_id=None):
        pass

    def generate_run_item(self, node=None, profile=None):
        pass

    def update_run_item(self, run_item=None):
        pass


@dataclass
class PromptFlowPersistenceSimulated(PromptFlowPersistence):
    """ Simulate DB interactions, keeps data as dicts """

    prompt_run_id: int = None
    prompt_flow_id: int = None

    config = None #config which defines the flow

    prompt_flow = None
    prompt_run = None

    def load_prompt_flow(self, prompt_flow_id=None):
        if "id" in self.config and self.config["id"] != prompt_flow_id:
            raise Exception("Error: prompt flow id not found in config")
        
        pf = PromptFlow()
        pf.id = self.config["id"]
        nodes = []
        for node_config in self.config["nodes"]:
            n = NodeRecord().from_dict(node_config)
            nodes.append(n)
        edges = []
        for edge_config in self.config["edges"]:
            e = EdgeRecord().from_dict(edge_config)
            e.start_node_id = edge_config["start_node_id"]
            edges.append(e)
        pf.nodes = nodes
        pf.edges = edges
        return pf

    def save_prompt_flow(self, prompt_flow=None):
        self.prompt_flow = prompt_flow

    def load_prompt_run(self, prompt_run_id=None):
        if self.prompt_run and prompt_run_id == self.prompt_run.id:
            return self.prompt_run
        #create a new prompt run
        run = PromptRun()
        run.id = 1 #simulated id
        run.id_prompt_flow = self.config["id"]
        run.payload = {}
        run.items = []
        self.prompt_run = run
        return run

    def save_run_payload(self, payload=None):
        """ Save our run, including any graph values such as "next_nodes" """
        #simulated DB update to payload here ...
        self.prompt_run.payload = payload

    def save_run_items(self, 
            items=None,
            id_prompt_run=None,
        ):
        """ Save any new run items
            Assign sequential run item ids
        """
        last_id = 0
        if len(self.prompt_run.items) > 0:
            last_id = self.prompt_run.items[-1].id
        
        for item in items:
            last_id += 1
            item.id = last_id
            self.prompt_run.items.append(item)
    
    def update_run_items(self,
            items=None,
            id_prompt_run=None,
        ):
        #simply overwrite any existing items
        for item1 in items:
            for i,item2 in enumerate(self.prompt_run.items):
                if item1.id == item2.id:
                    self.prompt_run.items[i] = item1
    
    def generate_run_item(self, node=None, profile=None):
        #create a new run item, add reference to node id
        item = PromptRunItem()
        item.id_node = node.id

        item.id = len(self.prompt_run.items) +1 #simulated id
        self.prompt_run.items.append(item)
        return item
    
    def update_run_item(self, run_item=None):
        if run_item is None:
            raise Exception("Error: run_item cannot be none")
        #simply overwrite existing item
        for i,item in enumerate(self.prompt_run.items):
            if item.id == run_item.id:
                self.prompt_run.items[i] = run_item
                #print(f"updated run item: {run_item.input_payload} {run_item.output_payload}")

    def mark_run_completed(self, prompt_run=None):
        prompt_run.completed = True
        return prompt_run


@dataclass
class PromptFlowPersistenceDB(PromptFlowPersistence):
    """ Handle DB interactions using sqlalchemy sessions """

    session = None #db session client 

    prompt_flow = None
    prompt_flow_run = None

    profile_id = None

    def load_prompt_flow(self, prompt_flow_id=None):
        if prompt_flow_id is None:
            raise Exception("Error: prompt flow id is undefined")

        pf = self.session.query(PromptFlow)\
            .filter(PromptFlow.id == prompt_flow_id)\
            .first()
        
        if pf is None:
            raise Exception(f"Error: prompt_flow_id: {prompt_flow_id} not found")
        self.prompt_flow = pf
        return pf


    def load_prompt_run(self, prompt_run_id=None):
        if prompt_run_id is None and self.prompt_flow:
            #create a new prompt run
            run = PromptRun()
            run.id_prompt_flow = self.prompt_flow.id
            run.payload = self.prompt_flow.payload
            if self.profile_id:
                run.id_profile = self.profile_id
            self.prompt_run = run
            
            self.session.add(run)
            self.session.commit()
            return run
        else:
            run = self.session.query(PromptRun)\
                .filter(PromptRun.id == prompt_run_id)\
                .first()
            self.prompt_run = run
            if run is None:
                raise Exception(f"Prompt run: {prompt_run_id} not found")
        return run

    def save_run_payload(self, payload=None):
        """ Save our run, including any graph values such as "next_nodes" """
        #simulated DB update to payload here ...
        self.prompt_run.payload = payload
        flag_modified(self.prompt_run, "payload")
        self.session.commit()


    def save_run_items(self, 
            items=None,
            id_prompt_run=None,
        ):
        """ Save any new run items
        """
        # for item in items:
        #     run_item_record = PromptRunItem.from()
        #     self.session.add(item)
        for item in items:
            run_item_record = PromptRunItem().from_prompt_node(n=item, id_prompt_run=id_prompt_run)
            if self.profile_id:
                run_item_record.id_profile = self.profile_id
            self.session.add(run_item_record)
        self.session.commit()
            
    def update_run_items(self,
            items=None,
            id_prompt_run=None,
        ):
        #update any output payloads 
        for node in items:
            run_item_record = self.session.query(PromptRunItem)\
                .filter(PromptRunItem.id_prompt_run == id_prompt_run)\
                .filter(PromptRunItem.id_node == node.id)\
                .first()
            if not run_item_record:
                raise Exception(f"Run Item Record: {id_prompt_run} not found")
            run_item_record.output_payload = node.output_payload
            flag_modified(run_item_record, "output_payload")
        self.session.commit()
    
    def generate_run_item(self, node=None, profile=None):
        #create a new run item, add reference to node id
        item = PromptRunItem()
        item.id_node = node.id
        item.id_prompt_run = self.prompt_run.id
        if self.profile_id:
            item.id_profile = self.profile_id
        self.session.add(item)
        self.session.commit()
        return item


    def update_run_item(self, run_item=None):
        if run_item is None:
            raise Exception("Error: run_item cannot be none")
        
        #flag json as modified to ensure an update
        flag_modified(run_item, "input_payload")
        flag_modified(run_item, "output_payload")

        self.session.commit()

    def mark_run_completed(self, prompt_run=None):
        if prompt_run is None:
            raise Exception("Error: prompt run cannot be none")

        prompt_run.completed = True
        self.session.commit()
        return prompt_run