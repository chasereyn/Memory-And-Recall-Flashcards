from datetime import datetime, timedelta
from typing import List, Optional
from flashcard import Flashcard


# Algorithm constants
MIN_EASE_FACTOR = 1.3
MAX_EASE_FACTOR = 2.5
MIN_INTERVAL = 1
MAX_INTERVAL = 365  # Cap at 1 year
EASE_FACTOR_INCREASE = 0.10
EASE_FACTOR_DECREASE_EASY = 0.05
EASE_FACTOR_DECREASE_MEDIUM = 0.15
EASE_FACTOR_DECREASE_HARD = 0.25
BACKOFF_BASE = 1.5  # Exponential backoff multiplier


def get_today() -> str:
    """Get today's date as ISO format string."""
    return datetime.now().strftime("%Y-%m-%d")


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO date string to datetime object."""
    if date_str is None:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def format_date(date: datetime) -> str:
    """Format datetime object to ISO date string."""
    return date.strftime("%Y-%m-%d")


def add_days(date_str: Optional[str], days: int) -> str:
    """Add days to a date string and return new date string."""
    if date_str is None:
        base_date = datetime.now()
    else:
        base_date = parse_date(date_str)
        if base_date is None:
            base_date = datetime.now()
    
    new_date = base_date + timedelta(days=days)
    return format_date(new_date)


def update_card_after_review(card: Flashcard, rating: int) -> None:
    """
    Update card metadata based on user rating.
    
    Rating 1-3: Track first rating, increment attempts, keep in session
    Rating 4: Update metadata based on first rating, apply exponential backoff if applicable
    """
    if rating not in [1, 2, 3, 4]:
        raise ValueError(f"Invalid rating: {rating}. Must be 1, 2, 3, or 4.")
    
    today = get_today()
    
    if rating in [1, 2, 3]:
        # Card stays in session - track first rating and increment attempts
        if card.first_rating is None:
            card.first_rating = rating
        
        card.session_attempts += 1
        card.completed_today = False
        # Don't update metadata yet - wait for rating 4
    
    elif rating == 4:
        # Card is done for session - update metadata based on first rating
        first_rating = card.first_rating if card.first_rating is not None else 4
        
        # Update metadata based on first rating
        if first_rating == 1:
            # Very difficult - user struggled significantly
            card.ease_factor = max(MIN_EASE_FACTOR, card.ease_factor - EASE_FACTOR_DECREASE_HARD)
            card.interval = max(MIN_INTERVAL, card.interval // 2)
            card.difficulty += 2
            card.consecutive_easy_sessions = 0
        
        elif first_rating == 2:
            # Difficult - user had some trouble
            card.ease_factor = max(MIN_EASE_FACTOR, card.ease_factor - EASE_FACTOR_DECREASE_MEDIUM)
            card.interval = max(MIN_INTERVAL, int(card.interval * 0.7))
            card.difficulty += 1
            card.consecutive_easy_sessions = 0
        
        elif first_rating == 3:
            # Medium - user had slight difficulty
            card.ease_factor = max(MIN_EASE_FACTOR, card.ease_factor - EASE_FACTOR_DECREASE_EASY)
            # Keep interval similar or slight decrease
            card.interval = max(MIN_INTERVAL, int(card.interval * 0.9))
            card.consecutive_easy_sessions = 0
        
        elif first_rating == 4:
            # Easy - user knew it immediately
            card.ease_factor = min(MAX_EASE_FACTOR, card.ease_factor + EASE_FACTOR_INCREASE)
            card.difficulty = max(0, card.difficulty - 1)
            
            # Apply exponential backoff for consecutive easy sessions
            card.consecutive_easy_sessions += 1
            backoff_multiplier = BACKOFF_BASE ** min(card.consecutive_easy_sessions, 10)  # Cap at 10
            new_interval = int(card.interval * card.ease_factor * backoff_multiplier)
            card.interval = min(MAX_INTERVAL, new_interval)
        
        # Update review tracking
        card.next_review = add_days(today, card.interval)
        card.completed_today = True
        
        # Reset session fields
        card.reset_session()


def get_active_cards(cards: List[Flashcard]) -> List[Flashcard]:
    """
    Get cards that are currently in an active session.
    These are cards that have been rated 1-3 but not yet completed (rated 4).
    """
    return [
        card for card in cards
        if not card.completed_today and card.first_rating is not None
    ]


def get_due_cards(cards: List[Flashcard], today: Optional[str] = None) -> List[Flashcard]:
    """
    Get cards that are due for review (ready for a new session).
    Includes cards with next_review <= today or next_review is None (new cards).
    Also includes cards that were completed_today from a previous day (reset at start of new day).
    """
    if today is None:
        today = get_today()
    
    due_cards = []
    for card in cards:
        # New cards (never reviewed)
        if card.next_review is None:
            due_cards.append(card)
        # Cards due for review
        elif card.next_review <= today:
            due_cards.append(card)
        # Cards completed in previous session (will be reset at start of new day)
        elif card.completed_today and card.next_review > today:
            # This shouldn't happen often, but handle it
            pass
    
    return due_cards


def prioritize_cards(active_cards: List[Flashcard], due_cards: List[Flashcard]) -> List[Flashcard]:
    """
    Prioritize cards for review.
    Active cards (in session) come first, then due cards (new session).
    
    Active cards sorted by:
    1. session_attempts (descending) - cards attempted more times first
    2. difficulty (descending) - struggling cards first
    
    Due cards sorted by:
    1. difficulty (descending) - struggling cards first
    2. next_review (ascending, None first) - oldest due dates first
    """
    # Sort active cards
    active_sorted = sorted(
        active_cards,
        key=lambda c: (c.session_attempts, c.difficulty),
        reverse=True
    )
    
    # Sort due cards
    def due_sort_key(card: Flashcard):
        next_rev = card.next_review if card.next_review else "0000-01-01"  # None comes first
        return (-card.difficulty, next_rev)
    
    due_sorted = sorted(due_cards, key=due_sort_key)
    
    # Active cards first, then due cards
    return active_sorted + due_sorted


def reset_daily_flags(cards: List[Flashcard], last_session_date: Optional[str], today: Optional[str] = None) -> None:
    """
    Reset daily flags if it's a new day.
    If last_session_date != today, reset completed_today flags and session fields for all cards.
    """
    if today is None:
        today = get_today()
    
    if last_session_date != today:
        for card in cards:
            # Reset completed_today for all cards that were completed
            if card.completed_today:
                card.completed_today = False
            # Reset session fields for ALL cards (new day = fresh start)
            card.reset_session()


def get_cards_for_review(cards: List[Flashcard], today: Optional[str] = None) -> List[Flashcard]:
    """
    Get all cards ready for review, properly prioritized.
    Combines active cards (in session) and due cards (new session).
    Active cards are excluded from due cards to prevent duplicates.
    """
    if today is None:
        today = get_today()
    
    active = get_active_cards(cards)
    active_ids = {card.id for card in active}
    
    # Exclude active cards from due cards to prevent duplicates
    due = [card for card in get_due_cards(cards, today) if card.id not in active_ids]
    
    return prioritize_cards(active, due)


def is_card_in_session(card: Flashcard) -> bool:
    """Check if card is currently in an active session."""
    return not card.completed_today and card.first_rating is not None

