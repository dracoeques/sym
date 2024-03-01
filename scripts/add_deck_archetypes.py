import os
import json

from sym.modules.db.db import *
from sym.modules.db.models import *

from sqlalchemy.orm.attributes import flag_modified

def main():
    eng,fact = local_session()
    session = fact()

    #archetypes = generate_archetypes()
    archetypes = load_archetypes()

    #sort to preserve ordering
    categories = sorted(list(archetypes.keys()))

    for category in categories:
        print("Category:", category)
        #sort the sub categories to preserve ordering
        subcategories =  archetypes[category]
        subcategories.sort(key=lambda x: x["name"])

        for config in subcategories:
            print("\tSubcategory:", config["name"])
            deck = add_deck(
                session=session,
                category=category, 
                subcategory=config["name"],
                is_archetype=True
            )

            #add columns
            #...
            for col_order,col_config in enumerate(config["columns"]):
                #print(col_config["name"])
                col = add_column(
                    session=session,
                    name=col_config["name"],
                    deck=deck,
                    key=col_config["key"],
                    order=col_order,
                )

                #add column items
                #...
                for item_order, item_config in enumerate(col_config["items"]):
                    #print(item_config["key"])
                    col_item = add_column_item(
                        session=session,
                        column=col,
                        item_config=item_config,
                        order=item_order,
                    )





def add_deck(
        session=None,
        category=None, 
        subcategory=None,
        is_archetype=False):
    
    if category is None or subcategory is None:
        raise Exception("category and subcategory cannot be None")
    
    #check if deck exists
    d  = session.query(PromptDeck)\
        .filter(PromptDeck.category == category)\
        .filter(PromptDeck.subcategory == subcategory)\
        .filter(PromptDeck.is_archetype == is_archetype)\
        .first()
    
    addnew = False
    if not d:
        d = PromptDeck()
        addnew = True
    
    d.category = category
    d.subcategory = subcategory
    d.is_archetype = is_archetype

    if addnew:
        session.add(d)

    session.commit()
    return d

def add_column(session=None,
        deck=None, 
        name=None,
        key=None,
        order=0):
    
    #check if this column already exists
    col = session.query(PromptDeckColumn)\
        .filter(PromptDeckColumn.name == name)\
        .filter(PromptDeckColumn.id_deck == deck.id)\
        .first()
    
    #create a new column
    if not col:
        col = PromptDeckColumn()
        session.add(col)
    
    col.name = name
    col.id_deck = deck.id
    col.key = key
    col.order = order
    
    session.commit()
    return col

def add_column_item(
        session=None,
        column=None, 
        item_config=None,
        order=0):
    
    
    
    key = item_config["key"]

    item = None
    pdci = None
    if key == "prompt_flow":

        if "id" in item_config:
            item = get_prompt_flow(
                session=session,
                prompt_flow_id=item_config["id"],
            )
            #check for existing prompt Deck column item connecting this flow
            pdci = session.query(PromptDeckColumnItem)\
                .filter(PromptDeckColumnItem.id_column == column.id)\
                .filter(PromptDeckColumnItem.id_prompt_flow == item.id)\
                .first()
            
    elif key == "prompt_lib":
        if "id" in item_config:
            item = get_prompt_lib(
                 session=session,
                prompt_id=item_config["id"],
            )
            #check for existing prompt Deck column item connecting this flow
            pdci = session.query(PromptDeckColumnItem)\
                .filter(PromptDeckColumnItem.id_column == column.id)\
                .filter(PromptDeckColumnItem.id_prompt == item.id)\
                .first()
    
    #TODO: Next step, create prompt-flows for prompt-libs, a single node!
    #Next: test that inputs match outputs (unit test)

    #TODO catch new types:
    # elif key == "prompt-lib":
    #     item = add_prompt_lib(
    #         session=session,
    #         item_config=item_config,
    #     )

    if not item:
        return None

    
    
    if not pdci:
        pdci = PromptDeckColumnItem()
        session.add(pdci)

    pdci.id_column = column.id
    pdci.order = order
    pdci.key = key
    if key == "prompt_flow":
        pdci.id_prompt_flow = item.id
    elif key == "prompt_lib":
        pdci.id_prompt = item.id

    session.commit()

  

    return pdci



def get_prompt_flow(session=None, prompt_flow_id=None):
    if not prompt_flow_id:
        raise Exception("Prompt Flow ID must be provided")
    pf = session.query(PromptFlow)\
        .filter(PromptFlow.id == prompt_flow_id)\
        .first()
    return pf

def get_prompt_lib(session=None, prompt_id=None):
    if not prompt_id:
        raise Exception("Prompt id must be provided")
    p = session.query(Prompt)\
        .filter(Prompt.id == prompt_id)\
        .first()
    return p

