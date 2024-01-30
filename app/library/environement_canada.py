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
date_issued_pst = ""
mutex = threading.Lock()


def start_ec_thread(url: str):
    while True:
        try:
            global ec_forecast
            global date_issued_pst

            # Get the latest events from DriveBC
            print("Requesting Environment Canada forecast... " + url)
            temp_ec_forecast, date_issued_pst_temp = get_ec_weather_forecast(url)

            with mutex:
                if temp_ec_forecast is not None and date_issued_pst_temp is not None:
                    print("Updating Environment Canada forecast for url: " + url)
                    ec_forecast = temp_ec_forecast
                    date_issued_pst = date_issued_pst_temp

        except Exception as e:
            print(e)

        # Wait 30 seconds before checking again
        time.sleep(30)


def get_latest_ec_forecast():
    global ec_forecast
    global date_issued_pst

    with mutex:
        return ec_forecast, date_issued_pst


def get_ec_weather_forecast(url: str):
    try:
        data = get_xml_response(url)

        forecasts = data["siteData"]["forecastGroup"]["forecast"]
        timestamps = data["siteData"]["forecastGroup"]["dateTime"]

        pst_time_str = ""

        for timestamp in timestamps:
            if timestamp["@zone"] == "PST" and timestamp["@name"] == "forecastIssue":
                pst_time = timestamp["timeStamp"]
                # parse the time in the format 20240119100508 to a datetime object
                pst_time = time.strptime(pst_time, "%Y%m%d%H%M%S")
                # format the time as YYYY-MM-DD HH:MM PST
                pst_time_str = time.strftime("%Y-%m-%d %H:%M", pst_time) + " PST"
                break

        forecast_objects = []

        for forecast in forecasts:
            forecast_period = str(forecast["period"]["#text"])
            text_summary = str(forecast["textSummary"])
            icon_url = ("https://weather.gc.ca/weathericons/" + str(forecast["abbreviatedForecast"]["iconCode"]["#text"])
                        + ".gif")
            forecast_objects.append(WeatherForecastEC(forecast_period, text_summary, icon_url))

        return forecast_objects, pst_time_str
    except Exception as e:
        print(e)
        return None


