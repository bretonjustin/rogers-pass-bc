import threading

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

from app.prochaine_tempete import prochaine_tempete

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


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # redirect to rogers pass page
    return RedirectResponse(url="/rogers-pass")


@app.get("/static/{path:path}")
def static(path: str):
    path = f"static/{path}"
    return FileResponse(path, headers={"Cache-Control": "public, max-age=2592000"})  # 2592000 seconds is 30 days


# Catch-all route for handling 404 errors
@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    content = templates.TemplateResponse("404.html", {"request": request})
    return HTMLResponse(content=content.body, status_code=404)


if __name__ == "__main__":
    print("Starting prochaine tempete thread")
    prochaine_tempete_thread = threading.Thread(target=prochaine_tempete.prochaine_tempete())
    prochaine_tempete_thread.start()
    print("Started prochaine tempete thread")

    uvicorn.run(app, host="localhost", port=8000)
    # exit the app clean
    exit(0)
