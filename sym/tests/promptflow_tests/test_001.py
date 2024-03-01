import unittest
import json
import graphlib
import asyncio
import logging


from sym.modules.promptflows.prompt_flow_runner import PromptFlowRunner
from sym.modules.promptflows.persistence import PromptFlowPersistenceSimulated
from sym.modules.promptflows.envelope import PromptFlowEnvelope
from sym.modules.promptflows.dispatcher import MessageDispatcherSimulated

from sym.modules.db.db import *
from sym.modules.db.models import *


logger = logging.getLogger(__name__)


class TestPromptFlow(unittest.IsolatedAsyncioTestCase):


    async def test_json_config_001(self):

        """ Test passing a json config, building a prompt 
            runner, and then measuring the output
        """

        #simple linear config
        flow_config = {
            "id":1,
            "nodes":[
                {
                    "id":1,
                    "node_type":"start",
                    "payload":{
                        "intro_text":"Hello there!"
                    }
                },
                {
                    "id":2,
                    "node_type":"question",
                    "payload":{
                        "question":"What are some of your favorite flavors?",
                        "variable":"flavors"
                    }
                },
                {
                    "id":3,
                    "node_type":"prompt",
                    "payload":{
                        "temperature":0.5,
                        "stream":False,
                        "model":"gpt-4",
                        "prompt":"""Given this persons love of these flavors: {{flavors}}
                                    Come up with 5 possible tea recommendations
                        """,
                        "system":"You are a helpful AI assistant which recommends teas"
                    }
                }
            ],
            "edges":[
                {
                    "id":1,
                    "start_node_id":1,
                    "end_node_id":2,
                },
                {
                    "id":2,
                    "start_node_id":2,
                    "end_node_id":3,
                },
            ]
        }

        #simulated messages
        user_messages = [
            {
                "action":"init",
                "prompt_flow_id":1,
                "prompt_run_id":1,
            },
            {
                "action":"send",
                "message":"I like raspberry, jasmin and lavender",
                "payload":{
                    "user_response":"I like raspberry, jasmin and lavender",
                },
                "prompt_flow_id":1,
                "prompt_run_id":1,
                "node_id":2,
                "prompt_run_item_id":2,
            },
        ]

        #use a JSON persistence strategy for this test
        json_persistence = PromptFlowPersistenceSimulated()
        json_persistence.config = flow_config

        #use a MessageDispatcherPrinter for this test
        simulated_dispatching = MessageDispatcherSimulated() 

        for message_payload in user_messages:

            #add our prompt_run_item_id here
            message_payload["prompt_run_item_id"] = simulated_dispatching.last_envelope_sent.prompt_run_item_id

            message_payload_text = json.dumps(message_payload)
            
            #load and initialize a prompt flow runner
            pfr = PromptFlowRunner(
                persistence=json_persistence,
                dispatcher=simulated_dispatching,
            )

            
            #simulate getting a message from the user
            envelope = await pfr.recieve_message(message=message_payload_text)
            logging.info(f"Recieved: {envelope.to_dict()}")
            

            pfr.input_envelope = envelope

            

            #now that we have an envelope, load our prompt flow
            pfr.build()

            #run the next iteration
            _ = await pfr.run()


            





    def test_e2e_001(self):
        #Define the flow in JSON 

        #load the flow into a DB / mocked equivalent
        #todo: how to instantiate a local db session equivalent

        #pull from DB 

        #instantiate the PromptRunner

        #Run the entire flow
        #TODO: how to instantiate a websocket test here
        #

        #validate the output is as expected
        #input -> expected
        #TODO: how to evaluate LLM variable responses

        #

        pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(name)s %(levelname)s %(message)s')
    unittest.main()