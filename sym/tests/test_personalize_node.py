import unittest
import json
import graphlib

from sym.modules.promptflow.nodes.personalize import ProfileData

from sym.modules.db.db import *
from sym.modules.db.models import *


class TestPersonalizeNode(unittest.TestCase):
    
    def test_init_node(self):
        #test initiialize works as expected
        init_payload = {}

        pass
