from typing import Optional


class Flashcard:
    """Represents a single flashcard with spaced repetition metadata."""
    
    def __init__(
        self,
        id: str,
        term: str,
        definition: str,
        next_review: Optional[str] = None,
        ease_factor: float = 2.5,
        interval: int = 1,
        difficulty: int = 0,
        completed_today: bool = False,
        first_rating: Optional[int] = None,
        session_attempts: int = 0,
        consecutive_easy_sessions: int = 0,
        latest_rating: Optional[int] = None
    ):
        self.id = id
        self.term = term
        self.definition = definition
        self.next_review = next_review
        self.ease_factor = ease_factor
        self.interval = interval
        self.difficulty = difficulty
        self.completed_today = completed_today
        self.first_rating = first_rating
        self.session_attempts = session_attempts
        self.consecutive_easy_sessions = consecutive_easy_sessions
        self.latest_rating = latest_rating
    
    def to_dict(self) -> dict:
        """Convert flashcard to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "term": self.term,
            "definition": self.definition,
            "next_review": self.next_review,
            "ease_factor": self.ease_factor,
            "interval": self.interval,
            "difficulty": self.difficulty,
            "completed_today": self.completed_today,
            "first_rating": self.first_rating,
            "session_attempts": self.session_attempts,
            "consecutive_easy_sessions": self.consecutive_easy_sessions,
            "latest_rating": self.latest_rating
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Flashcard':
        """Create flashcard from dictionary."""
        return cls(
            id=data["id"],
            term=data["term"],
            definition=data["definition"],
            next_review=data.get("next_review"),
            ease_factor=data.get("ease_factor", 2.5),
            interval=data.get("interval", 1),
            difficulty=data.get("difficulty", 0),
            completed_today=data.get("completed_today", False),
            first_rating=data.get("first_rating"),
            session_attempts=data.get("session_attempts", 0),
            consecutive_easy_sessions=data.get("consecutive_easy_sessions", 0),
            latest_rating=data.get("latest_rating")
        )
    
    def reset_session(self):
        """Reset session-specific fields."""
        self.first_rating = None
        self.session_attempts = 0
        self.latest_rating = None
    
    def start_session(self):
        """Initialize card for a new session."""
        if self.completed_today:
            self.reset_session()
    
    def __repr__(self) -> str:
        return f"Flashcard(id={self.id}, term={self.term[:30]}...)"

