import os
import logging
import asyncio, threading
import json
import time

from pydantic import BaseModel
import async_timeout
import asyncio
from typing import Optional


from sqlalchemy import create_engine, text
from collections import defaultdict


from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from fastapi import BackgroundTasks, WebSocket, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Depends, HTTPException, status
from fastapi.templating import Jinja2Templates

from fastapi_utils.tasks import repeat_every

from starlette.responses import StreamingResponse

import openai


from sym.modules.db.db import *
from sym.modules.db.models import *

from sym.modules.utils.utils import render_template, render_resource, redirect_to_bucket, redirect_to_frontend_bucket, render_from_frontend_bucket
from sym.modules.utils.utils import authenticate_user, InvalidAuth, user_can_read_project, user_can_update_project, user_can_create_project, user_can_delete_project
from sym.modules.auth.profile import get_profiles, get_default_profile
from sym.modules.personalization.relevant_context import save_user_response_ranking, get_relevant_profile_datums, relevant_datums_evaluator, relevant_profile_context_v1

from sym.modules.misc.love_coach_pdf import create_love_coach_pdf, get_love_coach_pdf_url

from sym.modules.autolib.main import create_model_record, update_model_record, convert_model2dict

from sym.modules.promptflow.core import PromptFlowRunner

from sym.modules.promptlibs.core import create_prompt_lib

from sym.modules.promptdecks.archetypes import read_archetype_categories, format_archetype_categories_d3, format_archetype_categories_flower

from sym.modules.promptflows.main import websocket_run, save_prompt_flow, form_run

from sym.modules.personalization.kv_etl import main as profile_kev_value_etl, run_kv_etl_async

from sym.modules.discovery.core import get_discovery_feed, topic_discovery, topics_discovery, create_or_update_discovery_feed, get_default_discovery_feed, get_discovery_feed_items, get_feed_items, convert_feed_items_to_json
from sym.modules.discovery.core import chat_with_media_item
from sym.modules.discovery.ode_chat_interface import ODE_Chat
from sym.modules.discovery.core import get_personalized_feed_items

from sym.modules.mirror.core import mirror_flow_status, flow_status

from sym.modules.ode import ode_websocket_run

app = FastAPI()

app.mount("/static", StaticFiles(directory="sym/static"), name="static")

openai.organization = os.getenv("OPENAI_ORG_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

origins = [
    "https://sym.ai",
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:5174",
    "https://www.heartcoach.com",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

## FRONT END

vitetemplate = Jinja2Templates(directory="sym/vitedist")

@app.get("/", response_class=HTMLResponse)
def front(request: Request):
    #return render_from_frontend_bucket("index.html")
    return vitetemplate.TemplateResponse("index.html", {"request": request})

@app.get("/app/", response_class=HTMLResponse)
def front_app(request: Request):
    #return render_from_frontend_bucket("index.html")
    return vitetemplate.TemplateResponse("index.html", {"request": request})

@app.get("/app/{path}", response_class=HTMLResponse)
def front_redirect(request: Request, path: str):
    #TODO: match all urls, or just serve frontend from s3
    return vitetemplate.TemplateResponse("index.html", {"request": request})

@app.get("/app/{path}/{path2}", response_class=HTMLResponse)
def front_redirect2(request: Request, path: str, path2: str):
    #TODO: match all urls, or just serve frontend from s3
    return vitetemplate.TemplateResponse("index.html", {"request": request})

@app.get("/app/{path}/{path2}/{path3}", response_class=HTMLResponse)
def front_redirect3(request: Request, path: str, path2: str, path3: str):
    #TODO: match all urls, or just serve frontend from s3
    #... lmao
    return vitetemplate.TemplateResponse("index.html", {"request": request})


#note: /assets is the default path used by VITE to load js / css
# @app.get('/assets/{resource}')
# def assets(resource):
#     path = "assets/"+resource
#     #print(f"Loading path: {path}")
#     redirect_url = redirect_to_frontend_bucket(path)
#     return RedirectResponse(url=redirect_url)
app.mount("/assets", StaticFiles(directory="sym/vitedist/assets", html=True), name="vite-assets")


#SCHEDULED TASKS
#TODO: Make these tasks async
# @app.on_event("startup")
# @repeat_every(seconds=60 * 60)  # 1 hour
# def process_key_values() -> None:
#     try:
#         profile_kev_value_etl()
#     except Exception as e:
#         logging.exception(e)
    

#BACK END ROUTES

@app.get("/status")
def read_root():
    return {"Hello": "Worlds"}


@app.post('/api/users/login')
async def users_login(request: Request):

    payload = await request.json()
    engine,session_factory = local_session()
    session = session_factory()
    if 'email' not in payload or 'password' not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            
        )
    email = payload["email"]
    u = session.query(User).filter(User.email == email).first()
    if not u or not u.check_password(payload["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            
        )
    t = Token().generate(u)
    try:
        session.add(t)
        session.commit()
    except Exception as e:
        logging.exception(e)
    response_json = t.to_dict()
    return response_json


@app.get('/api/users/me')
def users_me(request: Request):

    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        print("Unauthorized", ia)
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            #headers={"WWW-Authenticate": "Basic"},
        )
    
    

    return u.to_dict()

@app.get('/api/users/profiles')
def users_me(request: Request):

    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        print("Unauthorized", ia)
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            #headers={"WWW-Authenticate": "Basic"},
        )
    
    profiles = get_profiles(session, u.id)
    if profiles is None:
        return {"profiles":[]}
    return {"profiles":[x.to_dict() for x in profiles]}



