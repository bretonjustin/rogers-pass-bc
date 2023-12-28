from dataclasses import dataclass

from helpers import get_xml_response

@dataclass
class WeatherForecastEC:
    forecast_period: str
    text_summary: str
    icon_code: str



def get_weather_forecast(url: str):
    data = get_xml_response(url)