def add_prompt_flow(
        session=None,
        item_config=None,
    ):

    name = None
    if name in item_config:
        name = item_config["name"]
    category = None
    if category in item_config:
        category = item_config["category"]
    subcategory = None
    if subcategory in item_config:
        subcategory = item_config["subcategory"]
    description = None
    if description in item_config:
        description = item_config["description"]

    #check for existing prompt flow
    #TODO: constrain this by a project to prevent collisions
    #ie: someone else makes a prompt flow with the same name, category and subcategory
    pf = session.query(PromptFlow)\
        .filter(PromptFlow.name == name)\
        .filter(PromptFlow.category == category)\
        .filter(PromptFlow.subcategory == subcategory)\
        .first()

    
    if not pf:
        pf = PromptFlow()
        session.add(pf)
    
    pf.name = name
    pf.category = category
    pf.subcategory = subcategory
    pf.description = description
    pf.payload = item_config
    flag_modified(pf, "payload")

    #save prompt flow
    session.commit()

    #create nodes with edges
    prev_node = None
    for node_config in item_config["nodes"]:

        node = add_node(
            session=session,
            prompt_flow=pf,
            config=node_config,
        )

        if prev_node is not None:
            edge = add_edge(
                session=session,
                start_node_id=prev_node.id,
                end_node_id=node.id,
            )
        prev_node = node
    
    return pf

def add_node(
        session=None,
        prompt_flow=None,
        config=None,    
    ):

    name = None
    if "name" in config:
        name = config["name"]

    node_type = None
    if "key" in config:
        node_type = config["key"]
    
    
    #check if this node already exists
    node = session.query(Node)\
        .filter(Node.id_prompt_flow == prompt_flow.id)\
        .filter(Node.name == name)\
        .filter(Node.node_type == node_type)\
        .first()
    
    if not node:
        node = Node()
        session.add(node)
    
    node.name = name
    node.node_type = node_type
    node.id_prompt_flow = prompt_flow.id
    node.payload = config
    flag_modified(node, "payload")

    session.commit()
    return node

def add_edge(
        session=None,
        start_node_id=None,
        end_node_id=None,    
    ):
    #check if this edge already exists
    edge = session.query(Edge)\
        .filter(Edge.start_node_id == start_node_id)\
        .filter(Edge.end_node_id == end_node_id)\
        .first()
    
    if not edge:
        edge = Edge()
        session.add(edge)
    
    edge.start_node_id = start_node_id
    edge.end_node_id = end_node_id

    session.commit()
    return edge
    
def add_prompt_lib(session=None, item_config=None):
    #Note: new prompt lib design will create a prompt flow with a single node
    #a prompt lib node
    pass


def load_archetypes(fp="data/archetype_decks.json"):
    with open(fp) as f:
        d = json.load(f)
    return d
    
def save_archetypes(d, fp="data/archetype_decks.json"):
    with open(fp, "w") as f:
        json.dump(d, f, indent=2)
    

