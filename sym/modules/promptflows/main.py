import logging
import json

from sym.modules.auth.core import authenticate_ws_user
from sym.modules.auth.profile import get_default_profile, validate_user_profile

from sym.modules.promptflows.prompt_flow_runner import PromptFlowRunner
from sym.modules.promptflows.dispatcher import MessageDispatcherWebsocket
from sym.modules.promptflows.persistence import PromptFlowPersistenceDB

from sym.modules.db.models import PromptFlow
from sym.modules.db.models import Node as NodeRecord
from sym.modules.db.models import Edge as EdgeRecord



from sqlalchemy.orm.attributes import flag_modified

async def form_run(session, flow_id=None, payload=None):
    """ Run a prompt flow by passing in the values needed all at once
        Stream the results without needing a websocket connection / through the entire flow.
    """
    #TODO: assign global variables and attempt to complete the run, 
    #if we hit questions, assign results from the payload, if none, supply empty result
    #when streaming, use http streaming, or sync response based on the query param provided stream = true : false
    #

    #load the prompt flow
    if flow_id is None:
        raise Exception("flow_id is None, prompt flow id must be provided")

    pf = session.query(PromptFlow).filter(PromptFlow.id == flow_id).first()
    if pf is None:
        raise Exception(f"Prompt flow with id: {flow_id} not found")

    #given the variables provided in the payload, and the variables in the flow
    #assign those variables and run the flow
    #...


    pass




async def websocket_run(session, websocket):
    """ Default run using a websocket and a DB session"""
    dispatcher = MessageDispatcherWebsocket()
    dispatcher.websocket = websocket

    persistence = PromptFlowPersistenceDB()
    persistence.session = session


    while True:
        
        #load and initialize a prompt flow runner
        pfr = PromptFlowRunner(
            persistence=persistence,
            dispatcher=dispatcher,
        )
        pfr.session = session

        #get a message from our websocket
        envelope = await pfr.recieve_message()
        
        #check for user information / profile
        if envelope.authtoken:
            #print("Envelope AUTHTOKEN", envelope.authtoken)
            try:
                u = authenticate_ws_user(session, envelope)
                #print("Envelope USER", u.id)
                if u and envelope.profile_id is None:
                    #get their default profile
                    profile = get_default_profile(session, u.id)
                    envelope.profile_id = profile.id
                    #add this profile_id to our persistence module
                    pfr.persistence.profile_id = profile.id
                    #print("Envelope PROFILE", profile.id)
                else:
                    #TODO: confirm this user has access to use this profile
                    has_profile_access = validate_user_profile(session, u.id, envelope.profile_id)
                    if not has_profile_access:
                        #TODO: handle auth error here
                        logging.error(f"User is trying to access an invalid profile: user_id: {u.id} profile_id: {envelope.profile_id}")
                        #remove profile to prevent mis-auth
                        envelope.profile_id = None
            except Exception as e:
                #TODO: how to handle auth exception here?
                #we allow anonymous interactions
                logging.exception(e)
            
            

        #print(f"Recieved: {envelope.to_dict()}")
        

        #now that we have an envelope, load our prompt flow
        pfr.input_envelope = envelope
        envelopes = pfr.build()
        print("Existing envelopes", json.dumps([e.to_dict() for e in envelopes], indent=2))
        for m in envelopes:
            msg = await dispatcher.send_message(m)

        #run the next iteration
        _ = await pfr.run()



def save_prompt_flow(session, payload):
    """ parse and save a new prompt_flow from our frontend

        {

        id:1,
        name:"",
        category:"",
        "payload":{
        
            #network is our front end data structure
            "network":{
                
                "edges":[
                    {},
                    {},
                ],
                "nodes":[
                    {},
                ]
            },

            #node_data is how we store custom information 
            "node_data":{
                #... data belonging to these nodes
            }
        }
        }
    """

    if "id" in payload and payload["id"]:
        #existing prompt_flow, update values
        return update_prompt_flow(session, payload)
    else:
        return create_prompt_flow(session, payload)


