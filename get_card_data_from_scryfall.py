import os
import time
import datetime
import requests
import json

SEARCH_URL = 'https://api.scryfall.com/cards/search'
BASE_QUERY = 'type:creature (game:paper) (-is:digital -is:funny) is:firstprint is:notuniversesbeyond prefer:best'
CARDS_FILE = 'cards.json'
LAST_DATE_FILE = 'last_search_date.txt'
REQUEST_DELAY_SECONDS = 1
HEADERS = {
    'User-Agent': 'mb_thermal_printer/1.0',
    'Accept': 'application/json',
}


def get_art_url(card):
    if "image_uris" in card:
        return card["image_uris"].get("art_crop")
    # double faced cards carry their images per face instead of at the top level
    for face in card.get("card_faces", []):
        if "image_uris" in face:
            return face["image_uris"].get("art_crop")
    return None


def get_field(card, field):
    # double faced cards carry most gameplay fields per face instead of at the top level
    if field in card:
        return card[field]
    faces = card.get("card_faces")
    if faces:
        return faces[0].get(field)
    return None


def build_card_record(card):
    art_url = get_art_url(card)
    if not art_url:
        return None
    type_line = get_field(card, "type_line") or ""
    if "Creature" not in type_line:
        return None
    return {
        "id": card["id"],
        "name": card["name"],
        "mana_cost": get_field(card, "mana_cost"),
        "cmc": card.get("cmc"),
        "type_line": type_line,
        "oracle_text": get_field(card, "oracle_text"),
        "power": get_field(card, "power"),
        "toughness": get_field(card, "toughness"),
        "art_url": art_url,
    }


def is_creature_record(record):
    type_line = record.get("type_line") or ""
    front_type_line = type_line.split(" // ", 1)[0]
    return "Creature" in front_type_line


last_date = None
if os.path.exists(LAST_DATE_FILE):
    with open(LAST_DATE_FILE, 'r', encoding='utf-8') as fin:
        last_date = fin.read().strip() or None

cards_by_id = {}
if os.path.exists(CARDS_FILE):
    with open(CARDS_FILE, 'r', encoding='utf-8') as fin:
        cards_by_id = {
            card["id"]: card for card in json.load(fin)
            if is_creature_record(card)
        }

today = datetime.date.today().isoformat()

query = f"{BASE_QUERY} date<={today}"  # spoiled cards from unreleased sets have future dates
if last_date:
    query = f"{query} date>{last_date}"
    print(f"Searching for cards released after {last_date} and on or before {today}")
else:
    print(f"No previous search date found, fetching everything released on or before {today}")

new_count = 0
newest_date = last_date

url = SEARCH_URL
params = {
    'format': 'json',
    'include_extras': 'false',
    'include_multilingual': 'false',
    'include_variations': 'false',
    'order': 'name',
    'q': query,
    'unique': 'cards',
}
page = 0
completed = False

while url:
    time.sleep(REQUEST_DELAY_SECONDS)
    response = None
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        if response is not None and response.status_code == 404:
            print("No cards matched the search, nothing new to add")
            completed = True
        else:
            print(f"An error occurred while making the request: {e}")
        break

    response_dict = response.json()
    page += 1
    total_cards = response_dict.get("total_cards", 0)

    for card in response_dict.get("data", []):
        released_at = card.get("released_at")
        if released_at and (newest_date is None or released_at > newest_date):
            newest_date = released_at

        record = build_card_record(card)
        if not record:
            print(f"No art found for {card.get('name')}")
            continue

        cards_by_id[record["id"]] = record
        new_count += 1

    print(f"Page {page}: {new_count} new cards, {total_cards} matched the search")

    url = response_dict.get("next_page") if response_dict.get("has_more") else None
    params = None  # next_page already includes the query string
    if not url:
        completed = True

with open(CARDS_FILE, 'w') as fout:  # merge new cards into the permanent card database
    json.dump(list(cards_by_id.values()), fout)

# only advance the watermark on a clean run so a failure does not skip cards
if completed and newest_date:
    with open(LAST_DATE_FILE, 'w', encoding='utf-8') as fout:
        fout.write(newest_date)
    print(f"Saved latest release date {newest_date} to {LAST_DATE_FILE}")

print(f"Added {new_count} new cards, {len(cards_by_id)} total cards in {CARDS_FILE}")
