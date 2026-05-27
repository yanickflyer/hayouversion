import requests
import json
from datetime import date

base_url = "https://api.youversion.com/v1/"


def get_verse_day(api_key: str):
    """Return (content, reference) for today's verse using the provided API key.

    Returns None on error.
    """
    if not api_key:
        return None

    headers = {"x-yvp-app-key": api_key}
    # elapsed day of the current year (1-365/366)
    get_day_current_year = int(date.today().timetuple().tm_yday)

    try:
        response = requests.get(base_url + f"verse_of_the_days/{get_day_current_year}", headers=headers, timeout=10)
        response.raise_for_status()
        verse = response.json()

        passage_id = verse.get("passage_id")
        if not passage_id:
            return None

        get_passage = requests.get(base_url + f"bibles/3034/passages/{passage_id}", headers=headers, timeout=10)
        get_passage.raise_for_status()
        passage = get_passage.json()

        return passage.get("content"), passage.get("reference")
    except Exception:
        return None