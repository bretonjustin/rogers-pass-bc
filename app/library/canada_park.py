import threading
import time
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin

import pytz
import requests
import json
from bs4 import BeautifulSoup
from app.library.helpers import get_json_response, get_response, default_headers


@dataclass
class SkiArea:
    name: str
    isOpen: bool
    comment: str
    geometry_link: str
    group: str


@dataclass
class ParkingArea:
    name: str
    isOpen: bool
    comment: str
    latitude: float
    longitude: float
    group: str


@dataclass
class BackcountryAccess:
    is_valid: bool
    parking_areas: list[ParkingArea]
    unrestricted_areas: list[SkiArea]
    restricted_areas: list[SkiArea]
    prohibited_areas: list[SkiArea]
    valid_from: str
    valid_to: str


backcountry_access = BackcountryAccess(False, [], [], [], [], "", "")
mutex = threading.Lock()


def start_backcountry_access_thread(url: str):
    while True:
        try:
            global backcountry_access

            # Get the latest events from DriveBC
            print("Requesting backcountry access... " + url)
            temp_backcountry_access = get_backcountry_access(url)

            with mutex:
                if temp_backcountry_access is not None:
                    print("Updating backcountry access for url: " + url)
                    backcountry_access = temp_backcountry_access

        except Exception as e:
            print(e)

        # Wait 30 seconds before checking again
        time.sleep(30)


def get_latest_backcountry_access():
    global backcountry_access

    with mutex:
        return backcountry_access


def get_time_from_json_data(data: dict):
    str_date = data["PST"]
    # the format of the date is 2023-12-27T07:19:31-08:00
    # convert to datetime object
    date = datetime.strptime(str_date[:-6], "%Y-%m-%dT%H:%M:%S")
    # format date as YYYY-MM-DD HH:MM (PST)
    return date.strftime('%Y-%m-%d')


def get_backcountry_access(url: str) -> BackcountryAccess | None:
    try:
        # current date in YEAR-MONTH-DAY format as of PST time zone
        date = datetime.now(pytz.timezone('Canada/Pacific')).strftime('%Y-%m-%d')
        # add date to url
        url = url + date

        parking_areas = []
        restricted_areas = []
        unrestricted_areas = []
        prohibited_areas = []
        valid_from = ""
        valid_to = ""

        is_valid = True
        try:
            response = get_json_response(url)
        except Exception as e:
            is_valid = False

        if is_valid:
            valid_from = get_time_from_json_data(response["validFrom"])
            valid_to = get_time_from_json_data(response["validUntil"])

            for area in response["areas"]:
                ski_area = (SkiArea(area['properties']['nameEn'],
                                    area['properties']['isOpen'],
                                    area['properties']['commentEn'],
                                    area['geometry'],
                                    area['properties']['group']))

                soup = BeautifulSoup(ski_area.comment, features="html.parser")
                ski_area.comment = soup.get_text()

                if ski_area.group == 'R':
                    restricted_areas.append(ski_area)
                elif ski_area.group == 'U':
                    unrestricted_areas.append(ski_area)
                elif ski_area.group == 'P':
                    prohibited_areas.append(ski_area)

            for area in response["parkingLots"]:
                parking_area = ParkingArea(area['properties']['nameEn'],
                                           area['properties']['isOpen'],
                                           area['properties']['commentEn'],
                                           area['geometry']['coordinates'][1],
                                           area['geometry']['coordinates'][0],
                                           area['properties']['group'])
                soup = BeautifulSoup(parking_area.comment, features="html.parser")
                parking_area.comment = soup.get_text()

                parking_areas.append(parking_area)

        backcountry_access = BackcountryAccess(
            is_valid,
            parking_areas,
            unrestricted_areas,
            restricted_areas,
            prohibited_areas,
            valid_from,
            valid_to)

        return backcountry_access
    except Exception as e:
        print(e)
        return None
