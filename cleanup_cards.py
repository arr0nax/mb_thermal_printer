#!/usr/bin/env python3
"""Remove non-creature cards from the local cards.json database."""

import argparse
import json
import os
import tempfile
from pathlib import Path


def is_creature_record(card):
    type_line = card.get("type_line") or ""
    front_type_line = type_line.split(" // ", 1)[0]
    return "Creature" in front_type_line


def cleanup_cards(cards):
    kept = []
    removed = []
    for card in cards:
        if is_creature_record(card):
            kept.append(card)
        else:
            removed.append(card)
    return kept, removed


def write_cards(path, cards):
    directory = path.parent
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=directory,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as output:
        temporary_path = Path(output.name)
        json.dump(cards, output, separators=(",", ":"))
        output.write("\n")

    os.replace(temporary_path, path)


def main():
    parser = argparse.ArgumentParser(
        description="Remove cards that are not creatures from cards.json."
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=Path(__file__).resolve().parent / "cards.json",
        help="Path to the card database (default: cards.json next to this script)",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the cleaned records; without this option, only preview removals",
    )
    args = parser.parse_args()
    path = args.file.resolve()

    with path.open("r", encoding="utf-8") as source:
        cards = json.load(source)

    kept, removed = cleanup_cards(cards)
    print(f"Found {len(cards)} records; {len(removed)} would be removed")
    for card in removed:
        print(f"- {card.get('name', '<unnamed card>')}")

    if not args.write:
        print("Dry run only; use --write to update the file")
        return

    write_cards(path, kept)
    print(f"Wrote {len(kept)} creature records to {path}")


if __name__ == "__main__":
    main()