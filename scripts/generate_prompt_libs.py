import openai
import json
import re
from sym.modules.promptlibs.core import create_prompt_lib
from sym.modules.db.db import *
from sym.modules.db.models import *


from prompt_openai import run_openai_prompt

def build_prompt_libs():

    eng,fact = local_session()
    session = fact()


    with open("data/prompt_libs_main.json") as f:
        libs = json.load(f)

    with open("data/archetype_decks.json") as f:
        archetypes = json.load(f)

    added = False

    for cat in archetypes:
        for deck_num,config in enumerate(archetypes[cat]):
            sub = config["name"]

            if cat not in libs:
                libs[cat] = {}
            if sub not in libs[cat]:
                libs[cat][sub] = []

            column = {
                "name": "3 Prompt Libs",
                "key": "prompt_libs",
                "items": [],
            }



            if len(libs[cat][sub]) >= 3:
                continue

            
            
            #check for existing prompt libs
            if len(config["columns"]) < 2:
                #add a new prompt lib
                for prompt in prompt_prompt_libs(cat, sub):
                    name = f"""{cat} {sub} Generated Prompt Lib """
                    payload = {
                        "name":name,
                        "rawtext":prompt,
                        "category":cat,
                        "subcategory":sub,
                    }
                    p, err = create_prompt_lib(session, payload)
                    print(f"Created prompt: {p.id}")
                    #update our prompt libs json
                    libs[cat][sub].append(p.to_dict())
                    
                    added = True
                    #update the column
                    column["items"].append({
                        "id":p.id,
                        "key":"prompt_lib",
                        "name":name,
                    })
                archetypes[cat][deck_num]["columns"].append(column)


            else:
                
                if config["columns"][1]["key"] != "prompt_libs":

                    #replace existing column with prompt libs
                    for prompt in prompt_prompt_libs(cat, sub):
                        name = f"""{cat} {sub} Generated Prompt Lib """
                        payload = {
                            "name":name,
                            "rawtext":prompt,
                            "category":cat,
                            "subcategory":sub,
                        }
                        p, err = create_prompt_lib(session, payload)
                        print(f"Created prompt: {p.id}")
                        #update our prompt libs json
                        libs[cat][sub].append(p.to_dict())
                        
                        added = True
                        #update the column
                        column["items"].append({
                            "id":p.id,
                            "key":"prompt_lib",
                            "name":name,
                        })
                    archetypes[cat][deck_num]["columns"][1] = column

        
    with open("data/prompt_libs_main.json", "w") as f:
        json.dump(libs, f, indent=2)
    
    with open("data/archetype_decks.json", "w") as f:
        json.dump(archetypes, f, indent=2)
        

def prompt_prompt_libs(category, subcategory):
    """ Create prompt libs from a query to openai"""

    prompt = f"""Create three possible prompts to use as a starting point for common {category} {subcategory} tasks, just include a number and the prompt without preamble"""

    system = f"""You create common starting points for prompts (like mad libs) to solve specific tasks 
         just include a number and the prompt without preamble
        
        for example: 
            
        Input: Create three possible prompts to use as a starting point for common marketing email tasks
        Output:
        1. Unveiling Our Newest [Product/Feature]! 🌟 Step inside for a first look and an exclusive offer just for our valued subscribers.

        2. Here's Your [Month/Season] Round-up! 📅 Catch up on the latest in [Industry/Topic], plus a special preview of what's on the horizon.

        3. Long Time No See! 🕰️ We noticed you've been away. To welcome you back, here's a special [discount/gift] tailored just for you. Explore now!

        Input: Create three possible prompts to use as a starting point for common coaching decision tasks
        Output:
        1. I\u2019m deciding between [traveling to destination eg: Seoul,New York,Paris]. Provide research and insights to help me make a decision.

        2. Summarize the pros and cons between [the keto diet] and [the paleo diet].

        3. I am deciding [what university to go to for my master's]. Tell me what you do if you were in my situation.
    """

    msg,completion = run_openai_prompt(prompt, system=system)
    items = parse_numbered_items(msg)
    
    return items



def parse_numbered_items(s):
    # Find all items following a number and a dot, capturing the item content
    pattern = r'\d+\.\s*([^\n]+)'
    return re.findall(pattern, s)


if __name__ == "__main__":
    build_prompt_libs()
    #prompt_prompt_libs("learn", "science")