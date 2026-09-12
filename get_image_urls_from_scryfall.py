import time
import requests
import json

SEARCH_URL = 'https://api.scryfall.com/cards/search'
SEARCH_PARAMS = {
    'format': 'json',
    'include_extras': 'false',
    'include_multilingual': 'false',
    'include_variations': 'false',
    'order': 'name',
    'q': 'type:creature (game:paper) (-is:digital -is:funny -is:reprint) is:notuniversesbeyond prefer:best',
    'unique': 'cards',
}
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


image_urls = []
url = SEARCH_URL
params = SEARCH_PARAMS
page = 0

while url:
    time.sleep(0.1)  # scryfall asks for 50-100ms between requests
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the request: {e}")
        break

    response_dict = response.json()
    page += 1
    total_cards = response_dict.get("total_cards", 0)

    for card in response_dict.get("data", []):
        image_url = get_image_url(card)
        if not image_url:
            print(f"No image found for {card.get('name')}")
            continue
        image_urls.append({"name": card["name"], "image_url": image_url, "cmc": card.get("cmc")})

    print(f"Page {page}: collected {len(image_urls)} of {total_cards} cards")

    url = response_dict.get("next_page") if response_dict.get("has_more") else None
    params = None  # next_page already includes the query string

with open('creatures_image_urls.json', 'w') as fout:  # write image url's to json file
    json.dump(image_urls, fout)
