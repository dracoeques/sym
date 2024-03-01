from dataclasses import dataclass
import graphlib
graph = {"D": {"B", "C"}, "C": {"A"}, "B": {"A"}}
#todo: create example logic compose actions

@dataclass
class Node:
    id: int = None
    kind: str = None
    prompt: str = None
    text: str = None
    name: str = None

    sources = []
    targets = []

    def run(self):
        print(f"id:{self.id} kind:{self.kind}")

    def __hash__(self):
        return self.id
    
    def __eq__(self, other):
        if isinstance(other, Node):
            return self.__hash__() == other.__hash__()
        return NotImplemented

@dataclass
class Edge:

    source: int = None
    target: int = None

if __name__ == "__main__":

    n1 = Node(id=1, text="Hello world", kind="start")
    n2 = Node(id=2, text="What is your favorite dog?", kind="input")
    n3 = Node(id=3, kind="storage", name="dog")
    n4 = Node(id=4, kind="prompt", prompt="Tell me about {dog}")

    start_node = n1
    e1 = Edge(source=1, target=2) #start -> input
    e2 = Edge(source=2, target=3) #input -> storage
    e3 = Edge(source=3, target=4) #storage -> prompt