#################### 
# ODE
####################


@app.get("/api/ode-ws")
async def ode_ws(
        websocket: WebSocket):
    await websocket.accept()

    engine,session_factory = local_session()
    session = session_factory()

    while True:
        rawmsg = await websocket.receive_text()

        ode_chat = ODE_Chat()
        ode_chat.rawmsg = rawmsg
        ode_chat.ws = websocket
        ode_chat.session = session

        #TODO: catch error here if auth fails
        await ode_chat.init()
        await ode_chat.authenticate()

        response_payload = {}
        await websocket.send_text(json.dumps(response_payload))


@app.get('/api/ode/default-feed')
async def handle_default_discovery_feed(
        request: Request,
    ):
    """ Get the default discovery feed for the user
    this is the feed that is shown when the user logs in

    Args:
        request (Request): The request object containing user information.

    Returns:
        dict: The default discovery feed as a dictionary.
    """

    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        print("Unauthorized", ia)
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            #headers={"WWW-Authenticate": "Basic"},
        )
    
    #TODO: set default feed in user creation step
    
    p = get_default_profile(session, u.id)
    
    feed,err = get_default_discovery_feed(session=session, profile_id=p.id)
    return feed.to_dict()

@app.get('/api/ode/feed/{feed_id}/items')
async def handle_ode_read_feed(
        request: Request,
        feed_id:int,
        page:int=1,
        limit:int=10,
        after_id:int=None,
        before_id:int=None,
        sort_by:str="personalization",
    ):
    """ Get feed items for a specific feed

    This function handles the request to retrieve feed items for a specific feed.
    
    Parameters:
        request (Request): The request object containing the HTTP request information.
        feed_id (int): The ID of the feed for which to retrieve the items.
        page (int, optional): The page number of the feed items to retrieve. Defaults to 1.
        limit (int, optional): The maximum number of feed items to retrieve per page. Defaults to 20.
    
    Returns:
        List[FeedItem]: A list of feed items for the specified feed as JSON
    
    Raises:
        HTTPException: If the user is not authorized or if there is an error retrieving the feed items.
    """
    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        print("Unauthorized", ia)
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            #headers={"WWW-Authenticate": "Basic"},
        )
    
    items,err = get_feed_items(
        session=session, 
        feed_id=feed_id, 
        page=page, 
        limit=limit,
        after_id=after_id,
        before_id=before_id,
        sort_by=sort_by,
    )

    if err:
        raise HTTPException(
            status_code=500,
            detail=err,
        )
    
    response_payload = convert_feed_items_to_json(items)
    

    return response_payload




#################### 
# Prompt Flows
####################



@app.post('/api/promptflow')
async def create_promptflow(request: Request):
    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        print("Unuathorized", ia)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
           
        )
    
    #get payload
    payload = await request.json()

    #TODO: check if user can edit / save this flow
    pf = save_prompt_flow(session, payload)

    

    return convert_model2dict(pf)


@app.get('/api/promptflow/{item_id}')
async def get_promptflow(
        item_id:int,
        request: Request,
    ):
    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        print("Unuathorized", ia)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
           
        )
    
    #get promptflow
    pf = session.query(PromptFlow)\
            .filter(PromptFlow.id == item_id).first()
    if pf is None:
        raise HTTPException(
                status_code=404,
                detail=f"Prompt flow with id: {item_id} not found",
            
            )

    return convert_model2dict(pf)


