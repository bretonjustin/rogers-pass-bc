from dataclasses import dataclass


@dataclass
class Webcam:
    name: str
    latitude: float
    longitude: float
    altitude_m: int
    web_link: str