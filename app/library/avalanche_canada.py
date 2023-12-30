from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin

import pytz
import requests
from bs4 import BeautifulSoup
from app.library.helpers import get_json_response, default_headers


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
    id_: str
    forecasts: list[DailyAvalancheRating]
    problems: list[AvalancheProblems]
    summary: str
    travel_advice: str
    avalanche_summary: str
    snowpack_summary: str
    weather_summary: str
    confidence: str
    dateIssued: str
    validUntil: str
    official_link: str


def utc_to_pst(utc_datetime: str):
    utc_timezone = pytz.timezone("UTC")
    utc_datetime_obj = datetime.strptime(utc_datetime, '%Y-%m-%dT%H:%M:%SZ')
    utc_datetime = utc_timezone.localize(utc_datetime_obj)

    # Convert to PST (Pacific Standard Time)
    pst_timezone = pytz.timezone("Canada/Pacific")
    pst_datetime = utc_datetime.astimezone(pst_timezone)

    return pst_datetime.strftime("%Y-%m-%d %H:%M")


def get_avalanche_forecast_data(url: str) -> AvalancheForecast:
    json_response = get_json_response(url)
    summary = json_response["report"]["highlights"]
    travel_advice = json_response["report"]["terrainAndTravelAdvice"]

    date_issued = utc_to_pst(json_response["report"]["dateIssued"])
    valid_until = utc_to_pst(json_response["report"]["validUntil"])

    confidence = json_response["report"]["confidence"]["rating"]["value"]
    weather_summary = ""
    avalanche_summary = ""
    snowpack_summary = ""
    summaries = json_response["report"]["summaries"]
    for summary_ in summaries:
        if summary_["type"]["value"] == "weather-summary":
            weather_summary = summary_["content"]
        if summary_["type"]["value"] == "avalanche-summary":
            avalanche_summary = summary_["content"]
        if summary_["type"]["value"] == "snowpack-summary":
            snowpack_summary = summary_["content"]

    daily_avalanche_ratings = []

    id_ = json_response["report"]["id"]
    official_link = "https://www.avalanche.ca/forecasts/" + id_

    for daily_avalanche_rating in json_response["report"]["dangerRatings"]:
        date = daily_avalanche_rating["date"]["display"]
        alpine_danger_rating = daily_avalanche_rating["ratings"]["alp"]["rating"]["value"]
        treeline_danger_rating = daily_avalanche_rating["ratings"]["tln"]["rating"]["value"]
        below_treeline_danger_rating = daily_avalanche_rating["ratings"]["btl"]["rating"]["value"]
        daily_avalanche_ratings.append(
            DailyAvalancheRating(date, alpine_danger_rating, treeline_danger_rating, below_treeline_danger_rating))

    avalanche_forecast = AvalancheForecast(id_, daily_avalanche_ratings, [], summary, travel_advice, avalanche_summary,
                                           snowpack_summary, weather_summary, confidence, date_issued, valid_until,
                                           official_link)

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

        # for element in soup.select('.Notifications_Set__Zo5NW'):
        #     element.decompose()

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



