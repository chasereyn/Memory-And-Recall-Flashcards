import json
import os
import glob
from datetime import datetime
from typing import List, Optional, Tuple
from flashcard import Flashcard
from parser import parse_markdown_file


def ensure_data_directory():
    """Create data directory and decks subdirectory if they don't exist."""
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/decks", exist_ok=True)


def get_deck_name_from_file(filename: str) -> str:
    """Extract deck name from filename (e.g., 'spanish_vocab.md' -> 'spanish_vocab')."""
    # Remove .md extension and return
    if filename.endswith('.md'):
        return filename[:-3]
    return filename


def get_markdown_files() -> List[str]:
    """Get all .md files in the data directory."""
    markdown_files = []
    data_dir = "data"
    
    if os.path.exists(data_dir):
        # Find all .md files in data/ (not in subdirectories)
        pattern = os.path.join(data_dir, "*.md")
        markdown_files = [os.path.basename(f) for f in glob.glob(pattern)]
    
    return markdown_files


def load_cards(filepath: str) -> List[Flashcard]:
    """
    Load flashcards from JSON file.
    Returns empty list if file doesn't exist.
    """
    if not os.path.exists(filepath):
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cards = []
        for card_data in data.get("cards", []):
            cards.append(Flashcard.from_dict(card_data))
        
        return cards
    except Exception as e:
        print(f"Error loading cards from {filepath}: {e}")
        return []


def save_cards(cards: List[Flashcard], filepath: str):
    """Save flashcards to JSON file."""
    ensure_data_directory()
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    data = {
        "cards": [card.to_dict() for card in cards],
        "last_session_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving cards to {filepath}: {e}")


def sync_deck_from_markdown(markdown_path: str, deck_name: str) -> Tuple[int, int, int]:
    """
    Sync a deck from markdown file to JSON file.
    
    Args:
        markdown_path: Path to the markdown file
        deck_name: Name of the deck (used for JSON filename)
    
    Returns:
        Tuple of (preserved_count, added_count, removed_count)
    """
    # Parse markdown to get cards
    markdown_cards = parse_markdown_file(markdown_path)
    markdown_ids = {card.id for card in markdown_cards}
    
    # Load existing JSON cards
    json_path = f"data/decks/{deck_name}.json"
    existing_cards = load_cards(json_path)
    existing_ids = {card.id for card in existing_cards}
    
    # Create a dictionary of existing cards by ID for quick lookup
    existing_dict = {card.id: card for card in existing_cards}
    
    # Build synced cards list
    synced_cards = []
    preserved_count = 0
    added_count = 0
    
    # Keep cards that exist in both (preserve metadata from JSON)
    for card_id in markdown_ids:
        if card_id in existing_dict:
            # Card exists in both - preserve from JSON (has metadata)
            synced_cards.append(existing_dict[card_id])
            preserved_count += 1
        else:
            # New card from markdown
            # Find the card from markdown_cards list
            new_card = next(c for c in markdown_cards if c.id == card_id)
            synced_cards.append(new_card)
            added_count += 1
    
    # Calculate removed count (cards in JSON but not in markdown)
    removed_count = len(existing_ids - markdown_ids)
    
    # Save synced cards
    save_cards(synced_cards, json_path)
    
    return preserved_count, added_count, removed_count


def sync_all_decks():
    """Sync all markdown files in data/ with their corresponding JSON files in data/decks/."""
    ensure_data_directory()
    
    markdown_files = get_markdown_files()
    
    if not markdown_files:
        print("No markdown files found in data/ directory.")
        return
    
    print("\n" + "=" * 50)
    print("Syncing decks from markdown files...")
    print("=" * 50)
    
    total_preserved = 0
    total_added = 0
    total_removed = 0
    
    for md_file in sorted(markdown_files):
        deck_name = get_deck_name_from_file(md_file)
        markdown_path = os.path.join("data", md_file)
        
        try:
            preserved, added, removed = sync_deck_from_markdown(markdown_path, deck_name)
            
            print(f"\n{deck_name}:")
            print(f"  Preserved: {preserved} cards")
            print(f"  Added: {added} cards")
            print(f"  Removed: {removed} cards")
            
            total_preserved += preserved
            total_added += added
            total_removed += removed
            
        except Exception as e:
            print(f"\nError syncing {deck_name}: {e}")
            continue
    
    print("\n" + "=" * 50)
    print("Sync complete!")
    print(f"Total preserved: {total_preserved} cards")
    print(f"Total added: {total_added} cards")
    print(f"Total removed: {total_removed} cards")
    print("=" * 50)


def get_last_session_date(filepath: str) -> Optional[str]:
    """Get the last session date from JSON file."""
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("last_session_date")
    except Exception:
        return None
