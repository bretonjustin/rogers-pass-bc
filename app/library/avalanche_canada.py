
import requests
import json
from helpers import get_json_response


def get_avalanche_forecast(link: str):
    # use print version of website and hide some content
    # get the current forecast link with the json data
    url = get_json_response(link)


