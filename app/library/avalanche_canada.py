from dataclasses import dataclass
from urllib.parse import urljoin

import requests
import json
from bs4 import BeautifulSoup
from app.library.helpers import get_json_response, get_response, default_headers


@dataclass
class DailyAvalancheRating:
    date: str
    alpine_danger_rating: str
    treeline_danger_rating: str
    below_treeline_danger_rating: str


@dataclass
class AvalancheProblems:
    summary: str


@dataclass
class AvalancheForecast:
    forecasts: list[DailyAvalancheRating]
    problems: list[AvalancheProblems]
    summary: str
    travel_advice: str
    avalanche_summary: str
    snowpack_summary: str
    weather_summary: str
    confidence: str


def get_avalanche_forecast_data(url: str) -> AvalancheForecast:
    avalanche_forecast = AvalancheForecast([], [], "", "", "", "", "", "")
    return avalanche_forecast


# Inside the /embedded-page route
def extract_external_stylesheets(original_content, base_url):
    soup = BeautifulSoup(original_content, 'html.parser')
    stylesheets = []

    # Find and extract links to external stylesheets
    # Find and extract links to external stylesheets
    for link in soup.find_all('link', rel='stylesheet'):
        href = link.get('href')
        if href:
            # Make the URL absolute if it's relative
            absolute_url = urljoin(base_url, href)
            stylesheets.append(absolute_url)

    return stylesheets


def get_avalanche_forecast(link: str):
    # use print version of website and hide some content
    # get the current forecast link with the json data
    json_response = get_json_response(link)
    # get the forecast link
    forecast_link = json_response["url"]

    # get the print format of the forecast link
    print_link = forecast_link + "/print"

    try:
        # Fetch content from the target webpage
        response = requests.get(print_link, headers=default_headers)
        original_content = response.content

        # Extract external stylesheets from the original content
        original_stylesheets = extract_external_stylesheets(original_content, print_link)

        # Use BeautifulSoup to manipulate the HTML content
        soup = BeautifulSoup(original_content, 'html.parser')
        # Hide specific elements
        for element in soup.select('.forecast_ImprovedPrintableAlert__aTZ5_'):
            element.decompose()

        for element in soup.select('.forecast_LocaleSwitcher__ISgAQ'):
            element.decompose()

        for element in soup.select('.Forecast_Footer__fTwcV'):
            element.decompose()

        for element in soup.select('.Notifications_Set__Zo5NW'):
            element.decompose()

        # Render the modified content
        modified_content = str(soup)

        # Include original external stylesheets dynamically
        for stylesheet in original_stylesheets:
            modified_content = modified_content.replace(
                '</head>',
                f'<link rel="stylesheet" href="{stylesheet}"></head>',
                1  # Replace only the first occurrence (assuming </head> appears once)
            )

        return modified_content
    except Exception as e:
        print(e)
        return 'Internal Server Error', 500


def get_avalanche_canada_weather_forecast(url: str):
    json_response = get_json_response(url)
    summaries = json_response["report"]["summaries"]

    for summary in summaries:
        if summary["type"]["value"] == "weather-summary":
            return summary["content"]



