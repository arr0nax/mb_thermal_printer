import os
import time
import requests
import json

SEARCH_URL = 'https://api.scryfall.com/cards/search'
BASE_QUERY = 'type:creature (game:paper) (-is:digital -is:funny) is:firstprint is:notuniversesbeyond prefer:best'
OUTPUT_FILE = 'creatures_image_urls.json'
LAST_DATE_FILE = 'last_search_date.txt'
HEADERS = {
    'User-Agent': 'mb_thermal_printer/1.0',
    'Accept': 'application/json',
}


def get_image_url(card):
    if "image_uris" in card:
        return card["image_uris"].get("large")
    # double faced cards carry their images per face instead of at the top level
    for face in card.get("card_faces", []):
        if "image_uris" in face:
            return face["image_uris"].get("large")
    return None


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, 'r', encoding='utf-8') as fin:
        return json.load(fin)


last_date = None
if os.path.exists(LAST_DATE_FILE):
    with open(LAST_DATE_FILE, 'r', encoding='utf-8') as fin:
        last_date = fin.read().strip() or None

query = BASE_QUERY
if last_date:
    query = f"{query} date>{last_date}" 
    print(f"Searching for cards released on or after {last_date}")
else:
    print("No previous search date found, fetching everything")

image_urls = load_json(OUTPUT_FILE, [])
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
    time.sleep(0.1)  # scryfall asks for 50-100ms between requests
    response = None
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        if response is not None and response.status_code == 404:
            print("No cards matched the search, nothing new to download")
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

        image_url = get_image_url(card)
        if not image_url:
            print(f"No image found for {card.get('name')}")
            continue

        image_urls.append({"name": card["name"], "image_url": image_url, "cmc": card.get("cmc")})
        new_count += 1

    print(f"Page {page}: {new_count} new cards, {total_cards} matched the search")

    url = response_dict.get("next_page") if response_dict.get("has_more") else None
    params = None  # next_page already includes the query string
    if not url:
        completed = True

# the date filter is inclusive, so cards released on the watermark day come back each run
image_urls = list({card["name"]: card for card in image_urls}.values())

with open(OUTPUT_FILE, 'w') as fout:  # write image url's to json file
    json.dump(image_urls, fout)

# only advance the watermark on a clean run so a failure does not skip cards
if completed and newest_date:
    with open(LAST_DATE_FILE, 'w', encoding='utf-8') as fout:
        fout.write(newest_date)
    print(f"Saved latest release date {newest_date} to {LAST_DATE_FILE}")

print(f"Added {new_count} new cards, {len(image_urls)} total in {OUTPUT_FILE}")
