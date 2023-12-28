from dataclasses import dataclass

from app.library.helpers import get_xml_response, get_json_response


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


def custom_sort(event):
    severity_order = {"MAJOR": 0, "MINOR": 1}
    return (severity_order.get(event["severity"], float('inf')), event["severity"])


def get_major_drivebc_events(url: str):
    events = get_drivebc_events(url)
    major_events = []

    for event in events:
        if event.severity == "MAJOR":
            major_events.append(event)

    return major_events


def get_drivebc_events(url: str) -> list[RoadEvent]:
    data = get_json_response(url)
    events = []

    # Sort events using the custom sorting function
    sorted_events = sorted(data["events"], key=custom_sort)

    for event in sorted_events:
        events.append(
            RoadEvent(
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
        )

    # Order by severity MAJOR first, then MINOR, then everything else
    events = sorted(events, key=lambda x: x.severity, reverse=True)
    return events


