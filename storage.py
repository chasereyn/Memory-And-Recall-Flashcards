import json
import os
from datetime import datetime
from typing import List, Optional
from flashcard import Flashcard


def ensure_data_directory():
    """Create data directory if it doesn't exist."""
    os.makedirs("data", exist_ok=True)


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
    
    data = {
        "cards": [card.to_dict() for card in cards],
        "last_session_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving cards to {filepath}: {e}")


def merge_cards(existing_cards: List[Flashcard], new_cards: List[Flashcard]) -> List[Flashcard]:
    """
    Merge new cards with existing cards.
    Preserves existing cards and their metadata.
    Appends new cards that don't exist yet (based on ID).
    """
    # Create a dictionary of existing cards by ID for quick lookup
    existing_dict = {card.id: card for card in existing_cards}
    
    # Start with existing cards (preserves order and numbering)
    merged = existing_cards.copy()
    
    # Add new cards that don't already exist
    for new_card in new_cards:
        if new_card.id not in existing_dict:
            merged.append(new_card)
    
    return merged


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

