import json
import copy

from sym.modules.db.db import *
from sym.modules.db.models import *

from sym.modules.promptflows.main import save_prompt_flow

from sqlalchemy.orm.attributes import flag_modified

def save_3_question_agents(archetypes=None, folder = "data/flows/3_questions/"):
    eng,fact = local_session()
    session = fact()
    
    
    if archetypes is None:
        with open("data/archetype_decks.json") as f:
            archetypes = json.load(f)

    #category -> subcategory -> 3_q_agents
    with open("data/3_questions_main.json") as f:
        d = json.load(f)
    


    for cat in archetypes:
        for config in archetypes[cat]:
            sub = config["name"]

            if cat not in d:
                d[cat] = {}
            
            if sub not in d[cat]:
                d[cat][sub] = {}


            folder = "data/flows/3_questions/"
            filename = f"{cat}_{sub}.json"
            
            with open(folder+filename) as f:
                q3_payload = json.load(f)
            
            pf_payload = d[cat][sub]
            pf_payload["payload"] = q3_payload
            pf_payload["name"] = f"{cat} {sub} 3 questions agent - v2"
            pf_payload["category"] = cat
            pf_payload["subcategory"] = sub
            pf_payload["version"] = 2
            d[cat][sub] = pf_payload

            
            pf = save_prompt_flow(session, pf_payload)
            print(f"{cat} {sub} Prompt flow: {pf.id}")
            d[cat][sub]["id"] = pf.id
           
    
    with open("data/3_questions_main.json", "w") as f:
        json.dump(d, f, indent=2)

def generate_3question_archetypes(fp="data/archetype_decks.json"):
    with open(fp) as f:
        d = json.load(f)
    
    for cat in d:
        for config in d[cat]:
            sub = config["name"]
            generate_3question_flow(cat, sub)


def generate_3question_flow(category, subcategory, temperature=1.0):
    name = f"{category} {subcategory} 3 question agent - v2"
    
    #load the example payload
    with open("data/flows/example.json") as f:
        example = json.load(f)
    payload = copy.deepcopy(example)

    #structure 

    #first question intro 
    intro = f"""Welcome to the 3 question {category} {subcategory} agent. This bot is designed to ask you 3 highly relevant questions and provide instant feedback. To begin can you describe briefly the topic you'd like help with?"""

    #set first question
    payload["node_data"]["node_1697563524578"]["question"] = intro

    #update system prompts
    system = f"""You are an expert at {category} {subcategory}, provide helpful advice and feedback"""
    # p1
    payload["node_data"]["node_1697563526429"]["system"] = system
    payload["node_data"]["node_1697563526429"]["temperature"] = temperature

    # p2
    payload["node_data"]["node_1697563785636"]["system"] = system
    payload["node_data"]["node_1697563785636"]["temperature"] = temperature

    # p3
    payload["node_data"]["node_1697563981318"]["system"] = system
    payload["node_data"]["node_1697563981318"]["temperature"] = temperature

    # p4
    payload["node_data"]["node_1697564046524"]["system"] = system
    payload["node_data"]["node_1697564046524"]["temperature"] = temperature

    # p5
    payload["node_data"]["node_1697564158430"]["system"] = system
    payload["node_data"]["node_1697564158430"]["temperature"] = temperature

    #update value prompt
    value_prompt = """Given this topic {{topic}} \n\nAnd this survey:\n\nQuestion 1: {{q1}}\nAnswer 1: {{a1}}\n\nQuestion 2: {{q2}}\nAnswer 2: {{a2}}\n\nQuestion 3: {{q3}}\nAnswer 3: {{a3}}\n\nProvide helpful """+f"{category} {subcategory}"+""" advice for this situation"""
    payload["node_data"]["node_1697564046524"]["prompt"] = value_prompt

    #save output
    with open(f"data/flows/3_questions/{category}_{subcategory}.json", "w") as f:
        json.dump(payload, f, indent=2)

def update_prompt_archetypes():
    """ now we set our ids in the prompt deck archetypes"""
    
    with open("data/archetype_decks.json") as f:
        archetypes = json.load(f)

    #category -> subcategory -> 3_q_agents
    with open("data/3_questions_main.json") as f:
        d = json.load(f)

    for cat in archetypes:
        for i,config in enumerate(archetypes[cat]):
            sub = config["name"]
            q3_payload = d[cat][sub]
            q3_item = {
                        "id":q3_payload["id"],
                        "name":q3_payload["name"],
                        "key":"prompt_flow",
                    }
            q3_column = {
                    "name": "3 questions",
                    "key": "single_prompt_flow",
                    "items":[
                       q3_item, 
                    ]
                }

            #add our first column
            if len(archetypes[cat][i]["columns"]) == 0:
                archetypes[cat][i]["columns"].append(q3_column)
            else:
                #or update the first column
                archetypes[cat][i]["columns"][0] = q3_column
    
    with open("data/archetype_decks.json", "w") as f:
        json.dump(archetypes, f, indent=2)
    

if __name__ == "__main__":
    generate_3question_archetypes()
    save_3_question_agents()
    update_prompt_archetypes()