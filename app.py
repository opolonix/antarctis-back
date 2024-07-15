from fastapi import FastAPI
from tools.alchemy import include_handlers

app = FastAPI()
include_handlers("handlers", app)