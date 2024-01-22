import threading

from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app.library.avalanche_canada import get_avalanche_canada_weather_forecast, \
    get_latest_avalanche_canada_forecast, start_avalanche_canada_thread
from app.library.canada_park import get_latest_backcountry_access, \
    start_backcountry_access_thread
from app.library.drivebc import start_drivebc_thread, get_latest_drivebc_events
from app.library.environement_canada import get_ec_weather_forecast, get_latest_ec_forecast, start_ec_thread
from app.library.helpers import get_disclaimer
from app.library.webcams import Webcam

AVALANCHE_LINK = "https://api.avalanche.ca/forecasts/:lang/products/point?lat=51.29998&long=-117.51866"
WEATHER_LINK = "https://dd.weather.gc.ca/citypage_weather/xml/HEF/s0000856_e.xml"
DRIVE_LINK = "https://api.open511.gov.bc.ca/events?area_id=drivebc.ca/3"

WEATHER_STATIC_LINK = "https://api.avalanche.ca/weather/stations/98/measurements"

WINDY_LINK = "https://www.windy.com/51.302/-117.520?51.077,-117.377,8"

BACKCOUNTRY_AREA_DATA = "https://www.pc.gc.ca/apps/rogers-pass/data/publish-"
BACKCOUNTRY_AREA_MAP = "https://www.pc.gc.ca/apps/rogers-pass/"

SPOTWX_LINK = "https://spotwx.com/products/grib_index.php?model=gem_glb_15km&lat=51.27545&lon=-117.52779&tz=America/Vancouver&label="
SPOTWX_GFS_LINK = "https://spotwx.com/products/grib_index.php?model=gfs_pgrb2_0p25_f&lat=51.30123&lon=-117.52014&tz=America/Vancouver&label=Rogers%20Pass"

ROGERS_PASS_SUMMIT_DRIVE_WEBCAM = Webcam("Rogers Pass Summit", 1.1, 2.2, 1330, "https://images.drivebc.ca/bchighwaycam/pub/cameras/101.jpg")
WEBCAMS = [
    ROGERS_PASS_SUMMIT_DRIVE_WEBCAM,
    Webcam("Fidelity Snow Board", 1.1, 2.2, 1910, "https://www.pc.gc.ca/images/remotecamera/sarnif/fidelity/snowstake.jpg"),
    Webcam("Major Rogers snow board", 1.1, 2.2, 1368, "https://www.pc.gc.ca/images/remotecamera/sarnif/MajorRogers/Snowstake.jpg"),
    Webcam("Mount Abbott", 1.1, 2.2, 0, "https://www.pc.gc.ca/images/remotecamera/sarnif/Abbott/landscape.jpg"),
    Webcam("Mount Macdonald", -117.502752, 51.307452, 0, "https://www.pc.gc.ca/images/remotecamera/sarnif/Macdonald/landscape.jpg"),
]

AVALANCHE_SOURCE_NAME = "Avalanche Canada"
ROADS_SOURCE_NAME = "DriveBC"
WEATHER_SOURCE_NAME = "Environment Canada"
BACKCOUNTRY_AREA_SOURCE_NAME = "Parks Canada"
AVALANCHE_ORG_LINK = "https://www.avalanche.ca"
DRIVEBC_ORG_LINK = "https://www.drivebc.ca"
ENVIRONMENT_CANADA_ORG_LINK = "https://weather.gc.ca"
BACKCOUNTRY_AREA_SOURCE_LINK = "https://www.pc.gc.ca/apps/rogers-pass/"

router = APIRouter(
    prefix="/rogers-pass",
    tags=["rogers-pass"],
)

ROUTER_NAME = "Rogers Pass"

templates = Jinja2Templates(directory="templates")
router.mount("/static", StaticFiles(directory="static"), name="static")

print("Starting Rogers Pass threads")
# Start a thread to get the latest events from DriveBC
drivebc_thread = threading.Thread(target=start_drivebc_thread, args=(DRIVE_LINK,))
drivebc_thread.start()

avalanche_canada_thread = threading.Thread(target=start_avalanche_canada_thread, args=(AVALANCHE_LINK,))
avalanche_canada_thread.start()

backcountry_access_thread = threading.Thread(target=start_backcountry_access_thread, args=(BACKCOUNTRY_AREA_DATA,))
backcountry_access_thread.start()

environment_canada_thread = threading.Thread(target=start_ec_thread, args=(WEATHER_LINK,))
environment_canada_thread.start()

print("Started Rogers Pass threads")


def get_router_prefix():
    return router.prefix


