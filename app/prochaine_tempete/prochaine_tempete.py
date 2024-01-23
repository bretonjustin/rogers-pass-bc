# -*- coding: utf-8 -*-
# !/usr/bin/python3

from datetime import datetime
import ftplib
import time
import sys
import pytz
from jinja2 import Environment, FileSystemLoader

from app.prochaine_tempete.helpers import get_csv
import os

from dotenv import load_dotenv

load_dotenv()

base_api_url = "https://spotwx.io/api.php"
api_key = os.environ['API_KEY']

mountains = [
    {"name": "Mont Comi", "lat": "48.46575", "lon": "-68.21036", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Mont Sutton", "lat": "45.08195", "lon": "-72.54837", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Mont Lyall", "lat": "48.80412", "lon": "-66.08622", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Mont Gosford", "lat": "45.30179", "lon": "-70.86683", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Mont Hereford", "lat": "45.08229", "lon": "-71.60047", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Mont Albert", "lat": "48.93293", "lon": "-66.17872", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Massif du Sud", "lat": "46.62235", "lon": "-70.48768", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Mont Edouard", "lat": "48.15209", "lon": "-70.28355", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Massif de Charlevoix", "lat": "47.27839", "lon": "-70.61007", "snow": 0.0, "rain": 0.0,
     "freezing_rain": 0.0, "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "",
     "gfs_link": "", "google_map_link": ""},
    {"name": "Mont Orford", "lat": "45.31228", "lon": "-72.24160", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Mont Saint-Anne", "lat": "47.08696", "lon": "-70.93293", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Montagne Noire", "lat": "46.24366", "lon": "-74.29391", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Mont des Allemands", "lat": "49.17056", "lon": "-71.47667", "snow": 0.0, "rain": 0.0,
     "freezing_rain": 0.0, "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "",
     "gfs_link": "", "google_map_link": ""},
    {"name": "Mont Jacob", "lat": "48.41679", "lon": "-71.26578", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Mont Brillant", "lat": "46.91041", "lon": "-71.46024", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Mont Saint-Mathieu", "lat": "46.59737", "lon": "-72.83955", "snow": 0.0, "rain": 0.0,
     "freezing_rain": 0.0, "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "",
     "gfs_link": "", "google_map_link": ""},
    {"name": "Mont Alta", "lat": "46.03834", "lon": "-74.24119", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Mont Gallix", "lat": "50.16871", "lon": "-66.71735", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Mont Plante (Val-David-Val-Morin)", "lat": "46.02857", "lon": "-74.19882", "snow": 0.0, "rain": 0.0,
     "freezing_rain": 0.0, "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "",
     "gfs_link": "", "google_map_link": ""},
    {"name": "Les Sentiers du Moulin", "lat": "46.97585", "lon": "-71.25365", "snow": 0.0, "rain": 0.0,
     "freezing_rain": 0.0, "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "",
     "gfs_link": "", "google_map_link": ""},
    {"name": "Mont Hog's Back", "lat": "48.85675", "lon": "-66.10941", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Mont Veyrier (Monts Groulx)", "lat": "51.53338", "lon": "-68.08214", "snow": 0.0, "rain": 0.0,
     "freezing_rain": 0.0, "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "",
     "gfs_link": "", "google_map_link": ""},
    {"name": "Mont Valin", "lat": "48.61678", "lon": "-70.79904", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Le Valinouët", "lat": "48.63892", "lon": "-70.89714", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Ski Bromont", "lat": "45.28877", "lon": "-72.63882", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Owl's Head", "lat": "45.06267", "lon": "-72.29796", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Mont Blanc", "lat": "46.10164", "lon": "-74.48507", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Mont Tremblant", "lat": "46.22896", "lon": "-74.55661", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Mont Shefford", "lat": "45.36228", "lon": "-72.61082", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""},
    {"name": "Mont Adstock", "lat": "46.03107", "lon": "-71.20695", "snow": 0.0, "rain": 0.0, "freezing_rain": 0.0,
     "ice_pellets": 0.0, "hrdps_link": "", "gdps_link": "", "rdps_link": "", "nam_link": "", "gfs_link": "",
     "google_map_link": ""}
]

models = [
    ["hrdps_continental", "hrdps_continental"],
    ["rdps", "rdps_10km"],
    ["gdps", "gem_glb_15km"],
    ["nam", "nam_awphys"],
    ["gfs", "gfs_pgrb2_0p25_f"],
]

model_for_data = "rdps"

# Set the timezone to Montreal
montreal_timezone = pytz.timezone('America/Toronto')

# Create a Jinja2 environment and specify the templates directory
templates = Environment(loader=FileSystemLoader(os.path.join('app', 'prochaine_tempete', 'templates')))


def get_model_for_data(model_str):
    for model in models:
        if model[0] == model_str:
            return model


def populate_dict_array():
    for mountain in mountains:
        utc_offset = datetime.now(montreal_timezone).strftime('%z')
        url = base_api_url + "?key=" + api_key + "&lat=" + mountain["lat"] + "&lon=" + mountain["lon"] + "&model=" + \
              get_model_for_data(model_for_data)[1] + "&tz=" + utc_offset + "&format=csv"

        csv_data = get_csv(url)

        mountain["snow"] = csv_data[len(csv_data) - 1]["SQP"]
        mountain["rain"] = csv_data[len(csv_data) - 1]["RQP"]
        mountain["freezing_rain"] = csv_data[len(csv_data) - 1]["FQP"]
        mountain["ice_pellets"] = csv_data[len(csv_data) - 1]["IQP"]

        mountain["rdps_link"] = "https://spotwx.com/products/grib_index.php?model=" + get_model_for_data("rdps")[
            1] + "&lat=" + mountain["lat"] + "&lon=" + mountain["lon"] + "&tz=America%2FMontreal&label=" + mountain[
                                    "name"]
        mountain["rdps_link"] = mountain["rdps_link"].replace(" ", "%20")

        mountain["hrdps_link"] = "https://spotwx.com/products/grib_index.php?model=" + get_model_for_data("hrdps_continental")[
            1] + "&lat=" + mountain["lat"] + "&lon=" + mountain["lon"] + "&tz=America%2FMontreal&label=" + mountain[
                                     "name"]
        mountain["hrdps_link"] = mountain["hrdps_link"].replace(" ", "%20")

        mountain["gdps_link"] = "https://spotwx.com/products/grib_index.php?model=" + get_model_for_data("gdps")[
            1] + "&lat=" + mountain["lat"] + "&lon=" + mountain["lon"] + "&tz=America%2FMontreal&label=" + mountain[
                                    "name"]
        mountain["gdps_link"] = mountain["gdps_link"].replace(" ", "%20")

        mountain["nam_link"] = "https://spotwx.com/products/grib_index.php?model=" + get_model_for_data("nam")[
            1] + "&lat=" + mountain["lat"] + "&lon=" + mountain["lon"] + "&tz=America%2FMontreal&label=" + mountain[
                                   "name"]
        mountain["nam_link"] = mountain["nam_link"].replace(" ", "%20")

        mountain["gfs_link"] = "https://spotwx.com/products/grib_index.php?model=" + get_model_for_data("gfs")[
            1] + "&lat=" + mountain["lat"] + "&lon=" + mountain["lon"] + "&tz=America%2FMontreal&label=" + mountain[
                                   "name"]
        mountain["gfs_link"] = mountain["gfs_link"].replace(" ", "%20")

        mountain["google_map_link"] = "https://www.google.com/maps?z=12&t=k&q=""" + mountain["lat"] + """,""" + \
                                      mountain[
                                          "lon"] + """&ll=""" + mountain["lat"] + """,""" + mountain["lon"]

        mountain["google_map_link"] = mountain["google_map_link"].replace(" ", "%20")

        print(mountain["name"] + " done...")

        time.sleep(0.5)

    return mountains


def generate_html(sorted_mountains):
    # Get the current time in Montreal timezone
    now = datetime.now(montreal_timezone)

    data = {
        "mountains": sorted_mountains,
        "last_update": now.strftime("%Y-%m-%d %H:%M"),
    }

    # Load a template from the templates directory
    template = templates.get_template('prochaine_tempete.html')

    output = template.render({"data": data})

    file_name = 'index.html'
    with open(file_name, 'w', encoding="utf-8") as filetowrite:
        filetowrite.write(output)

    return file_name


def upload_ftp(file_name):
    username = str(os.environ['FTP_USERNAME'])
    password = str(os.environ['FTP_PASSWORD'])
    session = ftplib.FTP_TLS('justinbreton.xyz', username, password)
    file = open(file_name, 'rb')  # file to send
    session.storbinary('STOR /domains/justinbreton.xyz/public_html/prochaine-tempete/index.html', file)  # send the file
    file.close()  # close file and FTP
    session.quit()

    print("FTP upload done")


def prochaine_tempete():
    while True:
        try:
            unsorted_mountains = populate_dict_array()

            sorted_mountains = sorted(unsorted_mountains, key=lambda x: float(x["snow"]), reverse=True)

            file_name = generate_html(sorted_mountains)

            print("HTML done...")

            upload_ftp(file_name)

            print("FTP done...")

            time.sleep(53 * 60)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: " + str(e) + " " + str(exc_type) + " " + str(fname) + " " + str(exc_tb.tb_lineno))
            time.sleep(10)

