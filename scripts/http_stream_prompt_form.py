import os, json

import httpx


prompt_flow_id = 1

inference_request = {
    "model_name":"gpt-3.5-turbo",
    "input_text":f"What are 3 jokes about {subject}",
    "api_key":os.environ.get("OPENAI_API_KEY"),
    "org_id":os.environ.get("OPENAI_ORG_KEY"),
    "generation_cfg":None,
}



ENDPOINT_URL = "http://0.0.0.0:8000/openai_streaming"

#from inference_request import InferenceRequest

print(inference_request)

msg = ""

with httpx.stream('POST', ENDPOINT_URL, json=inference_request) as r:
    for chunk in r.iter_raw():  
        msg += chunk.decode("utf-8")

        print(msg)