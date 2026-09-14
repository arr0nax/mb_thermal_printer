import os
import urllib.request
import json

ART_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "art")
CARDS_FILE = 'cards.json'


def download_art_from_json(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for item in data:
            download_art(item)


def download_art(item):
    url = item["art_url"]
    cmc = int(item["cmc"])
    card_id = item["id"]

    directory = os.path.join(ART_ROOT, str(cmc))
    if not os.path.exists(directory):
        os.makedirs(directory)

    save_path = os.path.join(directory, f"{card_id}.jpg")
    if os.path.exists(save_path):
        return

    try:
        urllib.request.urlretrieve(url, save_path)
        print(f"Downloaded {item['name']} ({card_id}) to {save_path}")
    except Exception as e:
        print(f"Failed to download {item['name']} ({card_id}): {e}")


# Usage
download_art_from_json(CARDS_FILE)
