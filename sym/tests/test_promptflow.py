import unittest
import json
import graphlib

from sym.modules.promptflow.core import PromptFlowRunner

from sym.modules.db.db import *
from sym.modules.db.models import *


class TestPromptFlow(unittest.TestCase):

    def test_graphlogic(self):

        #Ordered graph
        #get inputs, targets
        #iterate through graph logic
        #next step, implement this with the node types

        n1 = Node(id=1, text="Hello world", kind="start")
        n2 = Node(id=2, text="What is your favorite kind of dog?", kind="input")
        n3 = Node(id=3, kind="storage", name="dog")
        n4 = Node(id=4, kind="prompt", prompt="Tell me about the {dog} breed")
        n5 = Node(id=5, kind="prompt", prompt="What are 3 possible names for a {dog}")


        graph = {
            n1:{n2}, #start -> input
            n2:{n3}, #input -> storage
            n3:{n4, n5}, #storage -> prompt1, prompt2
        }

        reversed_graph = {}
        for k,s in graph.items():
            for v in s:
                if v not in reversed_graph:
                    reversed_graph[v] = set()
                reversed_graph[v].add(k)

        ts = graphlib.TopologicalSorter(graph)
        reversed_order = tuple(ts.static_order())[::-1]
        for node in reversed_order:

            print(node)

            if node in reversed_graph:
                inputs = reversed_graph[node]
                for x in inputs:
                    print(f"Inputs: {x}")

            if node in graph:
                targets = graph[node]
                for x in targets:
                    print(f"Targets: {x}")
    
    def test_graphlogic2(self):
        graph = {"D": {"B", "C"}, "C": {"A"}, "B": {"A"}}
        ts = graphlib.TopologicalSorter(graph)
        print(tuple(ts.static_order()))

    def test_promptflow001(self):
        data = {
            "message":"init"
        }

        engine,session_factory = local_session()
        session = session_factory()
        pf = PromptFlowRunner()
        pf.session=session
        pf.rawmsg=data
        pf.init()

    def test_promptflow002(self):

        data = {
            
        }
        
if __name__ == "__main__":
    unittest.main()