def create_prompt_flow(session, payload):

    pf = PromptFlow().from_dict(payload)
    session.add(pf)
    session.commit()

    idstr2nodes = {}

    if "payload" in payload:
        inner_payload = payload["payload"]
        nodes = []
        edges = []
        if "network" in inner_payload:
            nodes = inner_payload["network"]["nodes"]
            edges = inner_payload["network"]["edges"]
        node_data = {}
        if "node_data" in inner_payload:
            node_data = inner_payload["node_data"]
        
        #add our nodes
        for node_config in nodes:
            node_payload = {}
            if node_config["id"] in node_data:
                node_payload = node_data[node_config["id"]]
            
            node_type = node_config["type"]
            id_str = node_config["id"]

            node_record = build_node_record(
                id_str=id_str,
                node_type=node_type,
                node_payload=node_payload,
                id_prompt_flow=pf.id,
            )
            session.add(node_record)
            idstr2nodes[id_str] = node_record
        
        session.commit()

        #add our edges
        for edge in edges:
            #print(edge)
            id_str = edge["id"]
            source = edge["source"]
            target = edge["target"]
            source_handle = edge["sourceHandle"]
            edge_payload = {
                "source_handle":source_handle,
            }
            node_source = idstr2nodes[source].id
            node_target = idstr2nodes[target].id
            edge_record = build_edge_record(
                id_str=id_str,
                id_prompt_flow=pf.id,
                start_node_id=node_source,
                end_node_id=node_target,
                edge_payload=edge_payload,
            )
            session.add(edge_record)
        session.commit()
            
    return pf

def build_node_record(
        id_str=None,
        node_type=None,
        node_payload=None,
        id_prompt_flow=None,
    ):
    n = NodeRecord()
    n.id_str = id_str
    n.node_type = node_type
    n.payload = node_payload
    n.id_prompt_flow = id_prompt_flow
    return n 

def build_edge_record(
        id_str=None,
        id_prompt_flow=None,
        start_node_id=None,
        end_node_id=None,
        edge_payload=None,
    ):
    e = EdgeRecord()
    e.id_str = id_str
    e.start_node_id = start_node_id
    e.end_node_id = end_node_id
    e.id_prompt_flow = id_prompt_flow
    e.payload = edge_payload
    return e

