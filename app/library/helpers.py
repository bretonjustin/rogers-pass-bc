import os.path
import markdown
import requests
import xmltodict

default_headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',  # Add this header
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


def get_response(url: str, headers: dict):
    res = requests.get(url, headers)
    if res.status_code == 200:
        return res
    else:
        raise Exception("Error receiving data", res.status_code)


def get_json_response(url: str) -> dict:
    json_headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=utf-8',
    }
    response = get_response(url, json_headers)
    return response.json()


def get_xml_response(url: str) -> dict:
    xml_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/xml',
        'Accept': 'application/xml, text/xml, */*; q=0.01',
    }
    content = get_response(url, xml_headers).text
    return dict(xmltodict.parse(content, encoding='utf-8'))
