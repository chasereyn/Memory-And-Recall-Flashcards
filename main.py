import os
from storage import (
    load_cards, 
    save_cards, 
    ensure_data_directory, 
    get_last_session_date,
    sync_all_decks,
    get_text_files,
    get_deck_name_from_file
)
from spaced_repetition import (
    update_card_after_review,
    get_cards_for_review,
    reset_daily_flags,
    get_today,
)
import random


def initialize(deck_name: str):
    """Load cards for a specific deck from JSON file."""
    json_path = f"data/decks/{deck_name}.json"
    cards = load_cards(json_path)
    
    if not cards:
        print(f"Error: No cards found for deck '{deck_name}'")
        return [], None
    
    return cards, json_path


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
    
    initial_card_count = len(review_cards)
    cards_completed = 0
    total_reviews = 0  # Total number of times cards were shown
    
    # Create a dictionary for quick card lookup by ID
    card_dict = {card.id: card for card in cards}
    
    while review_cards:
        # Get next card (prioritized)
        current_card = review_cards[0]
        cards_remaining = len(review_cards)
        
        print("-" * 50)
        print(f"{cards_remaining} card(s) remaining")
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
        total_reviews += 1
        
        # Save immediately after each review
        save_cards(cards, filepath)
        
        # Remove card from review list if completed (rated 4)
        if current_card.completed_today:
            cards_completed += 1
            print(f"\nCard completed! Next review in {current_card.interval} day(s).")
        else:
            print(f"\nCard will be shown again (attempt {current_card.session_attempts}).")
        
        # Handle card re-insertion based on rating
        if rating == 1 and not current_card.completed_today:
            # Rating 1: Show immediately (move to front)
            # Remove from current position and insert at front
            review_cards = [c for c in review_cards if c.id != current_card.id]
            review_cards.insert(0, current_card)
        elif rating in [2, 3] and not current_card.completed_today:
            # Rating 2/3: Insert at random position within fixed range
            # This prevents cards from being buried thousands of positions back in large decks
            # Remove from current position first
            review_cards = [c for c in review_cards if c.id != current_card.id]
            
            if len(review_cards) > 0:
                if rating == 2:
                    # Rating 2: Random position between 10-25 cards ahead (clamped to deck size)
                    min_pos = min(10, len(review_cards))
                    max_pos = min(25, len(review_cards))
                else:  # rating == 3
                    # Rating 3: Random position between 20-40 cards ahead (clamped to deck size)
                    min_pos = min(20, len(review_cards))
                    max_pos = min(40, len(review_cards))
                
                # Insert at random position within range, or append if range is invalid
                if min_pos <= max_pos:
                    insert_pos = random.randint(min_pos, max_pos)
                    review_cards.insert(insert_pos, current_card)
                else:
                    # If deck is smaller than minimum, append to end
                    review_cards.append(current_card)
            else:
                # If queue is empty, just add it
                review_cards.append(current_card)
        elif current_card.completed_today:
            # Rating 4: Card is completed, remove from queue
            # Simply remove it - no need to refresh entire queue
            review_cards = [c for c in review_cards if c.id != current_card.id]
        else:
            # Fallback: remove card (shouldn't happen, but be safe)
            review_cards = [c for c in review_cards if c.id != current_card.id]
        
        print()
    
    # Session complete message
    print("\n" + "=" * 50)
    if cards_completed == initial_card_count:
        print("Excellent! All cards completed for this session!")
    elif cards_completed > 0:
        print(f"Session complete! {cards_completed} card(s) mastered!")
    else:
        print("Session paused. Progress saved!")
    print("=" * 50)
    print(f"  Cards completed: {cards_completed} / {initial_card_count}")
    print(f"  Total reviews: {total_reviews}")
    if cards_completed < initial_card_count:
        remaining = initial_card_count - cards_completed
        print(f"  Cards remaining: {remaining}")
    print("=" * 50)


def get_available_decks():
    """Get list of available deck names from text files."""
    text_files = get_text_files()
    deck_names = [get_deck_name_from_file(f) for f in text_files]
    return sorted(deck_names)


def select_deck():
    """Show deck selection menu and return selected deck name, or None if user wants to exit."""
    # Get available decks from text files
    deck_names = get_available_decks()
    
    if not deck_names:
        print("No decks found. Add .txt files to the data/ directory.")
        return None
    
    # Get today's date for calculating due cards
    today = get_today()
    
    # Calculate deck info (due cards and total cards)
    deck_info = []
    for deck_name in deck_names:
        json_path = f"data/decks/{deck_name}.json"
        cards = load_cards(json_path)
        total_count = len(cards)
        
        # Reset daily flags if it's a new day (for accurate counts)
        last_session_date = get_last_session_date(json_path)
        reset_daily_flags(cards, last_session_date, today)
        
        # Get cards due for review
        due_cards = get_cards_for_review(cards, today)
        due_count = len(due_cards)
        
        deck_info.append({
            'name': deck_name,
            'due': due_count,
            'total': total_count
        })
    
    # Find max widths for formatting
    max_name_len = max(len(info['name']) for info in deck_info) if deck_info else 0
    max_due_digits = max(len(str(info['due'])) for info in deck_info) if deck_info else 0
    max_total_digits = max(len(str(info['total'])) for info in deck_info) if deck_info else 0
    
    # Show deck selection with formatted columns
    print("\nAvailable decks:")
    for i, info in enumerate(deck_info, 1):
        name_padding = ' ' * (max_name_len - len(info['name']))
        due_padding = ' ' * (max_due_digits - len(str(info['due'])))
        total_padding = ' ' * (max_total_digits - len(str(info['total'])))
        print(f"  {i}. {info['name']}{name_padding}    Due: {due_padding}{info['due']}    Total: {total_padding}{info['total']}")
    print(f"  {len(deck_names) + 1}. Exit")
    
    while True:
        try:
            choice = input(f"\nSelect deck (1-{len(deck_names) + 1}): ").strip()
            choice = int(choice)
            if 1 <= choice <= len(deck_names):
                selected_deck = deck_names[choice - 1]
                return selected_deck
            elif choice == len(deck_names) + 1:
                return None
            else:
                print(f"Please enter a number between 1 and {len(deck_names) + 1}.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nExiting...")
            return None


def run():
    """Run review session with deck selection.
    
    Returns:
        True if should continue (show deck selection again), False if should exit
    """
    selected_deck = select_deck()
    
    if selected_deck is None:
        return False  # User selected Exit
    
    cards, filepath = initialize(selected_deck)
    
    if not cards:
        return True  # Error loading cards, but continue to show deck selection
    
    print(f"\nLoaded {len(cards)} cards from {selected_deck} deck")
    
    review_session(cards, filepath)
    
    return True  # Review complete, show deck selection again


def main():
    """Main entry point."""
    ensure_data_directory()
    
    # Sync all decks from text files on startup
    sync_all_decks()
    
    print("\n" + "=" * 50)
    print("Flashcard Program")
    print("=" * 50)
    
    while True:
        try:
            should_continue = run()
            if not should_continue:
                # User selected Exit from deck menu
                print("\nGoodbye!")
                break
            # Otherwise, loop continues and shows deck selection again
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            import traceback
            traceback.print_exc()
            break


if __name__ == "__main__":
    main()
