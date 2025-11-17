import os
from parser import parse_memory_file, parse_recall_file
from storage import load_cards, save_cards, merge_cards, ensure_data_directory, get_last_session_date
from spaced_repetition import (
    update_card_after_review,
    get_cards_for_review,
    reset_daily_flags,
    get_today
)


def initialize_memory_mode():
    """Initialize memory mode: parse file, load existing cards, merge, and save."""
    # Parse memory.txt
    new_cards = parse_memory_file("memory.txt")
    
    # Load existing cards
    filepath = "data/memory_cards.json"
    existing_cards = load_cards(filepath)
    
    # Merge cards (preserves existing, appends new)
    merged_cards = merge_cards(existing_cards, new_cards)
    
    # Save merged cards
    save_cards(merged_cards, filepath)
    
    return merged_cards, filepath


def initialize_recall_mode(deck_name: str):
    """Initialize recall mode for a specific deck."""
    # Parse recall.txt
    decks = parse_recall_file("recall.txt")
    
    if deck_name not in decks:
        print(f"Error: Deck '{deck_name}' not found in recall.txt")
        return [], None
    
    new_cards = decks[deck_name]
    
    # Load existing cards for this deck
    filepath = f"data/recall_{deck_name.lower()}_cards.json"
    existing_cards = load_cards(filepath)
    
    # Merge cards (preserves existing numbering, appends new)
    merged_cards = merge_cards(existing_cards, new_cards)
    
    # Save merged cards
    save_cards(merged_cards, filepath)
    
    return merged_cards, filepath


def get_user_rating() -> int:
    """Get user rating (1-4) with validation."""
    while True:
        try:
            rating = input("Rate difficulty (1=Hard/Repeat, 2=Medium-Hard, 3=Medium, 4=Easy, or 'quit'): ").strip().lower()
            if rating == 'quit':
                return None
            rating = int(rating)
            if rating in [1, 2, 3, 4]:
                return rating
            else:
                print("Please enter a number between 1 and 4, or 'quit'.")
        except ValueError:
            print("Please enter a valid number (1-4) or 'quit'.")
        except KeyboardInterrupt:
            print("\nExiting...")
            return None


def review_session(cards, filepath):
    """Run a review session with the given cards."""
    today = get_today()
    last_session_date = get_last_session_date(filepath)
    
    # Reset daily flags if new day
    reset_daily_flags(cards, last_session_date, today)
    
    # Get cards ready for review
    review_cards = get_cards_for_review(cards, today)
    
    if not review_cards:
        print("\n" + "=" * 50)
        print("No cards due for review!")
        print("=" * 50)
        return
    
    print("\n" + "=" * 50)
    print(f"Starting review session - {len(review_cards)} card(s) ready")
    print("=" * 50)
    print("\nInstructions:")
    print("  - Press Enter to see the definition")
    print("  - Rate the card: 1=Hard/Repeat, 2=Medium-Hard, 3=Medium, 4=Easy")
    print("  - Cards rated 1-3 will be shown again until you rate them 4")
    print("  - Type 'quit' at any time to exit\n")
    
    cards_reviewed = 0
    cards_completed = 0
    
    # Create a dictionary for quick card lookup by ID
    card_dict = {card.id: card for card in cards}
    
    while review_cards:
        # Get next card (prioritized)
        current_card = review_cards[0]
        
        print("-" * 50)
        print(f"Card {cards_reviewed + 1} of {len(review_cards)}")
        print(f"Term: {current_card.term}")
        print("-" * 50)
        
        # Wait for user to press Enter to see definition
        input("Press Enter to reveal definition...")
        
        print(f"\nDefinition: {current_card.definition}")
        print()
        
        # Get rating
        rating = get_user_rating()
        if rating is None:
            break
        
        # Update card
        update_card_after_review(current_card, rating)
        cards_reviewed += 1
        
        # Save immediately after each review
        save_cards(cards, filepath)
        
        # Remove card from review list if completed (rated 4)
        if current_card.completed_today:
            cards_completed += 1
            print(f"\nCard completed! Next review in {current_card.interval} day(s).")
        else:
            print(f"\nCard will be shown again (attempt {current_card.session_attempts}).")
        
        # If card got rating 1, show it again immediately (next in queue)
        if rating == 1 and not current_card.completed_today:
            # Card stays in queue and will be shown again
            # Refresh list but keep this card at the front
            review_cards = get_cards_for_review(cards, today)
            # Move current card to front if it's still in the list
            if current_card.id in [c.id for c in review_cards]:
                review_cards = [c for c in review_cards if c.id == current_card.id] + [c for c in review_cards if c.id != current_card.id]
        else:
            # Refresh review list (cards may have changed priority)
            review_cards = get_cards_for_review(cards, today)
            
            # Remove current card if it's completed
            if current_card.completed_today:
                review_cards = [c for c in review_cards if c.id != current_card.id]
        
        print()
    
    print("=" * 50)
    print(f"Session complete!")
    print(f"  Cards reviewed: {cards_reviewed}")
    print(f"  Cards completed: {cards_completed}")
    print("=" * 50)


def run_memory_mode():
    """Run memory mode review session."""
    print("\n" + "=" * 50)
    print("Memory Mode")
    print("=" * 50)
    
    cards, filepath = initialize_memory_mode()
    print(f"Loaded {len(cards)} total cards")
    
    review_session(cards, filepath)


def run_recall_mode():
    """Run recall mode review session."""
    print("\n" + "=" * 50)
    print("Recall Mode")
    print("=" * 50)
    
    # Parse to see available decks
    decks = parse_recall_file("recall.txt")
    
    if not decks:
        print("No decks found in recall.txt")
        return
    
    # Show deck selection
    print("\nAvailable decks:")
    deck_names = list(decks.keys())
    for i, deck_name in enumerate(deck_names, 1):
        print(f"  {i}. {deck_name}")
    
    while True:
        try:
            choice = input(f"\nSelect deck (1-{len(deck_names)}): ").strip()
            choice = int(choice)
            if 1 <= choice <= len(deck_names):
                selected_deck = deck_names[choice - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(deck_names)}.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nExiting...")
            return
    
    cards, filepath = initialize_recall_mode(selected_deck)
    
    if not cards:
        return
    
    print(f"Loaded {len(cards)} cards from {selected_deck} deck")
    
    review_session(cards, filepath)


def main():
    """Main entry point with mode selection."""
    ensure_data_directory()
    
    print("=" * 50)
    print("Flashcard Program - Spanish Learning")
    print("=" * 50)
    
    while True:
        print("\nSelect mode:")
        print("  1. Memory Mode (English <-> Spanish)")
        print("  2. Recall Mode (Numbered phrases)")
        print("  3. Exit")
        
        try:
            choice = input("\nEnter choice (1-3): ").strip()
            
            if choice == "1":
                run_memory_mode()
            elif choice == "2":
                run_recall_mode()
            elif choice == "3":
                print("\nGoodbye!")
                break
            else:
                print("Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