# Get rogers pass data
@router.get("/", response_class=HTMLResponse)
async def rogers_pass(request: Request):
    # display weather forecast, avalanche for today, any major road events and backcountry access
    # also display two webcams
    avalanche_forecast = get_latest_avalanche_canada_forecast()
    _, major_events = get_latest_drivebc_events()
    backcountry_access = get_latest_backcountry_access()
    environment_canada_weather, ec_weather_date_issued_pst = get_latest_ec_forecast()

    data = {
        "router_prefix": get_router_prefix(),
        "router_name": ROUTER_NAME,
        "avalanche_forecast": avalanche_forecast,
        "major_events": major_events,
        "backcountry_access": backcountry_access,
        "road_webcam": ROGERS_PASS_SUMMIT_DRIVE_WEBCAM,
        "backcountry_map_link": BACKCOUNTRY_AREA_MAP,
        "avalanche_source_name": AVALANCHE_SOURCE_NAME,
        "roads_source_name": ROADS_SOURCE_NAME,
        "weather_source_name": WEATHER_SOURCE_NAME,
        "avalanche_canada_link": AVALANCHE_ORG_LINK,
        "roads_link": DRIVEBC_ORG_LINK,
        "environment_canada_link": ENVIRONMENT_CANADA_ORG_LINK,
        "backcountry_area_source_name": BACKCOUNTRY_AREA_SOURCE_NAME,
        "backcountry_area_source_link": BACKCOUNTRY_AREA_SOURCE_LINK,
        "spotwx_link": SPOTWX_GFS_LINK,
        "windy_link": WINDY_LINK,
        "environment_canada_weather": environment_canada_weather,
        "environment_canada_date_issued_pst": ec_weather_date_issued_pst,
    }
    response = templates.TemplateResponse("summary.html", {"request": request, "data": data})
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# Get rogers pass webcams
@router.get("/webcams", response_class=HTMLResponse)
async def rogers_pass_webcams(request: Request):
    data = {
        "webcams": WEBCAMS,
        "router_prefix": get_router_prefix(),
        "router_name": ROUTER_NAME,
    }
    return templates.TemplateResponse("webcams.html", {"request": request, "data": data})


@router.get("/roads", response_class=HTMLResponse)
async def rogers_pass_roads(request: Request):
    events, _ = get_latest_drivebc_events()
    data = {
        "events": events,
        "router_prefix": get_router_prefix(),
        "router_name": ROUTER_NAME,
    }
    return templates.TemplateResponse("roads.html", {"request": request, "data": data})


# get avalanche forecast
@router.get("/avalanche", response_class=HTMLResponse)
async def rogers_pass_avalanche(request: Request):
    data = {
        "router_prefix": get_router_prefix(),
        "router_name": ROUTER_NAME,
    }
    return templates.TemplateResponse("avalanche.html", {"request": request, "data": data})


@router.get("/avalanche_canada", response_class=HTMLResponse)
async def rogers_pass_avalanche_canada(request: Request):
    modified_content = get_latest_avalanche_canada_forecast()
    return HTMLResponse(content=modified_content)


@router.get("/backcountry-access", response_class=HTMLResponse)
async def rogers_pass_backcountry_access(request: Request):
    backcountry_access = get_latest_backcountry_access()
    data = {
        "router_name": ROUTER_NAME,
        "router_prefix": get_router_prefix(),
        "parkings": backcountry_access.parking_areas,
        "restricted_areas": backcountry_access.restricted_areas,
        "unrestricted_areas": backcountry_access.unrestricted_areas,
        "prohibited_areas": backcountry_access.prohibited_areas,
        "valid_from": backcountry_access.valid_from,
        "valid_until": backcountry_access.valid_to,
        "is_valid": backcountry_access.is_valid,
    }
    return templates.TemplateResponse("backcountry_access.html", {"request": request, "data": data})


@router.get("/weather", response_class=HTMLResponse)
async def rogers_pass_weather(request: Request):
    avalanche_canada_weather = get_avalanche_canada_weather_forecast()
    environment_canada_weather = get_ec_weather_forecast(WEATHER_LINK)
    data = {
        "router_name": ROUTER_NAME,
        "router_prefix": get_router_prefix(),
        "avalanche_canada_weather": avalanche_canada_weather,
        "environment_canada_weather": environment_canada_weather,
    }
    return templates.TemplateResponse("weather_forecast.html", {"request": request, "data": data})


@router.get("/disclaimer", response_class=HTMLResponse)
async def disclaimer(request: Request):
    disclaimer_ = get_disclaimer()
    data = {
        "router_name": ROUTER_NAME,
        "router_prefix": get_router_prefix(),
        "disclaimer": disclaimer_
    }

    return templates.TemplateResponse("disclaimer.html", {"request": request, "data": data})
