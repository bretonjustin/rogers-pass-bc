import threading
import time
from dataclasses import dataclass

from app.library.helpers import get_xml_response, get_html_response


@dataclass
class WeatherForecastEC:
    forecast_period: str
    text_summary: str
    icon_url: str


ec_forecast = []
date_issued_pst = ""
mutex = threading.Lock()


def start_ec_thread(url: str, weather_id: str):
    while True:
        try:
            # Get the latest events from DriveBC
            print("Requesting Environment Canada forecast... " + url + " for weather id: " + weather_id)
            temp_ec_forecast, date_issued_pst_temp = get_ec_weather_forecast(url, weather_id)

            with mutex:
                global ec_forecast
                global date_issued_pst
                if temp_ec_forecast is not None and date_issued_pst_temp is not None:
                    print("Updating Environment Canada forecast for url: " + url + " for weather id: " + weather_id)
                    ec_forecast = temp_ec_forecast
                    date_issued_pst = date_issued_pst_temp

        except Exception as e:
            print(e)

        # Wait 30 seconds before checking again
        time.sleep(30)


def get_latest_ec_forecast():
    with mutex:
        global ec_forecast
        global date_issued_pst
        return ec_forecast, date_issued_pst


def get_ec_weather_forecast(url: str, weather_id: str):
    try:
        correct_url = ""

        html_response = get_html_response(url)

        # find the link that contains the weather id
        for line in html_response.splitlines():
            if weather_id in line and "xml" in line:
                # extract the url from the line
                start_index = line.find("href=\"") + 6
                end_index = line.find(".xml") + 4
                correct_url = line[start_index:end_index]
                correct_url = url + correct_url
                break

        data = get_xml_response(correct_url)

        forecasts = data["siteData"]["forecastGroup"]["forecast"]
        timestamps = data["siteData"]["forecastGroup"]["dateTime"]

        pst_time_str = ""

        for timestamp in timestamps:
            if timestamp["@zone"] != "UTC" and timestamp["@name"] == "forecastIssue":
                pst_time = timestamp["timeStamp"]
                # parse the time in the format 20240119100508 to a datetime object
                pst_time = time.strptime(pst_time, "%Y%m%d%H%M%S")
                # format the time as YYYY-MM-DD HH:MM PST
                pst_time_str = time.strftime("%Y-%m-%d %H:%M", pst_time) + " " + str(timestamp["@zone"])
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


