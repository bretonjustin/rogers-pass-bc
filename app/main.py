
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware

from app import rogers_pass_bc

app = FastAPI()

origins = [
    "http://localhost",
    "https://rogers-pass-bc.herokuapp.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=500)

app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["rogers-pass-bc.herokuapp.com", "localhost"]
)

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
