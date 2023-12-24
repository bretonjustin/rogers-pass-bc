from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .library.helpers import *

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    data = {
        "avalanche_web_link": "https://www.avalanche.ca/forecasts/a2a7748a-d376-45c9-b6aa-272df4c22d5d_b2a14eb464567902bcdf5b0cf1efe870416fee4de1d80d5b1f6d9cbc1b3bd73a",
    }
    return templates.TemplateResponse("page.html", {"request": request, "data": data})


# Get rogers pass data
@app.get("/rogers-pass", response_class=HTMLResponse)
async def rogers_pass(request: Request):
    data = {
        
    }
    return templates.TemplateResponse("page.html", {"request": request, "data": data})
