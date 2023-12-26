from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app.library import drivebc
from app.library.avalanche_canada import get_avalanche_forecast
from app.library.webcams import Webcam

AVALANCHE_LINK = "https://api.avalanche.ca/forecasts/:lang/products/point?lat=51.29998&long=-117.51866"
WEATHER_LINK = "https://dd.weather.gc.ca/citypage_weather/xml/HEF/s0000856_e.xml"
DRIVE_LINK = "https://api.open511.gov.bc.ca/events?area_id=drivebc.ca/3"
#DRIVE_LINK = "https://api.open511.gov.bc.ca/events?area_id=drivebc.ca/3&severity=MAJOR"

SPOTWX_LINK = "https://spotwx.com/products/grib_index.php?model=gem_glb_15km&lat=51.27545&lon=-117.52779&tz=America/Vancouver&label="

WEBCAMS = [
    Webcam("Rogers Pass Summit", 1.1, 2.2, 1330, "https://images.drivebc.ca/bchighwaycam/pub/cameras/101.jpg"),
    Webcam("Fidelity Snow Board", 1.1, 2.2, 1910, "https://www.pc.gc.ca/images/remotecamera/sarnif/fidelity/snowstake.jpg"),
    Webcam("Major Rogers snow board", 1.1, 2.2, 1368, "https://www.pc.gc.ca/images/remotecamera/sarnif/MajorRogers/Snowstake.jpg"),
    Webcam("Mount Abbott", 1.1, 2.2, 0, "https://www.pc.gc.ca/images/remotecamera/sarnif/Abbott/landscape.jpg?1703511925481"),
]

router = APIRouter(
    prefix="/rogers-pass",
    tags=["rogers-pass"],
)

templates = Jinja2Templates(directory="templates")
router.mount("/static", StaticFiles(directory="static"), name="static")


def get_router_prefix():
    return router.prefix

# Get rogers pass data
@router.get("/", response_class=HTMLResponse)
async def rogers_pass(request: Request):
    data = {
        "router_prefix": get_router_prefix(),
    }
    return templates.TemplateResponse("page.html", {"request": request, "data": data})


# Get rogers pass webcams
@router.get("/webcams", response_class=HTMLResponse)
async def rogers_pass_webcams(request: Request):
    data = {
        "webcams": WEBCAMS,
        "router_prefix": get_router_prefix(),
    }
    return templates.TemplateResponse("webcams.html", {"request": request, "data": data})


@router.get("/roads", response_class=HTMLResponse)
async def rogers_pass_roads(request: Request):
    events = drivebc.get_major_drivebc_events(DRIVE_LINK)
    data = {
        "events": events,
        "router_prefix": get_router_prefix(),
    }
    return templates.TemplateResponse("roads.html", {"request": request, "data": data})


# get avalanche forecast
@router.get("/avalanche", response_class=HTMLResponse)
async def rogers_pass_avalanche(request: Request):
    data = {
        "router_prefix": get_router_prefix(),
        "avalanche_web_link": get_avalanche_forecast(AVALANCHE_LINK),
    }
    return templates.TemplateResponse("avalanche.html", {"request": request, "data": data})


@router.get("/avalanche_canada", response_class=HTMLResponse)
async def rogers_pass_avalanche_canada(request: Request):
    modified_content = get_avalanche_forecast(AVALANCHE_LINK)
    return HTMLResponse(content=modified_content)
