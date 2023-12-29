import markdown
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from app import rogers_pass_bc

app = FastAPI()

app.include_router(rogers_pass_bc.router)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # redirect to rogers pass page
    return RedirectResponse(url="/rogers-pass")


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
    # exit the app clean
    exit(0)
