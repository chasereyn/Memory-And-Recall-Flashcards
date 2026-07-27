import os
from storage import (
    load_cards,
    save_cards,
    delete_card,
    ensure_data_directory,
    get_last_session_date,
    sync_all_decks,
    get_deck_files,
    deck_progress_path,
    get_deck_name_from_file,
)
from spaced_repetition import (
    update_card_after_review,
    get_cards_for_review,
    get_deck_session_info,
    reset_daily_flags,
    get_today,
    DEFAULT_DAILY_LIMIT,
    get_daily_slots_used,
)
import random

# Set True to show overdue backlog in the deck menu (e.g. "Backlog: 523")
SHOW_BACKLOG_IN_MENU = False

# Decks shown in the menu (others still sync on startup). Empty list = show all.
VISIBLE_DECKS = ["spanish"]

# Per-deck daily new-card cap; unset decks use DEFAULT_DAILY_LIMIT.
DECK_DAILY_LIMITS = {"spanish": 50}


def get_daily_limit(deck_name: str) -> int:
    return DECK_DAILY_LIMITS.get(deck_name, DEFAULT_DAILY_LIMIT)


def ensure_daily_reset(cards, filepath):
    """On a new calendar day, reset session flags and persist so menu and review agree."""
    today = get_today()
    last_session_date = get_last_session_date(filepath)
    if last_session_date != today:
        reset_daily_flags(cards, last_session_date, today)
        save_cards(cards, filepath, update_session_date=True)
    return today


def initialize(deck_name: str):
    """Load cards for a specific deck from JSON file."""
    json_path = deck_progress_path(deck_name)
    cards = load_cards(json_path)
    
    if not cards:
        print(f"Error: No cards found for deck '{deck_name}'")
        return [], None
    
    return cards, json_path


def get_user_rating(card):
    """Get user rating with validation, constrained by sequential progression.

    Returns:
        int (1-4), 'delete', or None if user quits
    """
    # Determine allowed ratings based on latest_rating
    if card.latest_rating is None:
        # New card - can rate 1-4
        allowed_ratings = [1, 2, 3, 4]
        prompt_options = "1=Hard/Repeat, 2=Medium-Hard, 3=Medium, 4=Easy"
    elif card.latest_rating == 1:
        # Can only advance to 2
        allowed_ratings = [1, 2]
        prompt_options = "1=Hard/Repeat, 2=Medium-Hard"
    elif card.latest_rating == 2:
        # Can advance to 3
        allowed_ratings = [1, 2, 3]
        prompt_options = "1=Hard/Repeat, 2=Medium-Hard, 3=Medium"
    elif card.latest_rating == 3:
        # Can advance to 4
        allowed_ratings = [1, 2, 3, 4]
        prompt_options = "1=Hard/Repeat, 2=Medium-Hard, 3=Medium, 4=Easy"
    else:
        # Fallback (shouldn't happen)
        allowed_ratings = [1, 2, 3, 4]
        prompt_options = "1=Hard/Repeat, 2=Medium-Hard, 3=Medium, 4=Easy"

    extra_options = "d=Delete, or 'quit'"
    
    while True:
        try:
            rating = input(f"Rate difficulty ({prompt_options}, {extra_options}): ").strip().lower()
            if rating == 'quit':
                return None
            if rating == 'd':
                return 'delete'
            rating = int(rating)
            if rating in allowed_ratings:
                return rating
            else:
                allowed_str = ", ".join(str(r) for r in allowed_ratings)
                print(f"Please enter a number from [{allowed_str}], d, or 'quit'.")
        except ValueError:
            allowed_str = ", ".join(str(r) for r in allowed_ratings)
            print(f"Please enter a valid number from [{allowed_str}], d, or 'quit'.")
        except KeyboardInterrupt:
            print("\nExiting...")
            return None


