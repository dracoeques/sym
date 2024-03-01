import re

from sym.modules.db.models import Prompt, PromptVariable, PromptVariableOption

def create_prompt_lib(session, payload):
    #pre-parse variables
    variables = []
    if "rawtext" in payload:
        variables = parse_promptlib_variables(payload["rawtext"])
        text = replace_with_var_name(payload["rawtext"])
        payload["text"] = text #add parsed text to prompt payload

    if "id" in payload:
        prompt_id = payload["id"]
        p = session.query(Prompt)\
            .filter(Prompt.id == prompt_id)\
            .first()
        if p is None:
            return None,"Error: Promptlib not found"
        #use from_dict to update any variables
        p.from_dict(payload)
    else:
        #create prompt 
        p = Prompt().from_dict(payload)
        session.add(p)
        session.commit()

    #add any variables / options
    if variables:
        prompt_variables = []
        for v in variables:
            variable = PromptVariable().from_dict(v)
            session.add(variable)
            session.commit()
            options = []
            if "options" in v:
                for o in v["options"]:
                    pvo = PromptVariableOption()
                    pvo.value = o
                    pvo.label = o
                    pvo.prompt_variable_id = variable.id
                    session.add(pvo)
                    options.append(pvo)
                session.commit()
            variable.options = options
            prompt_variables.append(variable)
        p.variables = prompt_variables

    #final commit to set variables / options
    session.commit()

    return p, None

def parse_promptlib_variables(text):
    """ Given text, find all instances of {variables}
    
        Any options are expected in the format:
        {variable_name|option1,option2,option3}


        returns the prompt and a list of variables with options
    """
    pattern = r"\{([^}]+)\}"
    matches = re.findall(pattern, text)
    parsed_matches = []
    for match in matches:
        split_match = match.split("|")
        variable_name = split_match[0]
        options = split_match[1].split(",") if len(split_match) > 1 else []
        parsed_match = {"variable_name": variable_name, "options": options}
        parsed_matches.append(parsed_match)
    return parsed_matches

def replace_with_var_name(text):
    """ Given text, find all instances of {variables}
    
        Any options are expected in the format:
        {variable_name|option1,option2,option3}


        returns the prompt with just the variables
        eg: {variable_name}
    """
    pattern = r"\{([^}|]+)\|[^}]*\}"
    replaced_text = re.sub(pattern, r"{\1}", text)
    return replaced_text