@app.get('/api/promptflow-categories/')
async def get_promptflow_categories(
        request: Request,
    ):
    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        print("Unuathorized", ia)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
           
        )
    #get all categories for prompts
    #organized by subcategories
    return {"error":"not implemented"}
    
@app.get('/api/promptflows/')
async def get_promptflows(
        request: Request,
    ):
    engine,session_factory = local_session()
    session = session_factory()

    #TODO: debug auth
    # try:
    #     u = authenticate_user(session, request)
    # except InvalidAuth as ia:
    #     print("Unuathorized", ia)
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid token",
           
    #     )

    #get promptflows
    flow_records = session.query(PromptFlow)\
        .filter(PromptFlow.name != None)\
        .filter(PromptFlow.hidden != True)\
        .all()

    flows = []
    for flow in flow_records:
        flows.append(flow.to_dict())
    
    return {
        "flows":flows,
    }

@app.get('/api/promptflow-list/')
async def get_promptflow_list(
        request: Request,
    ):
    engine,session_factory = local_session()
    session = session_factory()

    #TODO: debug auth
    # try:
    #     u = authenticate_user(session, request)
    # except InvalidAuth as ia:
    #     print("Unuathorized", ia)
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid token",
           
    #     )

    #get promptflows
    flow_records = session.query(PromptFlow)\
        .filter(PromptFlow.name != None)\
        .filter(PromptFlow.hidden != True)\
        .all()

    flows = []
    for flow in flow_records:
        flows.append({
            "title":flow.name,
            "id":flow.id,
            "category":flow.category,
            "subcategory":flow.subcategory,
        })
    
    return {
        "flows":flows,
    }


@app.get('/api/promptlib/{item_id}')
async def get_promptlib(
    item_id:int,
    request: Request,
    
    ):
    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        print("Unuathorized", ia)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
           
        )
    #get prompt - and any variables

    prompt = session.query(Prompt)\
        .filter(Prompt.id == item_id)\
        .first()
    if prompt is None:
        raise HTTPException(
            status_code=404,
            detail=f"Prompt not found: {item_id}",
        )

    return prompt.to_dict()


@app.post('/api/promptlib')
async def post_promptlib(
    request: Request,
    
    ):
    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        print("Unuathorized", ia)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
           
        )
    #get payload
    payload = await request.json()

    p,err = create_prompt_lib(payload)

    if err:
        raise HTTPException(
                status_code=500,
                detail=err,
            )
    return p.to_dict()


@app.get('/api/prompt-view-category/')
async def get_prompt_view_category(
        request: Request,
        category:str=None,
        subcategory:str=None,
    ):
    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        print("Unuathorized", ia)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
           
        )

    if not category:
        raise HTTPException(
            status_code=400,
            detail="No category provided",   
        )
    else:
        category = category.lower().strip()
    if not subcategory:
        raise HTTPException(
            status_code=400,
            detail="No subcategory provided",   
        )
    else:
        subcategory = subcategory.lower().strip()

    #get prompt flows 
    flows = session.query(PromptFlow)\
        .filter(PromptFlow.category.ilike(category))\
        .filter(PromptFlow.subcategory.ilike(subcategory))\
        .filter(PromptFlow.hidden != True)\
        .all()

    #get prompts
    prompts = session.query(Prompt)\
        .filter(Prompt.category.ilike(category))\
        .filter(Prompt.subcategory.ilike(subcategory))\
        .all()


    return {
        "category":category,
        "subcategory":subcategory,
        "flows":[x.to_dict() for x in flows],
        "prompts":[x.to_dict() for x in prompts]
    }