def review_session(cards, filepath):
    """Run a review session with the given cards.

    Returns:
        'quit' if the user exited early, 'done' if the queue was finished.
    """
    today = ensure_daily_reset(cards, filepath)
    deck_name = get_deck_name_from_file(filepath)
    daily_limit = get_daily_limit(deck_name)

    # Get cards ready for review
    review_cards = get_cards_for_review(cards, today, daily_limit=daily_limit)
    
    if not review_cards:
        print("\n" + "=" * 60)
        print("No cards ready for today!")
        print("=" * 60)
        return 'done'
    
    slots_used = get_daily_slots_used(cards)
    print("\n" + "=" * 60)
    print(f"Starting review session - {len(review_cards)} card(s) in queue")
    print(f"Daily progress: {slots_used} / {daily_limit} cards touched today")
    print("=" * 60)
    print("\nInstructions:")
    print("  - Press Enter to see the definition")
    print("  - Rate the card: 1=Hard/Repeat, 2=Medium-Hard, 3=Medium, 4=Easy")
    print("  - You can only advance ratings one step at a time (e.g., 1→2→3→4)")
    print("  - Cards rated 1-3 will be shown again until you rate them 4")
    print("  - Press 'd' to delete the current card from the deck")
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
        
        print("-" * 60)
        print(f"{cards_remaining} card(s) remaining")
        print(f"Term: {current_card.term}")
        print("-" * 60)
        
        # Wait for user to press Enter to see definition
        input("Press Enter to reveal definition...")
        
        print(f"\nDefinition: {current_card.definition}")
        print()
        
        # Get rating
        rating = get_user_rating(current_card)
        if rating is None:
            return 'quit'
        if rating == 'delete':
            deck_name = get_deck_name_from_file(filepath)
            cards[:] = delete_card(cards, deck_name, current_card.id)
            save_cards(cards, filepath)
            review_cards = [c for c in review_cards if c.id != current_card.id]
            initial_card_count = len(review_cards)
            print("\nCard deleted.")
            print()
            continue
        
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
            # Rating 1: Insert randomly in positions 2-5 (for cognitive refocusing)
            # Remove from current position first
            review_cards = [c for c in review_cards if c.id != current_card.id]
            # Insert at random position in positions 2-5 (1-4 in 0-indexed), clamped to available positions
            if len(review_cards) > 0:
                min_pos = 1  # Position 2 (1-indexed)
                max_pos = min(4, len(review_cards) - 1)  # Position 5 (1-indexed) or end of queue
                if min_pos <= max_pos:
                    insert_pos = random.randint(min_pos, max_pos)
                    review_cards.insert(insert_pos, current_card)
                else:
                    # If queue is too short, append to end
                    review_cards.append(current_card)
            else:
                # If queue is empty, just add it
                review_cards.append(current_card)
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
    print("\n" + "=" * 60)
    if cards_completed == initial_card_count:
        print("Excellent! All cards completed for this session!")
    elif cards_completed > 0:
        print(f"Session complete! {cards_completed} card(s) mastered!")
    else:
        print("Session paused. Progress saved!")
    print("=" * 60)
    print(f"  Cards completed: {cards_completed} / {initial_card_count}")
    print(f"  Total reviews: {total_reviews}")
    if cards_completed < initial_card_count:
        remaining = initial_card_count - cards_completed
        print(f"  Cards remaining: {remaining}")
    print("=" * 60)
    return 'done'


def get_available_decks():
    """Get list of available deck names from text files."""
    deck_files = get_deck_files()
    deck_names = sorted(get_deck_name_from_file(f) for f in deck_files)
    if VISIBLE_DECKS:
        visible = set(VISIBLE_DECKS)
        deck_names = [name for name in deck_names if name in visible]
    return deck_names


def select_deck():
    """Show deck selection menu and return selected deck name, or None if user wants to exit."""
    # Get available decks from text files
    deck_names = get_available_decks()
    
    if not deck_names:
        print("No decks found. Add .tsv files to the data/decks/ directory.")
        return None
    
    # Get today's date for calculating due cards
    today = get_today()
    
    # Calculate deck info for menu display
    deck_info = []
    for deck_name in deck_names:
        json_path = deck_progress_path(deck_name)
        cards = load_cards(json_path)
        total_count = len(cards)
        
        ensure_daily_reset(cards, json_path)
        
        today_count, backlog_count = get_deck_session_info(
            cards, today, daily_limit=get_daily_limit(deck_name)
        )
        
        deck_info.append({
            'name': deck_name,
            'today': today_count,
            'backlog': backlog_count,
            'total': total_count
        })
    
    # Find max widths for formatting
    max_name_len = max(len(info['name']) for info in deck_info) if deck_info else 0
    max_today_digits = max(len(str(info['today'])) for info in deck_info) if deck_info else 0
    max_total_digits = max(len(str(info['total'])) for info in deck_info) if deck_info else 0
    
    # Show deck selection with formatted columns (right-aligned numbers)
    print("\nAvailable decks:")
    for i, info in enumerate(deck_info, 1):
        name_padding = ' ' * (max_name_len - len(info['name']))
        today_str = str(info['today']).rjust(max_today_digits)
        total_str = str(info['total']).rjust(max_total_digits)
        line = f"  {i:2d}. {info['name']}{name_padding}    Today: {today_str}    Total: {total_str}"
        if SHOW_BACKLOG_IN_MENU:
            line += f"    Backlog: {info['backlog']}"
        print(line)
    print("\nType 'exit' to exit")
    
    while True:
        try:
            choice = input(f"\nSelect deck (1-{len(deck_names)}, or 'exit'): ").strip().lower()
            if choice == 'exit':
                return None
            choice = int(choice)
            if 1 <= choice <= len(deck_names):
                selected_deck = deck_names[choice - 1]
                return selected_deck
            else:
                print(f"Please enter a number between 1 and {len(deck_names)}, or 'exit'.")
        except ValueError:
            print(f"Please enter a valid number between 1 and {len(deck_names)}, or 'exit'.")
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
    
    while True:
        cards, filepath = initialize(selected_deck)
        if not cards:
            break

        ensure_daily_reset(cards, filepath)
        daily_limit = get_daily_limit(selected_deck)
        today = get_today()
        review_cards = get_cards_for_review(cards, today, daily_limit=daily_limit)
        if not review_cards:
            break

        result = review_session(cards, filepath)
        if result == 'quit':
            break

        # Resume if cards remain (e.g. quit mid-session earlier)
        cards, filepath = initialize(selected_deck)
        ensure_daily_reset(cards, filepath)
        if not get_cards_for_review(cards, today, daily_limit=daily_limit):
            break
        print("\nMore cards left for today — continuing...\n")
    
    return True  # Review complete, show deck selection again


def main():
    """Main entry point."""
    ensure_data_directory()
    
    # Sync all decks from text files on startup
    sync_all_decks()
    
    print("\n" + "=" * 60)
    print("MemoryFlashcards")
    print("=" * 60)
    
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
