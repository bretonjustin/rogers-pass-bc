import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import rogers_pass_bc

app = FastAPI()

app.include_router(rogers_pass_bc.router)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    data = {
        "avalanche_web_link": "https://www.avalanche.ca/forecasts/a2a7748a-d376-45c9-b6aa-272df4c22d5d_b2a14eb464567902bcdf5b0cf1efe870416fee4de1d80d5b1f6d9cbc1b3bd73a",
    }
    return templates.TemplateResponse("page.html", {"request": request, "data": data})

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
    # exit the app clean
    exit(0)


