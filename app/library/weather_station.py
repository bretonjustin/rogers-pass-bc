import json
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
    hourlyPrecip: float
    snowHeight: float
    airTempAvg: float
    windSpeedAvg: float
    windDirCompass: str
    windSpeedGust: float
    relativeHumidity: float
    newSnow: float


def start_weather_station_thread(url: str):
    while True:
        try:
            # Get the latest events from DriveBC
            print("Requesting Weather Station data... " + url)
            temp_weather_station_measurement = get_weather_station_data(url)

            temp_weather_station_measurement_plot = plot_weather_station_data(temp_weather_station_measurement)

            with mutex:
                global weather_station_measurement_plot
                if temp_weather_station_measurement_plot is not None:
                    print("Updating Weather station for url: " + url)
                    weather_station_measurement_plot = temp_weather_station_measurement_plot

        except Exception as e:
            print(e)

        # Wait 30 seconds before checking again
        time.sleep(30)


def plot_weather_station_data(data):
    try:
        if data is None:
            raise Exception("No data to plot")

        time_array = []
        snow_height_array = []
        air_temp_avg_array = []
        wind_speed_avg_array = []
        wind_speed_gust_array = []
        wind_direction_array = []

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
            wind_speed_gust_array.append(measurement.windSpeedGust)
            wind_direction_array.append(measurement.windDirCompass)

        colors = ["#2caffe", "#544fc5", "#00e272", "#e69138", "#a64d79"]
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
            },
            "accessibility": {
                "enabled": False,
            },
        })

        snow_chart = Chart(container='snow_chart', options={
            "chart": {"type": "line",
                      "height": 500,  # Set minimum height here
                      "style": {
                          "minHeight": "500px"  # Ensure it's respected across various devices
                      }
                      },
            "title": {"text": "Snow Height"},
            "colors": [colors[0]],
            "xAxis": {"categories": time_array},
            "yAxis": {"title": {"text": "Snow Height (cm)"},
                      "labels": {"format": "{value} cm"}},
            "series": [
                {"name": "Snow Height", "data": snow_height_array, "tooltip": {"valueSuffix": " cm"}}
            ],
            "legend": {"enabled": False},  # Disable legend
            "accessibility": {
                "enabled": False,
            },
        })

        air_temp_chart = Chart(container='air_temp_chart', options={
            "chart": {"type": "line",
                      "height": 500,  # Set minimum height here
                      "style": {
                          "minHeight": "500px"  # Ensure it's respected across various devices
                      }
                      },
            "title": {"text": "Air Temperature Average"},
            "colors": [colors[1]],
            "xAxis": {"categories": time_array},
            "yAxis": {"title": {"text": "Air Temp Avg (°C)"},
                      "labels": {"format": "{value} °C"}},
            "series": [
                {"name": "Air Temp Avg", "data": air_temp_avg_array, "tooltip": {"valueSuffix": " °C"}}
            ],
            "legend": {"enabled": False},  # Disable legend
            "accessibility": {
                "enabled": False,
            },
        })

        wind_speed_chart = Chart(container='wind_speed_chart', options={
            "chart": {"type": "line",
                      "height": 500,  # Set minimum height here
                      "style": {
                          "minHeight": "500px"  # Ensure it's respected across various devices
                      }
                      },
            "title": {"text": "Wind Speed"},
            "colors": [colors[2], colors[3]],
            "xAxis": {"categories": time_array},
            "yAxis": {"title": {"text": "Wind Speed (km/h)"},
                      "labels": {"format": "{value} km/h"}},
            "tooltip": {
                "shared": True,  # Enable shared tooltip
                "useHTML": True,  # Optional: Use HTML for better formatting
                "headerFormat": '<strong>Time: {point.x}</strong><br/>',  # Customize header
                "pointFormat": '<span style="color:{series.color}">{series.name}: <b>{point.y} km/h</b></span><br/>'
                # Customize point format
            },
            "series": [
                {"name": "Wind Speed Avg", "data": wind_speed_avg_array, "tooltip": {"valueSuffix": " km/h"}},
                {"name": "Wind Speed Gust", "data": wind_speed_gust_array, "tooltip": {"valueSuffix": " km/h"},
                 "dashStyle": "ShortDash"}
            ],
            "legend": {"enabled": True},  # Disable legend
            "accessibility": {
                "enabled": False,
            },
        })

        # Define the wind direction labels
        wind_direction_labels = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

        # Convert your wind direction data to indices
        # For example, if your angles are [0, 45, 90, 135, 180, 225, 270, 315]:
        # wind_direction_angles = [0, 45, 90, 135, 180, 225, 270, 315]  # These should correspond to angles

        # Convert angles to indices based on the labels
        wind_direction_indices = [wind_direction_labels.index(direction) for direction in wind_direction_array]

        # Create the wind direction chart
        wind_direction_chart = Chart(container='wind_direction_chart', options={
            "chart": {
                "type": "line",
                "height": 500,  # Set minimum height here
                "style": {
                    "minHeight": "500px"  # Ensure it's respected across various devices
                }
            },
            "title": {"text": "Wind Direction"},
            "colors": [colors[4]],  # Specify your colors as needed
            "xAxis": {"categories": time_array},  # Assume time_array is defined
            "yAxis": {
                "title": {"text": "Wind Direction"},
                "categories": wind_direction_labels,  # Use string labels for y-axis
                "labels": {
                    "formatter": "function() { return this.value; }"  # Just return the category
                }
            },
            "series": [
                {"name": "Wind Direction", "data": wind_direction_indices,
                 "tooltip": {
                     "pointFormatter": f"function() {{ return 'Wind Direction: ' + {json.dumps(wind_direction_labels)}[this.y]; }}",
                     "followTouchMove": False,
                 }
                 }
            ],
            "legend": {"enabled": False},  # Enable legend
            "accessibility": {
                "enabled": False,
            },
        })

        return (complete_chart.to_js_literal(event_listener_enabled=False),
                snow_chart.to_js_literal(event_listener_enabled=False),
                air_temp_chart.to_js_literal(event_listener_enabled=False),
                wind_speed_chart.to_js_literal(event_listener_enabled=False),
                wind_direction_chart.to_js_literal(event_listener_enabled=False))
    except Exception as e:
        print(f"Error plotting weather station data: {e}")
        return None


def get_weather_station_data(url: str):
    try:
        json_response = get_json_response(url)

        # response is a list of measurements
        measurements = []

        for measurement in json_response:
            # cast each field to a measurement object
            measurements.append(WeatherStationMeasurement(
                station=measurement["stationId"],
                measurementDateTime=datetime.strptime(measurement["measurementDateTime"], "%Y-%m-%dT%H:%M:%SZ"),
                hourlyPrecip=measurement["hourlyPrecip"],
                snowHeight=measurement["snowHeight"],
                airTempAvg=measurement["airTempAvg"],
                windSpeedAvg=measurement["windSpeedAvg"],
                windDirCompass=measurement["windDirCompass"],
                windSpeedGust=measurement["windSpeedGust"],
                relativeHumidity=measurement["relativeHumidity"],
                newSnow=measurement["newSnow"]
            ))

        return measurements

    except Exception as e:
        print(f"Error getting weather station data: {e}")
        return None


def get_latest_weather_station_data():
    with mutex:
        global weather_station_measurement_plot
        return weather_station_measurement_plot
