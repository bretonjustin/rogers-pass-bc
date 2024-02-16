import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urljoin

import pytz
import requests
from bs4 import BeautifulSoup
from app.library.helpers import get_json_response, default_headers, isLocationInRadius


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


@dataclass
class MinReport:
    id: str
    latitude: str
    longitude: str
    observations: list[str]
    title: str
    username: str
    url: str
    date: str


@dataclass
class MinReports:
    fromDate: str
    region: str
    min_report_list: list[MinReport]


min_reports = MinReports("", "", [])
avalanche_forecast = AvalancheForecast("", [], [], "", "", "", "", "", "", "", "", "")
mutex = threading.Lock()


def start_avalanche_canada_thread(url: str):
    while True:
        try:
            global avalanche_forecast

            # Get the latest events from DriveBC
            print("Requesting Avalanche Canada forecast... " + url)
            temp_avalanche_forecast = get_avalanche_forecast_data(url)

            with mutex:
                if temp_avalanche_forecast is not None:
                    print("Updating Avalanche Canada forecast for url: " + url)
                    avalanche_forecast = temp_avalanche_forecast

        except Exception as e:
            print(e)

        # Wait 30 seconds before checking again
        time.sleep(30)


def get_latest_avalanche_canada_forecast():
    global avalanche_forecast

    with mutex:
        return avalanche_forecast


def utc_to_pst(utc_datetime: str):
    utc_timezone = pytz.timezone("UTC")
    utc_datetime_obj = datetime.strptime(utc_datetime[:16], '%Y-%m-%dT%H:%M')
    utc_datetime = utc_timezone.localize(utc_datetime_obj)

    # Convert to PST (Pacific Standard Time)
    pst_timezone = pytz.timezone("Canada/Pacific")
    pst_datetime = utc_datetime.astimezone(pst_timezone)

    return pst_datetime.strftime("%Y-%m-%d %H:%M")


def get_avalanche_forecast_data(url: str) -> AvalancheForecast | None:
    try:
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

        avalanche_forecast = AvalancheForecast(id_, daily_avalanche_ratings, [], summary, travel_advice,
                                               avalanche_summary,
                                               snowpack_summary, weather_summary, confidence, date_issued, valid_until,
                                               official_link)

        return avalanche_forecast
    except Exception as e:
        print(e)
        return None


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


def get_avalanche_canada_weather_forecast():
    return get_latest_avalanche_canada_forecast().weather_summary
    # json_response = get_json_response(url)
    # summaries = json_response["report"]["summaries"]
    #
    # for summary in summaries:
    #     if summary["type"]["value"] == "weather-summary":
    #         return summary["content"]


def get_latest_avalanche_canada_min_reports():
    global min_reports

    with mutex:
        return min_reports


def start_min_reports_thread(url: str, lat: float, lon: float, radius: int):
    while True:
        try:
            global min_reports

            # Get the latest events from DriveBC
            print("Requesting Avalanche Canada min reports... " + url)
            temp_min_reports = get_avalanche_canada_min_reports(url, lat, lon, radius)

            with mutex:
                if temp_min_reports is not None:
                    print("Updating Avalanche Canada min reports for url: " + url)
                    min_reports = temp_min_reports

        except Exception as e:
            print(e)

        # Wait 30 seconds before checking again
        time.sleep(30)


def get_avalanche_canada_min_reports(url: str, lat: float, lon: float, radius: int) -> MinReports:
    min_reports.min_report_list = []
    min_reports.fromDate = (datetime.now() + timedelta(days=-7)).strftime("%Y-%m-%d")
    min_reports.region = "Selkirks"
    page_size = 1000
    url += f"?fromdate={min_reports.fromDate}&pagesize={page_size}&region={min_reports.region}"
    json_response = get_json_response(url)
    data = json_response["items"]["data"]

    for report in data:
        temp_report = MinReport(id=report["id"],
                                latitude=report["location"]["latitude"],
                                longitude=report["location"]["longitude"],
                                title=report["title"],
                                username=report["username"],
                                url="https://avalanche.ca/mountain-information-network/submissions/" + report["id"],
                                date=report["datetime"],
                                observations=[])

        # convert date to pst timezone
        temp_report.date = utc_to_pst(temp_report.date)

        temp_report.date = temp_report.date[:10]
        for key, value in report["observations"].items():
            if value == 1:
                temp_report.observations.append(key)

        if isLocationInRadius(lat, lon, radius, float(temp_report.latitude), float(temp_report.longitude)):
            min_reports.min_report_list.append(temp_report)

    return min_reports
