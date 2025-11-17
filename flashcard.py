from datetime import datetime
from typing import Optional


class Flashcard:
    """Represents a single flashcard with spaced repetition metadata."""
    
    def __init__(
        self,
        id: str,
        term: str,
        definition: str,
        last_reviewed: Optional[str] = None,
        next_review: Optional[str] = None,
        ease_factor: float = 2.5,
        interval: int = 1,
        repetitions: int = 0,
        difficulty: float = 0.3,
        review_count: int = 0,
        struggle_count: int = 0,
        completed_today: bool = False,
        first_rating_this_session: Optional[int] = None,
        session_attempts: int = 0,
        consecutive_easy_sessions: int = 0
    ):
        self.id = id
        self.term = term
        self.definition = definition
        self.last_reviewed = last_reviewed
        self.next_review = next_review
        self.ease_factor = ease_factor
        self.interval = interval
        self.repetitions = repetitions
        self.difficulty = difficulty
        self.review_count = review_count
        self.struggle_count = struggle_count
        self.completed_today = completed_today
        self.first_rating_this_session = first_rating_this_session
        self.session_attempts = session_attempts
        self.consecutive_easy_sessions = consecutive_easy_sessions
    
    def to_dict(self) -> dict:
        """Convert flashcard to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "term": self.term,
            "definition": self.definition,
            "last_reviewed": self.last_reviewed,
            "next_review": self.next_review,
            "ease_factor": self.ease_factor,
            "interval": self.interval,
            "repetitions": self.repetitions,
            "difficulty": self.difficulty,
            "review_count": self.review_count,
            "struggle_count": self.struggle_count,
            "completed_today": self.completed_today,
            "first_rating_this_session": self.first_rating_this_session,
            "session_attempts": self.session_attempts,
            "consecutive_easy_sessions": self.consecutive_easy_sessions
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Flashcard':
        """Create flashcard from dictionary."""
        return cls(
            id=data["id"],
            term=data["term"],
            definition=data["definition"],
            last_reviewed=data.get("last_reviewed"),
            next_review=data.get("next_review"),
            ease_factor=data.get("ease_factor", 2.5),
            interval=data.get("interval", 1),
            repetitions=data.get("repetitions", 0),
            difficulty=data.get("difficulty", 0.3),
            review_count=data.get("review_count", 0),
            struggle_count=data.get("struggle_count", 0),
            completed_today=data.get("completed_today", False),
            first_rating_this_session=data.get("first_rating_this_session"),
            session_attempts=data.get("session_attempts", 0),
            consecutive_easy_sessions=data.get("consecutive_easy_sessions", 0)
        )
    
    def reset_session(self):
        """Reset session-specific fields."""
        self.first_rating_this_session = None
        self.session_attempts = 0
    
    def start_session(self):
        """Initialize card for a new session."""
        if self.completed_today:
            self.reset_session()
    
    def __repr__(self) -> str:
        return f"Flashcard(id={self.id}, term={self.term[:30]}...)"

