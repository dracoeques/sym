import unittest

import json

from sym.modules.promptflows.nodes.question import QuestionNode
from sym.modules.promptflows.persistence import PromptFlowPersistenceSimulated



class TestPromptNodes(unittest.TestCase):

    def question_node_persistence(self):

        
        # d = {
        #     "id":1,
        #     "nodes":[
        #             "id":1,
        #             "node_type":"question",
        #             "payload":{
        #                 "question_text":"What are some of your favorite flavors?",
        #                 "variable_name":"flavors",
        #             },
        #     ]
        # }
    
        # json_persistence = PromptFlowPersistenceSimulated()
        # json_persistence.config = d



        # q = QuestionNode()
        pass