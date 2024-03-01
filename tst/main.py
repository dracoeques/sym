import os
import logging

import json
import time


from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.templating import Jinja2Templates



app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

