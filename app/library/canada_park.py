from urllib.parse import urljoin

import requests
import json
from bs4 import BeautifulSoup
from app.library.helpers import get_json_response, get_response, default_headers


def get_backcountry_access_map(url: str):
    # load page and wait to load
    response = get_response(url, default_headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # hide id "controls"
    controls = soup.find(id="controls")
    controls['style'] = "display:none"

    # return the modified html
    return str(soup)
