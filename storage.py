import csv
import glob
import json
import os
from datetime import datetime
from typing import List, Optional, Tuple

from flashcard import Flashcard
from parser import parse_deck_tsv, write_deck_tsv

PROGRESS_FIELDNAMES = [
    "id",
    "next_review",
    "ease_factor",
    "interval",
    "difficulty",
    "completed_today",
    "first_rating",
    "session_attempts",
    "consecutive_easy_sessions",
    "latest_rating",
    "term",
    "definition",
]

SESSION_DATE_PREFIX = "# last_session_date: "

DEFAULT_EASE_FACTOR = 2.5
DEFAULT_INTERVAL = 1


def has_progress(card: Flashcard) -> bool:
    """True if the card has review state beyond factory defaults."""
    return (
        card.next_review is not None
        or card.ease_factor != DEFAULT_EASE_FACTOR
        or card.interval != DEFAULT_INTERVAL
        or card.difficulty != 0
        or card.completed_today
        or card.first_rating is not None
        or card.session_attempts != 0
        or card.consecutive_easy_sessions != 0
        or card.latest_rating is not None
    )


def _merge_progress(card: Flashcard, saved: Flashcard) -> None:
    card.next_review = saved.next_review
    card.ease_factor = saved.ease_factor
    card.interval = saved.interval
    card.difficulty = saved.difficulty
    card.completed_today = saved.completed_today
    card.first_rating = saved.first_rating
    card.session_attempts = saved.session_attempts
    card.consecutive_easy_sessions = saved.consecutive_easy_sessions
    card.latest_rating = saved.latest_rating


def ensure_data_directory():
    """Create data directories if they don't exist."""
    os.makedirs("data/decks", exist_ok=True)
    os.makedirs("data/progress", exist_ok=True)


def deck_content_path(deck_name: str) -> str:
    return f"data/decks/{deck_name}.tsv"


def deck_progress_path(deck_name: str) -> str:
    return f"data/progress/{deck_name}.tsv"


def get_deck_name_from_file(filename: str) -> str:
    """Extract deck name (e.g. 'spanish.tsv' or 'data/progress/spanish.tsv' -> 'spanish')."""
    filename = os.path.basename(filename)
    for suffix in (".tsv", ".txt"):
        if filename.endswith(suffix):
            return filename[: -len(suffix)]
    return filename


def get_deck_files() -> List[str]:
    """Get deck content TSV filenames in data/decks/."""
    pattern = os.path.join("data", "decks", "*.tsv")
    return [os.path.basename(f) for f in glob.glob(pattern)]


