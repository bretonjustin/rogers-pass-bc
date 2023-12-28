from dataclasses import dataclass

from app.library.helpers import get_xml_response


@dataclass
class WeatherForecastEC:
    forecast_period: str
    text_summary: str
    icon_url: str


def get_ec_weather_forecast(url: str):
    data = get_xml_response(url)

    forecasts = data["siteData"]["forecastGroup"]["forecast"]

    forecast_objects = []

    for forecast in forecasts:
        forecast_period = str(forecast["period"]["#text"])
        text_summary = str(forecast["textSummary"])
        icon_url = ("https://weather.gc.ca/weathericons/" + str(forecast["abbreviatedForecast"]["iconCode"]["#text"])
                    + ".gif")
        forecast_objects.append(WeatherForecastEC(forecast_period, text_summary, icon_url))

    return forecast_objects


