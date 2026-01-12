import threading
import time
from dataclasses import dataclass
from datetime import datetime

from app.library.helpers import get_json_response


@dataclass
class RoadEvent:
    headline: str
    description: str
    link: str
    created: str
    updated: str
    type: str
    subtype: str
    latitude: float
    longitude: float
    severity: str = ""


events = []
major_events = []

mutex = threading.Lock()


def start_drivebc_thread(url: str):
    while True:
        try:
            # Get the latest events from DriveBC
            print("Requesting DriveBC events... " + url)
            temp_events, temp_major_events = get_drivebc_events(url)

            with mutex:
                global events
                global major_events
                if temp_events is not None and temp_major_events is not None:
                    print("Updating DriveBC events for url: " + url)
                    events = temp_events
                    major_events = temp_major_events

        except Exception as e:
            print(e)

        # Wait 30 seconds before checking again
        time.sleep(30)


def get_latest_drivebc_events():
    with mutex:
        global events
        global major_events
        return events, major_events


# Custom sorting key function
def custom_sort(event):
    # Parse the updated date in the given format
    updated_date = datetime.strptime(event.updated, "%Y-%m-%dT%H:%M:%S%z")
    return updated_date


def filter_major_events(events: list[RoadEvent]) -> list[RoadEvent]:
    major_events_filtered = []

    string_array = [
        "Glacier National Park",
        "east of Revelstoke",
        "west of Golden",
        "Illecillewaet Brake Check",
        "Revelstoke to Golden",
        "Golden to Revelstoke",
        "Rogers Pass",
        "Roger's Pass"
    ]

    for event in events:
        if event.severity == "MAJOR":
            for string in string_array:
                if string.lower() in event.description.lower():
                    major_events_filtered.append(event)
                    break

    return major_events_filtered


def get_drivebc_events(url: str) -> {list[RoadEvent], list[RoadEvent]}:
    try:
        data = get_json_response(url)

        events = []
        major_events = []

        for event in data["events"]:
            road_event = RoadEvent(
                headline=event["headline"],
                description=event["description"],
                link="https://drivebc.ca/mobile/pub/events/id/" + str(event["id"]).split('/')[-1] + ".html",
                created=event["created"],
                updated=event["updated"],
                type=event["event_type"],
                subtype="",
                latitude=0,
                longitude=0,
                severity=event["severity"]
            )

            if road_event.severity == "MAJOR":
                major_events.append(road_event)
            else:
                events.append(road_event)

        # Sort the list of events
        events = sorted(events, key=custom_sort, reverse=True)
        major_events = sorted(major_events, key=custom_sort, reverse=True)

        # Add the major events back to the list at the beginning
        events = major_events + events

        return events, major_events
    except Exception as e:
        print(e)
        return None, None