def update_prompt_flow(session, payload):
    
    id_prompt_flow = payload["id"]
    pf = session.query(PromptFlow)\
        .filter(PromptFlow.id == id_prompt_flow)\
        .first()
    if not pf:
        raise Exception(f"prompt flow id: {id_prompt_flow} not found")

    
    #update any values on prompt flow
    pf = pf.from_dict(payload)
    flag_modified(pf, "payload")
    session.commit()

    #update any nodes / edges

    #get existing nodes / edges
    idstr2nodes = {n.id_str:n for n in pf.nodes}
    idstr2edges = {e.id_str:e for e in pf.edges}

    #get new nodes / edges
    new_idstr2nodes = {}
    new_idstr2edges = {}
    
    if "payload" in payload:
        inner_payload = payload["payload"]
        nodes = []
        edges = []
        if "network" in inner_payload:
            nodes = inner_payload["network"]["nodes"]
            new_idstr2nodes = {n["id"] for n in nodes}

            edges = inner_payload["network"]["edges"]
            new_idstr2edges = {e["id"] for e in edges}

        node_data = {}
        if "node_data" in inner_payload:
            node_data = inner_payload["node_data"]
        
        #add our nodes
        for node_config in nodes:
            node_payload = {}
            if node_config["id"] in node_data:
                node_payload = node_data[node_config["id"]]
            
            node_type = node_config["type"]
            id_str = node_config["id"]

            if id_str not in idstr2nodes:
                #create a new node record
                node_record = build_node_record(
                    id_str=id_str,
                    node_type=node_type,
                    node_payload=node_payload,
                    id_prompt_flow=pf.id,
                )
                session.add(node_record)
            else:
                node_record = idstr2nodes[id_str]
                #update any values
                node_record.node_type = node_type
                node_record.payload = node_payload
                node_record.deleted = False
                flag_modified(node_record, "payload")
            idstr2nodes[id_str] = node_record

        #save our nodes
        session.commit()

        #add our edges
        for edge in edges:
            id_str = edge["id"]
            node_source = idstr2nodes[edge["source"]].id
            node_target = idstr2nodes[edge["target"]].id
            
            source_handle = edge["sourceHandle"]
            edge_payload = {
                "source_handle":source_handle,
            }
            if id_str not in idstr2edges:
                #create a new edge record
                edge_record = build_edge_record(
                    id_str=id_str,
                    id_prompt_flow=pf.id,
                    start_node_id=node_source,
                    end_node_id=node_target,
                    edge_payload=edge_payload,
                )
                session.add(edge_record)
            else:
                #use existing edge record and update it
                edge_record = idstr2edges[id_str]
                edge_record.start_node_id = node_source
                edge_record.end_node_id = node_target
                edge_record.deleted = False
                edge_record.payload = edge_payload
                flag_modified(edge_record, "payload")
        
        #save our edges
        session.commit()
    
    #final cleanup, delete any nodes or edges which no longer exist
    for idstr_old in idstr2nodes:
        if idstr_old not in new_idstr2nodes:
            node = idstr2nodes[idstr_old]
            #node no longer exists, delete it
            #note: since previous runs can reference this node, 
            #we just mark it as deleted
            if not node.deleted:
                node.deleted = True


    for idstr_old in idstr2edges:
        if idstr_old not in new_idstr2edges:
            edge = idstr2edges[idstr_old]
            #edge no longer exists, delete it
            #note: since previous runs can reference this edge, 
            #we just mark it as deleted
            if not edge.deleted:
                edge.deleted = True
    
    #finish any deletes
    session.commit()
    return pf


def duplicate_prompt_flow(session, id_prompt_flow):
    """ Duplicate a prompt flow and all of its nodes and edges """
    
    #TODO: Ted - duplicate prompt flow

    #load the prompt flow
    pf = session.query(PromptFlow)\
        .filter(PromptFlow.id == id_prompt_flow)\
        .first()
    if not pf:
        raise Exception(f"prompt flow id: {id_prompt_flow} not found")

    
    #get all nodes and edges for this flow from the database
    nodes = pf.nodes
    edges = pf.edges

    #get existing nodes / edges
    idstr2nodes = {}

    #create a new prompt flow object with the existing data 
    #CHANGE THE NAME
    new_pf = PromptFlow()

    #save the new prompt flow object
    session.add(pf)
    session.commit()

    #create new nodes and edges for the new prompt flow object
    #add our nodes
    for node_config in nodes:
        id_str = node_config["id"]
        node_type = node_config["type"]
        node_payload = node_config["node_payload"]

        node_record = build_node_record(
            id_str=id_str,
            node_type=node_type,
            node_payload=node_payload,
            id_prompt_flow=pf.id,
        )
        session.add(node_record)
        idstr2nodes[id_str] = node_record
    
    session.commit()

    #add our edges
    for edge in edges:
        #print(edge)
        id_str = edge["id"]
        source = edge["source"]
        target = edge["target"]
        source_handle = edge["sourceHandle"]
        edge_payload = {
            "source_handle":source_handle,
        }
        node_source = idstr2nodes[source].id
        node_target = idstr2nodes[target].id
        edge_record = build_edge_record(
            id_str=id_str,
            id_prompt_flow=pf.id,
            start_node_id=node_source,
            end_node_id=node_target,
            edge_payload=edge_payload,
        )
        session.add(edge_record)
    session.commit()

    return new_pf