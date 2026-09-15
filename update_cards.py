#!/usr/bin/env python3
"""Fetch new creature cards and prepare their art for printing."""

import argparse
import datetime
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import requests

SEARCH_URL = "https://api.scryfall.com/cards/search"
BASE_QUERY = (
    "type:creature (game:paper) (-is:digital -is:funny) "
    "is:firstprint is:notuniversesbeyond prefer:best"
)
REQUEST_DELAY_SECONDS = 1
HEADERS = {
    "User-Agent": "mb_thermal_printer/1.0",
    "Accept": "application/json",
}
PROJECT_ROOT = Path(__file__).resolve().parent
CARDS_FILE = PROJECT_ROOT / "cards.json"
LAST_DATE_FILE = PROJECT_ROOT / "last_search_date.txt"
ART_ROOT = PROJECT_ROOT / "art"


def get_field(card, field):
    if field in card:
        return card[field]
    faces = card.get("card_faces")
    if faces:
        return faces[0].get(field)
    return None


def get_art_url(card):
    if "image_uris" in card:
        return card["image_uris"].get("art_crop")
    for face in card.get("card_faces", []):
        if "image_uris" in face:
            return face["image_uris"].get("art_crop")
    return None


def is_front_face_creature(type_line):
    return "Creature" in (type_line or "").split(" // ", 1)[0]


def build_card_record(card):
    art_url = get_art_url(card)
    type_line = get_field(card, "type_line") or ""
    if not art_url or not is_front_face_creature(type_line):
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
    return is_front_face_creature(record.get("type_line"))


def read_cards(path):
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as source:
        return {
            card["id"]: card
            for card in json.load(source)
            if is_creature_record(card)
        }


def read_last_date(path):
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").strip() or None


def fetch_new_cards(last_date, cmc=None):
    today = datetime.date.today().isoformat()
    query = f"{BASE_QUERY} date<={today}"
    if last_date:
        query = f"{query} date>{last_date}"
        print(f"Searching for cards released after {last_date} and on or before {today}")
    else:
        print(f"No previous search date found; fetching cards released on or before {today}")
    if cmc is not None:
        query = f"{query} cmc={cmc}"
        print(f"Limiting this update to mana value {cmc}")

    url = SEARCH_URL
    params = {
        "format": "json",
        "include_extras": "false",
        "include_multilingual": "false",
        "include_variations": "false",
        "order": "name",
        "q": query,
        "unique": "cards",
    }
    records = []
    newest_date = last_date
    page = 0

    while url:
        time.sleep(REQUEST_DELAY_SECONDS)
        response = requests.get(url, params=params, headers=HEADERS, timeout=30)
        if response.status_code == 404:
            print("No cards matched the search")
            return records, newest_date
        response.raise_for_status()
        response_data = response.json()
        page += 1

        for card in response_data.get("data", []):
            released_at = card.get("released_at")
            if released_at and (newest_date is None or released_at > newest_date):
                newest_date = released_at
            record = build_card_record(card)
            if record:
                records.append(record)
            else:
                print(f"Skipping {card.get('name', '<unnamed card>')}: no front-face creature art")

        print(f"Fetched page {page} of {response_data.get('total_cards', 0)} matching cards")
        url = response_data.get("next_page") if response_data.get("has_more") else None
        params = None

    return records, newest_date


def image_paths(record):
    directory = ART_ROOT / str(int(record["cmc"]))
    return directory / f"{record['id']}.jpg", directory / "converted_files" / f"{record['id']}.bmp"


def download_art(record, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return

    temporary_path = destination.with_suffix(".jpg.tmp")
    try:
        with requests.get(record["art_url"], headers=HEADERS, timeout=60, stream=True) as response:
            response.raise_for_status()
            with temporary_path.open("wb") as output:
                for chunk in response.iter_content(chunk_size=64 * 1024):
                    output.write(chunk)
        os.replace(temporary_path, destination)
        print(f"Downloaded {record['name']}")
    finally:
        temporary_path.unlink(missing_ok=True)


def find_imagemagick():
    magick = shutil.which("magick")
    if magick:
        return [magick]
    convert = shutil.which("convert")
    if convert:
        return [convert]
    raise RuntimeError("ImageMagick is required; install it so 'magick' or 'convert' is available")


def convert_art(source, destination, imagemagick):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return

    with tempfile.NamedTemporaryFile(
        dir=destination.parent,
        prefix=f".{destination.stem}.",
        suffix=".bmp",
        delete=False,
    ) as temporary_file:
        temporary_path = Path(temporary_file.name)

    try:
        subprocess.run(
            imagemagick
            + [
                str(source),
                "-resize",
                "384x",
                "-colorspace",
                "Gray",
                "+level",
                "20%,100%",
                "-gamma",
                "2.0",
                "-ordered-dither",
                "o8x8",
                str(temporary_path),
            ],
            check=True,
        )
        os.replace(temporary_path, destination)
        print(f"Converted {source.name} to {destination}")
    finally:
        temporary_path.unlink(missing_ok=True)


def write_json(path, value):
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as output:
        temporary_path = Path(output.name)
        json.dump(value, output, separators=(",", ":"))
        output.write("\n")
    os.replace(temporary_path, path)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch new creature cards, download their art, and convert it for printing."
    )
    parser.add_argument("--cards-file", type=Path, default=CARDS_FILE)
    parser.add_argument("--last-date-file", type=Path, default=LAST_DATE_FILE)
    parser.add_argument(
        "--cmc",
        type=int,
        choices=range(0, 101),
        metavar="N",
        help="Only fetch and prepare cards with this mana value",
    )
    args = parser.parse_args()

    cards_path = args.cards_file.resolve()
    last_date_path = args.last_date_file.resolve()
    cards_by_id = read_cards(cards_path)
    last_date = read_last_date(last_date_path)
    fetched_records, newest_date = fetch_new_cards(last_date, cmc=args.cmc)
    new_records = [record for record in fetched_records if record["id"] not in cards_by_id]

    if new_records:
        imagemagick = find_imagemagick()
        print(f"Preparing art for {len(new_records)} new cards")
        for index, record in enumerate(new_records, start=1):
            jpg_path, bmp_path = image_paths(record)
            download_art(record, jpg_path)
            convert_art(jpg_path, bmp_path, imagemagick)
            print(f"Prepared {index}/{len(new_records)}: {record['name']}")

    for record in fetched_records:
        cards_by_id[record["id"]] = record
    write_json(cards_path, list(cards_by_id.values()))

    if newest_date and args.cmc is None:
        last_date_path.write_text(newest_date, encoding="utf-8")
        print(f"Saved latest release date {newest_date}")
    elif args.cmc is not None:
        print("Kept the release-date watermark unchanged after the scoped update")

    print(f"Added {len(new_records)} new cards; {len(cards_by_id)} total cards")


if __name__ == "__main__":
    main()