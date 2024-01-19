import threading
import time
from dataclasses import dataclass

from app.library.helpers import get_xml_response


@dataclass
class WeatherForecastEC:
    forecast_period: str
    text_summary: str
    icon_url: str


ec_forecast = []
mutex = threading.Lock()


def start_ec_thread(url: str):
    while True:
        global ec_forecast

        # Get the latest events from DriveBC
        temp_ec_forecast = get_ec_weather_forecast(url)

        with mutex:
            if temp_ec_forecast is not None:
                print("Updating Environment Canada forecast for url: " + url)
                ec_forecast = temp_ec_forecast

        # Wait 30 seconds before checking again
        time.sleep(30)


def get_latest_ec_forecast():
    global ec_forecast

    with mutex:
        return ec_forecast


def get_ec_weather_forecast(url: str):
    try:
        data = get_xml_response(url)

        forecasts = data["siteData"]["forecastGroup"]["forecast"]
        timestamp_pst = data["siteData"]["dateTime"]["dateTime"]

        forecast_objects = []

        for forecast in forecasts:
            forecast_period = str(forecast["period"]["#text"])
            text_summary = str(forecast["textSummary"])
            icon_url = ("https://weather.gc.ca/weathericons/" + str(forecast["abbreviatedForecast"]["iconCode"]["#text"])
                        + ".gif")
            forecast_objects.append(WeatherForecastEC(forecast_period, text_summary, icon_url))

        return forecast_objects
    except Exception as e:
        print(e)
        return None


