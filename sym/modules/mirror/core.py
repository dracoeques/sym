from sym.modules.db.models import *


def flow_status(profile_id=None, session=None, payload=None):
    
    if profile_id is None:
        raise Exception("Profile Id cannot be none")
    
    flows = payload
    for k in flows:
        flow = flows[k]
        flowId = flow["flowId"]

        #check for an existing flow run for this flow and profile
        flowRun = session.query(PromptRun)\
            .filter(PromptRun.id_prompt_flow == flowId)\
            .filter(PromptRun.id_profile == profile_id)\
            .filter(PromptRun.completed == True)\
            .order_by(PromptRun.created_on.desc())\
            .first()
        if flowRun:
            flows[k]["runId"] = flowRun.id
            flows[k]["completed"] = flowRun.completed
    return flows

def mirror_flow_status(profile_id=None, session=None):
    """ Based on this individuals current completions of these flows
        return the status and any previous flow run Ids for reference
    """
    if profile_id is None:
        raise Exception("Profile Id cannot be none")

    flows = default_mirror_flows()

    for k in flows:
        flow = flows[k]
        flowId = flow["flowId"]

        #check for an existing flow run for this flow and profile
        flowRun = session.query(PromptRun)\
            .filter(PromptRun.id_prompt_flow == flowId)\
            .filter(PromptRun.id_profile == profile_id)\
            .filter(PromptRun.completed == True)\
            .order_by(PromptRun.created_on.desc())\
            .first()
        if flowRun:
            flows[k]["runId"] = flowRun.id
            flows[k]["completed"] = flowRun.completed

    return flows


def default_mirror_flows():

    flows = {
        "values":{
            "flowId":201,
            "runId":None,
            "completed":False,
        },
        "interests":{
            "flowId":200,
            "runId":None,
            "completed":False,
        },
        "personality":{
            "flowId": 196,
            "runId":None,
            "completed":False,
        },
        "opportunity":{
            "flowId":202,
            "runId":None,
            "completed":False,
        }
    }

    return flows

