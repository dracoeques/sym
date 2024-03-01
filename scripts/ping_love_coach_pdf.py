import requests
import json
payload = {
    "model":"gpt-4",
    "email":"blakedallen@gmail.com",
    "q1":1,
    "q2":0,
    "q3":0,
    "q4":1,
    "q5":1,
    "q6":0,
    "q7":1,
}

#url = "http://sym.ai/love_coach_type"
#url = "https://dev.sym.ai/love_coach_type_sync"
url = "http://localhost:8000/love_coach_type_sync"
#url = "http://localhost:8000/love_coach_type"

r = requests.post(url, json=payload)
print(r.status_code)
print(json.dumps(r.json(), indent=2))