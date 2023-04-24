from helpers import get_xml_response


def get_major_drivebc_events(url: str):
    data = get_xml_response(url)