def _serialize_value(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _parse_optional_int(value: str) -> Optional[int]:
    value = (value or "").strip()
    if not value:
        return None
    return int(value)


def _parse_bool(value: str) -> bool:
    return (value or "").strip().lower() in ("true", "1", "yes")


def _apply_progress(card: Flashcard, row: dict) -> None:
    card.term = row.get("term") or card.term
    card.definition = row.get("definition") or card.definition
    card.next_review = row.get("next_review") or None
    card.ease_factor = float(row.get("ease_factor") or 2.5)
    card.interval = int(row.get("interval") or 1)
    card.difficulty = int(row.get("difficulty") or 0)
    card.completed_today = _parse_bool(row.get("completed_today", ""))
    card.first_rating = _parse_optional_int(row.get("first_rating", ""))
    card.session_attempts = int(row.get("session_attempts") or 0)
    card.consecutive_easy_sessions = int(row.get("consecutive_easy_sessions") or 0)
    card.latest_rating = _parse_optional_int(row.get("latest_rating", ""))


def load_progress(deck_name: str) -> Tuple[dict[str, Flashcard], Optional[str]]:
    """Load progress metadata keyed by card id. Returns (progress_dict, last_session_date)."""
    path = deck_progress_path(deck_name)
    if not os.path.exists(path):
        return {}, None

    progress = {}
    last_session_date = None

    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            for line in f:
                if line.startswith(SESSION_DATE_PREFIX):
                    last_session_date = line[len(SESSION_DATE_PREFIX) :].strip()
                    break

        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(
                (row for row in f if not row.startswith("#")),
                delimiter="\t",
            )
            for row in reader:
                if not row.get("id"):
                    continue
                card = Flashcard(id=row["id"], term="", definition="")
                _apply_progress(card, row)
                progress[card.id] = card
    except Exception as e:
        print(f"Error loading progress from {path}: {e}")
        return {}, last_session_date

    return progress, last_session_date


def load_cards(filepath: str) -> List[Flashcard]:
    """
    Load flashcards for a deck by merging content TSV + progress TSV.
    filepath should be the progress path (legacy signature kept for main.py).
    """
    deck_name = os.path.basename(filepath).replace(".tsv", "").replace(".json", "")
    content_path = deck_content_path(deck_name)

    if not os.path.exists(content_path):
        return []

    content_cards = parse_deck_tsv(content_path)
    progress, _ = load_progress(deck_name)

    cards = []
    for card in content_cards:
        if card.id in progress:
            _merge_progress(card, progress[card.id])
        cards.append(card)

    return cards


def delete_card(cards: List[Flashcard], deck_name: str, card_id: str) -> List[Flashcard]:
    """Remove a card from deck content and return the updated in-memory list."""
    remaining = [card for card in cards if card.id != card_id]
    write_deck_tsv(deck_content_path(deck_name), remaining)
    return remaining


def _progress_row(card: Flashcard) -> dict:
    return {
        "id": card.id,
        "next_review": _serialize_value(card.next_review),
        "ease_factor": _serialize_value(card.ease_factor),
        "interval": _serialize_value(card.interval),
        "difficulty": _serialize_value(card.difficulty),
        "completed_today": _serialize_value(card.completed_today),
        "first_rating": _serialize_value(card.first_rating),
        "session_attempts": _serialize_value(card.session_attempts),
        "consecutive_easy_sessions": _serialize_value(card.consecutive_easy_sessions),
        "latest_rating": _serialize_value(card.latest_rating),
        "term": card.term,
        "definition": card.definition,
    }


def save_cards(cards: List[Flashcard], filepath: str, update_session_date: bool = True):
    """Save review progress to TSV (content file is edited separately)."""
    ensure_data_directory()
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    deck_name = os.path.basename(filepath).replace(".tsv", "").replace(".json", "")
    filepath = deck_progress_path(deck_name)

    if update_session_date:
        last_session_date = datetime.now().strftime("%Y-%m-%d")
    else:
        _, last_session_date = load_progress(deck_name)

    touched = [card for card in cards if has_progress(card)]
    if not touched and last_session_date is None:
        if os.path.exists(filepath):
            os.remove(filepath)
        return

    try:
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            if last_session_date is not None:
                f.write(f"{SESSION_DATE_PREFIX}{last_session_date}\n")
            writer = csv.DictWriter(f, fieldnames=PROGRESS_FIELDNAMES, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            for card in touched:
                writer.writerow(_progress_row(card))
    except Exception as e:
        print(f"Error saving progress to {filepath}: {e}")


def sync_deck(deck_name: str) -> Tuple[int, int, int]:
    """
    Sync deck content TSV with progress TSV.

    Returns:
        Tuple of (preserved_count, added_count, removed_count)
    """
    content_path = deck_content_path(deck_name)
    content_cards = parse_deck_tsv(content_path)
    content_ids = {card.id for card in content_cards}

    progress_dict, _ = load_progress(deck_name)
    existing_ids = set(progress_dict)

    synced_cards = []
    preserved_count = 0
    added_count = 0

    for card in content_cards:
        if card.id in progress_dict:
            _merge_progress(card, progress_dict[card.id])
            synced_cards.append(card)
            preserved_count += 1
        else:
            synced_cards.append(card)
            added_count += 1

    removed_count = len(existing_ids - content_ids)
    touched_cards = [card for card in synced_cards if has_progress(card)]
    save_cards(touched_cards, deck_progress_path(deck_name), update_session_date=False)

    return preserved_count, added_count, removed_count


def sync_all_decks():
    """Sync all deck TSV files in data/decks/ with their progress files."""
    ensure_data_directory()

    deck_files = get_deck_files()
    if not deck_files:
        print("No deck TSV files found in data/decks/.")
        return

    print("\nSyncing decks...")

    total_preserved = 0
    total_added = 0
    total_removed = 0

    for deck_file in sorted(deck_files):
        deck_name = get_deck_name_from_file(deck_file)
        try:
            preserved, added, removed = sync_deck(deck_name)
            total_preserved += preserved
            total_added += added
            total_removed += removed
        except Exception as e:
            print(f"\nError syncing {deck_name}: {e}")
            continue

    print("Sync complete!")
    print(f"Total preserved: {total_preserved} cards")
    print(f"Total added: {total_added} cards")
    print(f"Total removed: {total_removed} cards")


def get_last_session_date(filepath: str) -> Optional[str]:
    """Get the last session date from a progress TSV file."""
    deck_name = os.path.basename(filepath).replace(".tsv", "").replace(".json", "")
    path = deck_progress_path(deck_name)

    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(SESSION_DATE_PREFIX):
                    return line[len(SESSION_DATE_PREFIX) :].strip()
    except Exception:
        return None

    return None


def load_legacy_json_cards(json_path: str) -> Tuple[List[Flashcard], Optional[str]]:
    """Load cards from legacy JSON format (used by convert_decks.py)."""
    if not os.path.exists(json_path):
        return [], None

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cards = [Flashcard.from_dict(row) for row in data.get("cards", [])]
    return cards, data.get("last_session_date")
