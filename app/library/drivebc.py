from dataclasses import dataclass

from app.library.helpers import get_xml_response


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


def get_major_drivebc_events(url: str) -> list:
    data = get_xml_response(url)
    events = []
    for event in data["open511"]["events"]["event"]:
        events.append(
            RoadEvent(
                headline=event["headline"],
                description=event["description"],
                link="",
                created=event["created"],
                updated=event["updated"],
                type=event["event_type"],
                subtype="",
                latitude=0,
                longitude=0,
            )
        )
    return events