def generate_archetypes():
    archetypes = {

        "Coaching":[
            {
                "name":"Relationships",
                "columns":[
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":110,
                                "key":"prompt_flow",
                                "name":"3 questions to help with coaching relationships"
                            }
                        ]
                    },
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":15,
                                "key":"prompt_lib",
                                "name":"Prompt libs for relationships",
                            },
                            {
                                "id":16,
                                "key":"prompt_lib",
                                "name":"Prompt libs for relationships",
                            },
                            {
                                "id":17,
                                "key":"prompt_lib",
                                "name":"Prompt libs for relationships",
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[{
                                "id":111,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Health",
                "columns":[
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":56,
                                "key":"prompt_flow",
                                "name":"3 questions for health coaching"
                            }
                        ]
                    },
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":18,
                                "key":"prompt_lib",
                                
                            },
                            {
                                "id":19,
                                "key":"prompt_lib",
                                
                            },
                            {
                                "id":20,
                                "key":"prompt_lib",
                                
                            }
                        ]
                    },
                    
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Career",
                "columns":[
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":21,
                                "key":"prompt_lib",
                                
                            },
                            {
                                "id":22,
                                "key":"prompt_lib",
                                
                            },
                            {
                                "id":23,
                                "key":"prompt_lib",
                                
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":57,
                                "key":"prompt_flow",
                                "name":"3 questions agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Money",
                "columns":[
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":24,
                                "key":"prompt_lib",
                                
                            },
                            {
                                "id":25,
                                "key":"prompt_lib",
                                
                            },
                            {
                                "id":26,
                                "key":"prompt_lib",
                                
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":58,
                                "key":"prompt_flow",
                                "name":"3 questions agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Spiritual",
                "columns":[
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":27,
                                "key":"prompt_lib",
                                
                            },
                            {
                                "id":28,
                                "key":"prompt_lib",
                                
                            },
                            {
                                "id":29,
                                "key":"prompt_lib",
                                
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":59,
                                "key":"prompt_flow",
                                "name":"3 questions agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Emotional",
                "columns":[
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":30,
                                "key":"prompt_lib",
                                
                            },
                            {
                                "id":31,
                                "key":"prompt_lib",
                                
                            },
                            {
                                "id":32,
                                "key":"prompt_lib",
                                
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":60,
                                "key":"prompt_flow",
                                "name":"3 questions agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },

            {   
                "name":"Decisions",
                "columns":[
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":54,
                                "key":"prompt_flow",
                                "name":"3 questions to help you with coaching decisions",
                                "category":"coaching",
                                "subcategory":"decisions",
                            }
                        ]
                    },
                    {
                        "name":"3 prompt libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":12,
                                "key":"prompt_lib",
                                "value":"I’m deciding between {traveling to destination|Seoul,New York,Paris}. Provide research and insights to help me make a decision.",
                                "system":"You are a coaching expert who helps their client make decisions",
                            },
                            {
                                "id":13,
                                "key":"prompt_lib",
                                "value":"Summarize the pros and cons between {the keto diet} and {the paleo diet}.",
                                "system":"You are a coaching expert who helps their client make decisions",
                            },
                            {
                                "id":14,
                                "key":"prompt_lib",
                                "value":"I am deciding {what university to go to for my master's}. Tell me what you do if you were in my situation. ",
                                "system":"You are a coaching expert who helps their client make decisions",
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                                "nodes":[
                                    {
                                        "name":"youdiy-question-1",
                                        "key":"question",
                                        "value":"What kind of expert would be most helpful to making your decision",
                                        "hint":"A strategic genius...",
                                        "storage":"you",
                                    },
                                    {
                                        "name":"youdiy-question-2",
                                        "key":"question",
                                        "value":"How would you describe yourself?",
                                        "hint":"I am a 30 year old engineer living in Montreal",
                                        "storage":"I",
                                    },
                                    {
                                        "name":"youdiy-question-3",
                                        "key":"question",
                                        "value":"What would be most helpful right now?",
                                        "hint":"List 5 simple effective decision-making frameworks I can use...",
                                        "storage":"do",
                                    },
                                    {
                                        "name":"youdiy-question-4",
                                        "key":"question",
                                        "value":"Why would this be helpful right now?",
                                        "hint":"I want to make stronger decisions more quickly.",
                                        "storage":"why",
                                    },
                                    {
                                        "name":"youdiy-prompt-1",
                                        "key":"prompt",
                                        "value":"You are {you} Help this individual: {I} by: {do} because: {why}",
                                        "system":"You are a coaching expert who helps their client make decisions"
                                    },
                                ]
                            }
                        ]
                    },
                ]
            }
        ],
        "Search":[
            {
                "name":"Geography",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":33,
                                "key":"prompt_lib",
                            },
                            {
                                "id":34,
                                "key":"prompt_lib",
                            },
                            {
                                "id":35,
                                "key":"prompt_lib",
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":61,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"History",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":36,
                                "key":"prompt_lib",
                            },
                            {
                                "id":37,
                                "key":"prompt_lib",
                            },
                            {
                                "id":38,
                                "key":"prompt_lib",
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":62,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Facts",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":39,
                                "key":"prompt_lib",
                            },
                            {
                                "id":40,
                                "key":"prompt_lib",
                            },
                            # {
                            #     "id":,
                            #     "key":"prompt_lib",
                            # }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":63,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Trends",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":41,
                                "key":"prompt_lib",
                            },
                            {
                                "id":42,
                                "key":"prompt_lib",
                            },
                            {
                                "id":43,
                                "key":"prompt_lib",
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":64,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Health",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":45,
                                "key":"prompt_lib",
                            },
                            {
                                "id":46,
                                "key":"prompt_lib",
                            },
                            {
                                "id":47,
                                "key":"prompt_lib",
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":65,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Research",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":48,
                                "key":"prompt_lib",
                            },
                            {
                                "id":49,
                                "key":"prompt_lib",
                            },
                            {
                                "id":50,
                                "key":"prompt_lib",
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":66,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Products",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":51,
                                "key":"prompt_lib",
                            },
                            {
                                "id":52,
                                "key":"prompt_lib",
                            },
                            {
                                "id":53,
                                "key":"prompt_lib",
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":67,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
        ],
        "Tech":[
            {
                "name":"Code",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":54,
                                "key":"prompt_lib",
                            },
                            {
                                "id":55,
                                "key":"prompt_lib",
                            },
                            {
                                "id":57,
                                "key":"prompt_lib",
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":68,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Support",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":58,
                                "key":"prompt_lib",
                            },
                            {
                                "id":59,
                                "key":"prompt_lib",
                            },
                            # {
                            #     "id":57,
                            #     "key":"prompt_lib",
                            # }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":69,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Architecture",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":60,
                                "key":"prompt_lib",
                            },
                            {
                                "id":61,
                                "key":"prompt_lib",
                            },
                            {
                                "id":62,
                                "key":"prompt_lib",
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":70,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Debugging",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":63,
                                "key":"prompt_lib",
                            },
                            {
                                "id":64,
                                "key":"prompt_lib",
                            },
                            {
                                "id":65,
                                "key":"prompt_lib",
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":71,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Syntax",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":66,
                                "key":"prompt_lib",
                            },
                            {
                                "id":67,
                                "key":"prompt_lib",
                            },
                            {
                                "id":68,
                                "key":"prompt_lib",
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":72,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Hardware",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":69,
                                "key":"prompt_lib",
                            },
                            {
                                "id":70,
                                "key":"prompt_lib",
                            },
                            {
                                "id":71,
                                "key":"prompt_lib",
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":73,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Recommendations",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":72,
                                "key":"prompt_lib",
                            },
                            {
                                "id":73,
                                "key":"prompt_lib",
                            },
                            {
                                "id":74,
                                "key":"prompt_lib",
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":74,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
        ],
        "Write":[
            {
                "name":"Content",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":75,
                                "key":"prompt_lib",
                            },
                            {
                                "id":76,
                                "key":"prompt_lib",
                            },
                            {
                                "id":77,
                                "key":"prompt_lib",
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":76,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Editing",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":78,
                                "key":"prompt_lib",
                            },
                            {
                                "id":79,
                                "key":"prompt_lib",
                            },
                            {
                                "id":80,
                                "key":"prompt_lib",
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":77,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Strategy",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":81,
                                "key":"prompt_lib",
                            },
                            {
                                "id":82,
                                "key":"prompt_lib",
                            },
                            {
                                "id":83,
                                "key":"prompt_lib",
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":78,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Emails",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":84,
                                "key":"prompt_lib",
                            },
                            {
                                "id":85,
                                "key":"prompt_lib",
                            },
                            {
                                "id":86,
                                "key":"prompt_lib",
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":79,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Agreements",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":87,
                                "key":"prompt_lib",
                            },
                            {
                                "id":88,
                                "key":"prompt_lib",
                            },
                            {
                                "id":89,
                                "key":"prompt_lib",
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":80,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Marketing",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":90,
                                "key":"prompt_lib",
                            },
                            {
                                "id":91,
                                "key":"prompt_lib",
                            },
                            {
                                "id":92,
                                "key":"prompt_lib",
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":81,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
            {
                "name":"Creative",
                "columns":[
                    
                    {
                        "name":"3 Prompt Libs",
                        "key":"prompt_libs",
                        "items":[
                            {
                                "id":93,
                                "key":"prompt_lib",
                            },
                            {
                                "id":94,
                                "key":"prompt_lib",
                            },
                            {
                                "id":95,
                                "key":"prompt_lib",
                            }
                        ]
                    },
                    {
                        "name":"3 questions",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":82,
                                "key":"prompt_flow",
                                "name":"3 Questions Agent"
                            }
                        ]
                    },
                    {
                        "name":"You I Do Why Style",
                        "key":"single_prompt_flow",
                        "items":[
                            {
                                "id":37,
                                "key":"prompt_flow",
                                "name":"You I do why coaching agent",
                            }
                        ]
                    },
                ],
            },
        ],
        "Learn":[
            {
                "name":"Health",
                "columns":[],
            },
            {
                "name":"History",
                "columns":[],
            },
            {
                "name":"Science",
                "columns":[],
            },
            {
                "name":"Homework",
                "columns":[],
            },
            {
                "name":"Prompting",
                "columns":[],
            },
            {
                "name":"Tutor",
                "columns":[],
            },
            {
                "name":"Math",
                "columns":[],
            },
        ],
        "Entertainment":[
            {
                "name":"Books",
                "columns":[],
            },
            {
                "name":"Games",
                "columns":[],
            },
            {
                "name":"Music",
                "columns":[],
            },
            {
                "name":"Movies",
                "columns":[],
            },
            {
                "name":"Travel",
                "columns":[],
            },
            {
                "name":"Puzzles",
                "columns":[],
            },
            {
                "name":"Crafts",
                "columns":[],
            },
        ],
        "Ideas":[
            {
                "name":"Brainstorm",
                "columns":[],
            },
            {
                "name":"Names",
                "columns":[],
            },
            {
                "name":"Models",
                "columns":[],
            },
            {
                "name":"Synthesize",
                "columns":[],
            },
            {
                "name":"Future",
                "columns":[],
            },
            {
                "name":"Solutions",
                "columns":[],
            },
            {
                "name":"Perspectives",
                "columns":[],
            },
        ]     
    }
    return archetypes

if __name__ == "__main__":
   
    main()
    