#circle view
@app.get('/api/circle-categories')
async def get_circle_categories(
        request: Request,
    ):
    engine,session_factory = local_session()
    session = session_factory()
    # try:
    #     u = authenticate_user(session, request)
    # except InvalidAuth as ia:
    #     print("Unuathorized", ia)
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid token",
           
    #     )

    #get unique categories and then the count of each item in each subcategory
    # Define the SQL statement
    sql = text("""
        SELECT LOWER(category) as category, LOWER(subcategory) as subcategory, COUNT(*) as count
        FROM (
            SELECT LOWER(category) as category, LOWER(subcategory) as subcategory
            FROM prompts
            UNION ALL
            SELECT LOWER(category) as category, LOWER(subcategory) as subcategory
            FROM prompt_flows
        ) as combined
        GROUP BY LOWER(category), LOWER(subcategory)
        ORDER BY LOWER(category), LOWER(subcategory)
    """)

    # Execute the SQL statement
    result = session.execute(sql)

    # Parse the results into a nested dict
    data = defaultdict(dict)

    for row in result:
        category,subcategory,count = row[0],row[1],row[2]
        data[category][subcategory] = count

    # If you want a plain dict instead of a defaultdict, you can convert it
    data = dict(data)

    #re-package in the format required for front end
    #bit of a strange structure needed:
    # data = {
    #         name:"topics",
    #         children:[
    #             {
    #                 name:"Arts",
    #                 children:[
    #                     {
    #                         name:"Art History",
    #                         prompt_id:1,
    #                         children:[
    #                             {
    #                                 name:"Art History",
    #                                 value:20,
    #                             }
    #                         ]                     
    #                     },
    #                     {
    #                         name:"Art Technique",
    #                         prompt_id:2,
    #                         children:[
    #                             {
    #                                 name:"Art Technique",
    #                                 value:10,
    #                             }
    #                         ]                
    #                     },
    d = {
        "name":"topics",
        "children":[],
    }
    topics = []
    for category in data:

        if category is None:
            continue

        topic = {
            "name":category,
            "children":[],
        }
        subtopics = []
        for subcategory in data[category]:

            if subcategory is None:
                continue
            sub = {
                "name":subcategory,
                "url":f"/app/prompt-view-category/{category}/{subcategory}",
                "children":[
                    {
                        "name":subcategory,
                        "value":data[category][subcategory],
                    }
                ],
            }
            subtopics.append(sub)
        topic["children"] = subtopics
        topics.append(topic)
    d["children"] = topics
    return d

#archetype / flower view 
@app.get('/api/archetype-categories')
async def get_archetype_categories(
        request: Request,
    ):
    engine,session_factory = local_session()
    session = session_factory()

    categories = read_archetype_categories(session)
    categories_d3 = format_archetype_categories_d3(categories)
    return categories_d3
    #return {}

@app.get('/api/flower-categories')
async def get_archetype_categories(
        request: Request,
    ):
    engine,session_factory = local_session()
    session = session_factory()

    categories = read_archetype_categories(session)
    categories_flower = format_archetype_categories_flower(categories)
    return categories_flower


#WEBSOCKET LOGIC

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()

        #
        recieved = json.loads(data)
        print(recieved)

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": recieved["context"]},
                {"role": "user", "content": recieved["prompt"]}
            ]
        )


        message = completion.choices[0].message

        temp_id = int(time.time())
        payload = {
            "text":message["content"],
            "context": recieved["context"],
            "prompt": recieved["prompt"],
            "id":temp_id,
        }
        print(payload)
        await websocket.send_text(json.dumps(payload))



@app.websocket("/ws2")
async def websocket_endpoint2(websocket: WebSocket):
    engine,session_factory = local_session()
    session = session_factory()
    
    await websocket.accept()
    MAX_MESSAGES = 5000
    CURRENT_MESSAGE = 0
    while True:
        data = await websocket.receive_text()

        #load the promptFlow
        try:        
            pf = PromptFlowRunner()
            pf.session=session
            pf.rawmsg=data
            pf.init()
        except Exception as e:
            payload = {
                "error":str(e),
            }
            logging.exception(e)
            await websocket.send_text(json.dumps(payload))
            break

        #run the next step, stream responses
        try:
            async for envelope in pf.next():
                resp = await envelope.to_dict()
                
                await websocket.send_text(json.dumps(resp))
                # CURRENT_MESSAGE += 1
                # if CURRENT_MESSAGE >= MAX_MESSAGES:
                #     break
        except Exception as e:
            payload = {
                "error":str(e),
            }
            logging.exception(e)
            await websocket.send_text(json.dumps(payload))
            break


@app.websocket("/api/ode/ws")
async def websocket_endpoint(websocket: WebSocket):
    engine,session_factory = local_session()
    session = session_factory()
    _ = await ode_websocket_run(session, websocket)
    
        

