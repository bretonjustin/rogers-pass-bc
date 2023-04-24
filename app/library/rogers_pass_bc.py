from webcams import Webcam

AVALANCHE_LINK = "https://api.avalanche.ca/forecasts/:lang/products/point?lat=51.29998&long=-117.51866"
WEATHER_LINK = "https://dd.weather.gc.ca/citypage_weather/xml/HEF/s0000856_e.xml"
DRIVE_LINK = "https://api.open511.gov.bc.ca/events?area_id=drivebc.ca/3&severity=MAJOR"
SPOTWX_LINK = "https://spotwx.com/products/grib_index.php?model=gem_glb_15km&lat=51.27545&lon=-117.52779&tz=America/Vancouver&label="

WEBCAMS = [
    Webcam("Rogers Pass Summit", 1.1, 2.2, 1330, "https://images.drivebc.ca/bchighwaycam/pub/cameras/101.jpg"),
]
