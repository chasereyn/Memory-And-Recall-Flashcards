import hashlib
from typing import List, Dict
from flashcard import Flashcard


def parse_memory_file(filepath: str = "memory.txt") -> List[Flashcard]:
    """
    Parse memory.txt file and create Flashcard objects.
    Pairs consecutive non-empty lines as term/definition.
    """
    flashcards = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]
        
        i = 0
        while i < len(lines):
            # Skip blank lines
            if not lines[i]:
                i += 1
                continue
            
            # Get term (current line)
            term = lines[i]
            i += 1
            
            # Skip to next non-empty line for definition
            while i < len(lines) and not lines[i]:
                i += 1
            
            # If we have a definition, create flashcard
            if i < len(lines):
                definition = lines[i]
                
                # Generate unique ID using hash of term+definition
                id_string = f"{term}|{definition}"
                card_id = hashlib.md5(id_string.encode('utf-8')).hexdigest()[:12]
                
                # Check if card already exists in our list (avoid duplicates)
                if not any(card.id == card_id for card in flashcards):
                    flashcard = Flashcard(
                        id=card_id,
                        term=term,
                        definition=definition
                    )
                    flashcards.append(flashcard)
                
                i += 1
    
    except FileNotFoundError:
        print(f"Warning: {filepath} not found.")
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
    
    return flashcards


def parse_recall_file(filepath: str = "recall.txt") -> Dict[str, List[Flashcard]]:
    """
    Parse recall.txt file and create Flashcard objects for each deck.
    Returns a dictionary with deck names as keys and lists of flashcards as values.
    """
    decks = {}
    current_deck = None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]
        
        for line in lines:
            # Check if line is a deck header
            if line.startswith('[') and line.endswith(']'):
                deck_name = line[1:-1]  # Remove brackets
                current_deck = deck_name
                decks[current_deck] = []
                continue
            
            # Skip blank lines
            if not line or not current_deck:
                continue
            
            # Create flashcard with number as term and phrase as definition
            # Number is based on position in the deck (1-indexed)
            phrase_number = len(decks[current_deck]) + 1
            card_id = f"{current_deck.lower()}_{phrase_number}"
            
            flashcard = Flashcard(
                id=card_id,
                term=str(phrase_number),
                definition=line
            )
            decks[current_deck].append(flashcard)
    
    except FileNotFoundError:
        print(f"Warning: {filepath} not found.")
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
    
    return decks