def async_wrap_iter(it):
    """Wrap blocking iterator into an asynchronous one"""
    loop = asyncio.get_event_loop()
    q = asyncio.Queue(1)
    exception = None
    _END = object()

    async def yield_queue_items():
        while True:
            next_item = await q.get()
            if next_item is _END:
                break
            yield next_item
        if exception is not None:
            # the iterator has raised, propagate the exception
            raise exception

    def iter_to_queue():
        nonlocal exception
        try:
            for item in it:
                # This runs outside the event loop thread, so we
                # must use thread-safe API to talk to the queue.
                asyncio.run_coroutine_threadsafe(q.put(item), loop).result()
        except Exception as e:
            exception = e
        finally:
            asyncio.run_coroutine_threadsafe(q.put(_END), loop).result()

    threading.Thread(target=iter_to_queue).start()
    return yield_queue_items()

async def stream_openai(prompt):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'user', 'content': prompt}
        ],
        temperature=0,
        stream=True  # this time, we set stream=True
    )

    async for chunk in async_wrap_iter(response):
        #print(chunk)
        yield chunk['choices'][0]["delta"]["content"]
        



@app.websocket("/wstest")
async def websocket_endpoint(websocket: WebSocket):
    print("wstest")
    await websocket.accept()
    print("wstest open")
    example = "Describe the steps involved with creating a self sustaining automated organic farm that get's alot of shade but is near a river, include examples for what crops to grow and what automations to use"
    
    while True:
        
        data = await websocket.receive_text()

        print("Recieved:", data)

        # for chunk in data.split(" "):
        #     await websocket.send_text(chunk)
        #     await asyncio.sleep(0.1)

        # async for chunk in stream_openai_requests(data):
        #     #print(chunk)
        #     await websocket.send_text(chunk)

        async for chunk in stream_openai(data):
            #print(chunk)
            await websocket.send_text(chunk)



@app.websocket("/ws3")
async def websocket_endpoint3(websocket: WebSocket):
    engine,session_factory = local_session()
    session = session_factory()
    
    await websocket.accept()
    MAX_MESSAGES = 5000
    CURRENT_MESSAGE = 0
    while True:
        data = await websocket.receive_text()

        #load the promptFlow
        try:        
            pf = PromptFlowRunner()
            pf.session=session
            pf.rawmsg=data
            pf.init()
        except Exception as e:
            payload = {
                "error":str(e),
            }
            logging.exception(e)
            await websocket.send_text(json.dumps(payload))
            break

        #run the next step, stream responses
        try:
            async for envelope in pf.next():
                resp = await envelope.to_dict()
                
                await websocket.send_text(json.dumps(resp))
                # CURRENT_MESSAGE += 1
                # if CURRENT_MESSAGE >= MAX_MESSAGES:
                #     break
        except Exception as e:
            payload = {
                "error":str(e),
            }
            logging.exception(e)
            await websocket.send_text(json.dumps(payload))
            break


## PromptFlows v2
@app.websocket("/ws-v2")
async def websocket_endpoint_pf2(websocket: WebSocket):
    engine,session_factory = local_session()
    session = session_factory()
    
    await websocket.accept()
    MAX_MESSAGES = 5000
    CURRENT_MESSAGE = 0

    await websocket_run(session, websocket)


### Future coach / AI products related logic

@app.post('/api/prompt-flow-form/{flow_id}')
async def handle_prompt_form(
        request: Request,
        flow_id: int,

    ):

    payload = await request.json()
    engine,session_factory = local_session()
    session = session_factory()

    #TODO:
    #run a prompt flow all at once
    await form_run(session, flow_id=flow_id, payload=payload)




@app.get('/api/client-getting-secrets')
async def get_prompt_form(
        request: Request,

    ):

    payload = await request.json()
    engine,session_factory = local_session()

    #TODO:
    #run a prompt flow all at once

@app.post('/api/client-getting-secrets')
async def handle_prompt_form(
        request: Request,

    ):

    payload = await request.json()
    engine,session_factory = local_session()

    #TODO:
    #run a prompt flow all at once



## Prompt Decks
@app.get('/api/prompt-deck/{item_id}')
async def get_prompt_deck(
        item_id:int,
        request: Request,
    ):
    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        print("Unuathorized", ia)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    #get prompt deck
    p = session.query(PromptDeck)\
            .filter(PromptDeck.id == item_id).first()
    if p is None:
        raise HTTPException(
                status_code=404,
                detail=f"Prompt deck with id: {item_id} not found",
            
            )

    return p.to_dict()


