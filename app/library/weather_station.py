import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urljoin

import pytz
import requests
from bs4 import BeautifulSoup
from app.library.helpers import get_json_response, default_headers, isLocationInRadius

from highcharts_core.chart import Chart


weather_station_measurement_plot = ""
mutex = threading.Lock()

@dataclass
class WeatherStationMeasurement:
    station: int
    measurementDateTime: datetime
    transmissionDateTime: datetime
    hourlyPrecip: float
    snowHeight: float
    airTempAvg: float
    airTempMax: float
    airTempMin: float
    windSpeedAvg: float
    windDirCompass: str
    windSpeedGust: float
    relativeHumidity: float


def start_weather_station_thread(url: str):
    while True:
        try:
            global weather_station_measurement_plot

            # Get the latest events from DriveBC
            print("Requesting Weather Station data... " + url)
            temp_weather_station_measurement = get_weather_station_data(url)

            with mutex:
                if temp_weather_station_measurement is not None:
                    print("Updating Weather station for url: " + url)
                    weather_station_measurement_plot = plot_weather_station_data(temp_weather_station_measurement)

        except Exception as e:
            print(e)

        # Wait 30 seconds before checking again
        time.sleep(30)


def plot_weather_station_data(data):
    time_array = []
    snow_height_array = []
    air_temp_avg_array = []
    wind_speed_avg_array = []

    # order the data by date time
    data.sort(key=lambda x: x.measurementDateTime)

    for measurement in data:
        measurement.measurementDateTime = measurement.measurementDateTime.replace(tzinfo=pytz.utc)
        measurement.measurementDateTime = measurement.measurementDateTime.astimezone(pytz.timezone('America/Vancouver'))
        time_str = measurement.measurementDateTime.strftime("%b %d %H:%M")
        time_array.append(time_str)
        snow_height_array.append(measurement.snowHeight)
        air_temp_avg_array.append(measurement.airTempAvg)
        wind_speed_avg_array.append(measurement.windSpeedAvg)

    colors = ["#2caffe", "#544fc5", "#00e272"]
    complete_chart = Chart(container='weather_station_chart', options={
        "chart": {"type": "line",
                  "height": 500,  # Set minimum height here
                  "style": {
                      "minHeight": "500px"  # Ensure it's respected across various devices
                  }
                  },
        "title": {"text": "Rogers Pass Weather Station"},
        "colors": colors,
        "xAxis": {"categories": time_array},
        "yAxis": [
            {"title": {"text": "Snow Height (cm)"},
             "labels": {"format": "{value} cm"}},
            {"title": {"text": "Air Temp Avg (°C)"},
             "labels": {"format": "{value} °C"}, "opposite": True},
            {"title": {"text": "Wind Speed Avg (km/h)"},
             "labels": {"format": "{value} km/h"}, "opposite": True}
        ],
        "series": [
            {"name": "Snow Height", "data": snow_height_array, "yAxis": 0, "tooltip": {"valueSuffix": " cm"}},
            {"name": "Air Temp Avg", "data": air_temp_avg_array, "yAxis": 1, "tooltip": {"valueSuffix": " °C"}},
            {"name": "Wind Speed Avg", "data": wind_speed_avg_array, "yAxis": 2, "tooltip": {"valueSuffix": " km/h"}}
        ],
        "legend": {"enabled": True, "layout": "horizontal", "align": "center", "verticalAlign": "bottom"},
        "tooltip": {
            "shared": True,
        }
    })

    snow_chart = Chart(container='snow_chart', options={
        "chart": {"type": "line",
                  "height": 500,  # Set minimum height here
                  "style": {
                      "minHeight": "500px"  # Ensure it's respected across various devices
                  }
                  },
        "title": {"text": "Rogers Pass Weather Station Snow Height"},
        "colors": [colors[0]],
        "xAxis": {"categories": time_array},
        "yAxis": {"title": {"text": "Snow Height (cm)"},
                  "labels": {"format": "{value} cm"}},
        "series": [
            {"name": "Snow Height", "data": snow_height_array, "tooltip": {"valueSuffix": " cm"}}
        ],
        "legend": {"enabled": False},  # Disable legend
    })

    air_temp_chart = Chart(container='air_temp_chart', options={
        "chart": {"type": "line",
                  "height": 500,  # Set minimum height here
                  "style": {
                      "minHeight": "500px"  # Ensure it's respected across various devices
                  }
                  },
        "title": {"text": "Rogers Pass Weather Station Air Temp Avg"},
        "colors": [colors[1]],
        "xAxis": {"categories": time_array},
        "yAxis": {"title": {"text": "Air Temp Avg (°C)"},
                  "labels": {"format": "{value} °C"}},
        "series": [
            {"name": "Air Temp Avg", "data": air_temp_avg_array, "tooltip": {"valueSuffix": " °C"}}
        ],
        "legend": {"enabled": False},  # Disable legend
    })

    wind_speed_chart = Chart(container='wind_speed_chart', options={
        "chart": {"type": "line",
                  "height": 500,  # Set minimum height here
                  "style": {
                      "minHeight": "500px"  # Ensure it's respected across various devices
                  }
                  },
        "title": {"text": "Rogers Pass Weather Station Wind Speed Avg"},
        "colors": [colors[2]],
        "xAxis": {"categories": time_array},
        "yAxis": {"title": {"text": "Wind Speed Avg (km/h)"},
                  "labels": {"format": "{value} km/h"}},
        "series": [
            {"name": "Wind Speed Avg", "data": wind_speed_avg_array, "tooltip": {"valueSuffix": " km/h"}}
        ],
        "legend": {"enabled": False},  # Disable legend
    })

    return (complete_chart.to_js_literal(event_listener_enabled=False), snow_chart.to_js_literal(event_listener_enabled=False), air_temp_chart.to_js_literal(event_listener_enabled=False),
            wind_speed_chart.to_js_literal(event_listener_enabled=False))


def get_weather_station_data(url: str):
    try:
        json_response = get_json_response(url)

        # response is a list of measurements
        measurements = []

        for measurement in json_response:
            # cast each field to a measurement object
            measurements.append(WeatherStationMeasurement(
                station=measurement["station"],
                measurementDateTime=datetime.fromisoformat(measurement["measurementDateTime"]),
                transmissionDateTime=datetime.fromisoformat(measurement["transmissionDateTime"]),
                hourlyPrecip=measurement["hourlyPrecip"],
                snowHeight=measurement["snowHeight"],
                airTempAvg=measurement["airTempAvg"],
                airTempMax=measurement["airTempMax"],
                airTempMin=measurement["airTempMin"],
                windSpeedAvg=measurement["windSpeedAvg"],
                windDirCompass=measurement["windDirCompass"],
                windSpeedGust=measurement["windSpeedGust"],
                relativeHumidity=measurement["relativeHumidity"]
            ))

        return measurements

    except Exception as e:
        print(f"Error getting weather station data: {e}")
        return None


def get_latest_weather_station_data():
    global weather_station_measurement_plot
    with mutex:
        return weather_station_measurement_plot





