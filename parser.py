import hashlib
from typing import Dict, List
from flashcard import Flashcard


def parse_markdown_file(filepath: str) -> List[Flashcard]:
    """
    Parse markdown file and create Flashcard objects.
    Pairs consecutive non-empty lines as term/definition.
    No deck headers - just term/definition pairs.
    Returns a list of flashcards.
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
        return []
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return []
    
    return flashcards