# Personalization

@app.post("/api/run_personal_kv_etl/")
async def post_run_kv_etl(request: Request):

    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    #get default profile id
    p = get_default_profile(session, u.id)

    _ = await run_kv_etl_async(id_profile=p.id)

    return {
        "kv_etl":"success",
        "new_items":0,
    }




@app.get('/api/get_personal_kv/')
async def get_relevant_kv(
        request: Request,
    ):
    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    #get default profile id
    p = get_default_profile(session, u.id)

    #use query params
    params = request.query_params

    limit = 20
    if "limit" in params:
        limit = params["limit"]
    
    topic = None
    if "topic" in params:
        topic = params["topic"]
    else:
        raise HTTPException(
            status_code=400,
            detail="Error: Topic query parameter must be provided",
        )

    
    evaluator_datums,t,context_response = relevant_profile_context_v1(
            topic, 
            id_profile=p.id, 
            limit=limit, 
            session=session)

    return {
        "topic":topic,
        "context_response":context_response,
        "context":t.to_dict(),
        "evaluator_datums":[d.to_dict() for d in evaluator_datums],
    }

@app.post('/api/vote_personal_kv/')
async def vote_relevant_kv(
        request: Request,

    ):

    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    #get default profile id
    p = get_default_profile(session, u.id)

    payload = await request.json()

    #get context text used in this query
    id_text = None
    if "id_text" in payload:
        id_text = payload["id_text"]
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid payload, id_text must be provided",
        )
    
    #get the profile datum being ranked
    if "id_profile_datum" in payload:
        id_profile_datum = payload["id_profile_datum"]
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid payload, id_profile_datum must be provided",
        )

    #get the value (upvote / downvote)
    liked = True
    if "liked" in payload:
        try:
            liked = bool(payload["liked"])
        except Exception as e:
            raise HTTPException(
            status_code=400,
            detail="Invalid liked value, must be true or false",
        )
    
    #save the response
    r = save_user_response_ranking(
        session, 
        id_text, 
        id_profile_datum, 
        p.id, 
        liked=liked)
    
    return r.to_dict()




@app.post('/api/discover/{item_id}')
async def discover_interaction(
        request: Request,
        item_id:int,
        page: int = 1,
    ):

    engine,session_factory = local_session()
    session = session_factory()
    
    # try:
    #     u = authenticate_user(session, request)
    # except InvalidAuth as ia:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid token",
    #     )
    
    # #get default profile id
    # p = get_default_profile(session, u.id)

    #TODO: save media_interaction
    return {"error":"Not implemented"}

@app.get('/api/discover-topics')
async def get_discovery_topics(
        request: Request,
        topics:str="",
        limit:int=10,
    ):

    engine,session_factory = local_session()
    session = session_factory()
    
    # try:
    #     u = authenticate_user(session, request)
    # except InvalidAuth as ia:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid token",
    #     )
    
    # #get default profile id
    # p = get_default_profile(session, u.id)

    #TODO: save mediat_interaction
    print(topics)
    topic_list = topics.split(",")

    items = topics_discovery(topic_list, session=session, topic_limit=limit)

    return [x.to_dict() for x in items]


@app.get("/api/discovery-feed/{feed_id}")
async def read_discovery_feed(
        request: Request,
        feed_id: int,
    ):
    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    #get default profile id
    p = get_default_profile(session, u.id)

    feed, err = get_discovery_feed(feed_id, session=session)

    if err:
        raise HTTPException(
            status_code=500,
            detail=err,
        )

    return feed.to_dict()

@app.post("/api/discovery-feed")
async def create_discovery_feed(
        request: Request,
    ):

    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    #get default profile id
    p = get_default_profile(session, u.id)

    payload = await request.json()

    #get context used in this request
    feed_id = None
    if "id" in payload:
        feed_id = payload["id"]
    
    topics = []
    if "topics" in payload:
        topics = payload["topics"]
    
    name = None
    if "name" in payload:
        name = payload["name"]
    
    description = None
    if "description" in payload:
        description = payload["description"]
    
    feed,err = create_or_update_discovery_feed(
        feed_id=feed_id,
        profile_id=p.id, 
        session=session, 
        topics=topics,
        name=name,
        description=description)

    if err:
        raise HTTPException(
            status_code=500,
            detail=err,
        )

    return feed.to_dict()

