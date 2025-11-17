# CCC - Spanish Learning Flashcard Program

A spaced repetition flashcard system designed to help you learn Spanish vocabulary and practice active recall of phrases.

## Features

- **Memory Mode**: Learn English ↔ Spanish word pairs with spaced repetition
- **Recall Mode**: Practice numbered phrases to expand active vocabulary
- **Smart Algorithm**: Session-based spaced repetition that adapts to your performance
- **Persistent Storage**: All progress saved automatically across sessions

## Quick Start

1. Add your vocabulary to `memory.txt` (term/definition pairs, one per line)
2. Add phrases to `recall.txt` (organized by deck: `[Spanish]` or `[English]`)
3. Run the program:
   ```bash
   python main.py
   ```
4. Select a mode and start reviewing!

## Rating System

- **1 = Hard/Repeat**: Card shown again immediately (stays in session)
- **2 = Medium-Hard**: Card shown again soon (stays in session)
- **3 = Medium**: Card shown again soon (stays in session)
- **4 = Easy**: Card completed for session (removed from queue)

Cards rated 1-3 will cycle until you rate them 4. The algorithm uses your **first rating** in each session to determine difficulty adjustments.

## File Structure

- `main.py` - Main entry point and UI
- `flashcard.py` - Flashcard data model
- `parser.py` - Parses memory.txt and recall.txt files
- `storage.py` - JSON persistence layer
- `spaced_repetition.py` - Spaced repetition algorithm
- `memory.txt` - English/Spanish vocabulary pairs
- `recall.txt` - Numbered phrase decks
- `data/` - JSON files storing flashcard metadata

## How It Works

The algorithm tracks your performance and adjusts review intervals:
- **Struggling cards** (rated 1-2) appear more frequently
- **Easy cards** (rated 4 immediately) use exponential backoff (appear less often over time)
- **Session-based**: Cards must be rated 4 to complete a session
- **First impression matters**: Your first rating in a session determines the difficulty adjustment

## Requirements

- Python 3.11+

## License

Personal project for language learning.

