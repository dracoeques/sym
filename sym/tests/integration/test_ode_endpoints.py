
import os
import requests
import json

sym_api_key = os.environ.get("SYM_API_KEY")

endpoint = "http://sym.ai/api/ode/default-feed"
#endpoint = "http://dev.sym.ai/api/ode/default-feed"
#endpoint = "http://localhost:8000/api/ode/default-feed"


headers = {"X-API-KEY":sym_api_key}
r = requests.get(endpoint, headers=headers)
feed = r.json()
print(feed)
feed_id = feed["id"]

#now get items from the feed
endpoint = f"http://localhost:8000/api/ode/feed/{feed_id}/items"
headers = {"X-API-KEY":sym_api_key}
r = requests.get(endpoint, headers=headers)
print(json.dumps(r.json(), indent=2))