@app.get("/api/discovery-feed-items/{feed_id}")
async def read_discovery_feed_items(
        request: Request,
        feed_id: int,
        page: int =1,
        per_topic_limit=10, 
        max_embedding_distance=0.5, 

    ):
    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    #get default profile id
    p = get_default_profile(session, u.id)

    items, err = get_discovery_feed_items(
        feed_id, 
        page=page, 
        per_topic_limit=per_topic_limit, 
        max_embedding_distance=max_embedding_distance,
        session=session)

    if err:
        raise HTTPException(
            status_code=500,
            detail=err,
        )

    return items


@app.get("/api/personalized-feed-items/{feed_id}")
async def read_personalized_feed_items(
        request: Request,
        feed_id: int,
        page: int =1,
        per_topic_limit=10, 
        max_embedding_distance=0.5, 

    ):
    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    #get default profile id
    p = get_default_profile(session, u.id)

    items, err = get_personalized_feed_items(
        feed_id, 
        #id_profile=p.id,
        page=page, 
        per_topic_limit=per_topic_limit, 
        max_embedding_distance=max_embedding_distance,
        session=session)

    if err:
        raise HTTPException(
            status_code=500,
            detail=err,
        )

    return items


@app.post("/api/chat-with-media-item")
async def post_chat_with_media_item(
        request: Request,
    ):

    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    #get default profile id
    p = get_default_profile(session, u.id)

    #
    payload = await request.json()
    

    prompt = payload["prompt"]
    id_media_item = payload["id_media_item"]
    messages = payload["messages"]

    text = await chat_with_media_item(
        prompt, 
        id_media_item, 
        session=session, 
        id_profile=p.id,
        messages=messages)

    return {
        "response":text,
    }



### MIRROR FLOW ###
@app.post("/api/flow-status")
async def get_flow_status(
        request: Request,
    ):

    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    #get default profile id
    p = get_default_profile(session, u.id)

    #
    payload = await request.json()

    flows = flow_status(profile_id=p.id, session=session, payload=payload)
    return flows


@app.post("/api/flow-reset-completed-status")
async def reset_flow_completed_status(
        request: Request,
    ):

    engine,session_factory = local_session()
    session = session_factory()
    try:
        u = authenticate_user(session, request)
    except InvalidAuth as ia:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    #TODO: reset specific flow runs for this user based on the payload to 
    #not show as not completed

    #get default profile id
    p = get_default_profile(session, u.id)

    #
    flows = await request.json()

    return {"error":"Not implemented"}

GENERATION_TIMEOUT_SEC = 180

async def stream_generator(subscription):
    async with async_timeout.timeout(GENERATION_TIMEOUT_SEC):
        try:
            async for chunk in subscription:
                msg = chunk.choices[0].delta.content or ""
                yield msg
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Stream timed out")



class InferenceRequest(BaseModel):
    model_name: str
    input_text: str 
    api_key: Optional[str]
    org_id: Optional[str] = None
    generation_cfg: Optional[dict] = None

@app.post(f"/openai_streaming")
async def openai_streaming(request: InferenceRequest) -> StreamingResponse: 
    
    messages = [
        {
            "role":"user",
            "content":request.input_text,
        }
    ]

    try:    

        client = openai.AsyncOpenAI(
            # This is the default and can be omitted
            api_key=request.api_key,
            organization=request.org_id,
        )

        stream = await client.chat.completions.create(
            model=request.model_name,
            messages=messages,
            stream=True,
            #**request.generation_cfg
        )

        return StreamingResponse(stream_generator(stream),
                                media_type='text/event-stream')
    except openai.OpenAIError as e:
        logging.exception(e)
        raise HTTPException(status_code=500, detail='OpenAI call failed')
    

# LOVE COACH
    
@app.post("/love_coach_type")
async def love_coach_type(request: Request, background_tasks: BackgroundTasks):

    payload = await request.json()
    background_tasks.add_task(create_love_coach_pdf, payload)
    #response = await create_love_coach_pdf(payload)
    coach_pdf_url = await get_love_coach_pdf_url(payload)
    return {
        "message":"report creation started",
        "coach_pdf_url":coach_pdf_url,

    }

@app.post("/love_coach_type_sync")
async def love_coach_type_sync(request: Request):

    payload = await request.json()
    response = await create_love_coach_pdf(payload)
    return response

