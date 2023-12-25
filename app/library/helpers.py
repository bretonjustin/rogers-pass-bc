import os.path
import markdown
import requests
import json
import xmltodict
import xml.etree.ElementTree as ET

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/xml, text/xml, */*; q=0.01',  # Add this header
}

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
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res
    else:
        raise Exception("Error receiving data", res.status_code)


def get_json_response(url: str) -> dict:
    return json.loads(get_response(url).json())


def get_xml_response(url: str) -> dict:
    content = get_response(url).text
    return dict(xmltodict.parse(content, encoding='utf-8'))
