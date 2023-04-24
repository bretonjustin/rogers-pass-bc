import os.path
import markdown
import requests
import json
import xmltodict


def openfile(filename):
    filepath = os.path.join("app/pages/", filename)
    with open(filepath, "r", encoding="utf-8") as input_file:
        text = input_file.read()

    html = markdown.markdown(text)
    data = {
        "text": html
    }
    return data


def get_response(url: str):
    res = requests.get(url)
    if res.status_code == 200:
        return res
    else:
        raise Exception("Error receiving data", res.status_code)


def get_json_response(url: str) -> dict:
    return json.loads(get_response(url).json())


def get_xml_response(url: str) -> dict:
    return xmltodict.parse(get_response(url).content)
