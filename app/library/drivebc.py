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


# Custom sorting key function
def custom_sort(event):
    # Parse the updated date in the given format
    updated_date = datetime.strptime(event.updated, "%Y-%m-%dT%H:%M:%S%z")
    return updated_date


def get_drivebc_events(url: str) -> {list[RoadEvent], list[RoadEvent]}:
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


