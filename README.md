# CCC - Flashcard Learning System

A spaced repetition flashcard system with automatic syncing and a unique session-based algorithm designed for effective vocabulary learning.

## Quick Start

1. **Add your vocabulary**: Create text files (`.txt`) in the `data/` directory. Each file represents a deck. Format: term and definition on consecutive lines:
   ```
   Roof
   Tejado
   
   Step aside!
   Golpe avisa!
   ```

2. **Run the program**:
   ```bash
   python main.py
   ```

3. **Select a deck** and start reviewing!

That's it! No setup required—just add your vocabulary and run the program.

## Features

### Automatic Syncing

The system automatically syncs your text files with JSON storage on startup. It:
- **Preserves** cards that exist in both (keeps your progress and review history)
- **Adds** new cards from text files
- **Removes** cards that you've deleted from text files

Your review progress is never lost—only the source content (text files) is synced, while all learning metadata stays intact.

### Session-Based Algorithm

Unlike traditional spaced repetition systems (like Anki's SM-2), this uses a **session-based approach** designed to prevent gaming and improve retention:

**Rating System:**
- **1 = Hard/Repeat**: Reappears randomly in positions 2-5 (stays in session)
- **2 = Medium-Hard**: Reappears 10-25 cards ahead (fixed range, stays in session)
- **3 = Medium**: Reappears 20-40 cards ahead (fixed range, stays in session)
- **4 = Easy**: Completed for session (removed from queue, scheduled for future review)

**Key Features:**

**First Impression Matters** - Your **first rating** determines difficulty adjustment, not your final rating. If you struggle initially (1-3) but eventually rate it 4, the algorithm still recognizes the initial difficulty. This prevents easy cards from being scheduled too far out due to momentary lapses.

**Session Completion Required** - Cards rated 1-3 stay in session until rated 4. This ensures active recall rather than passive recognition and prevents gaming the system (you can't just see the answer and rate it "easy").

**Fixed-Distance Reinsertion** - Unlike proportional systems that can bury struggling cards thousands of positions back in large decks, fixed distances work identically for 20 cards or 3000+ cards. Hard cards reappear randomly in positions 2-5 (not immediately) to force cognitive refocusing—the unpredictable brief gap prevents short-term/muscle memory from masquerading as true learning.

**Smart Prioritization** - Active session cards (struggling) appear first, prioritized by attempts and difficulty. Well-mastered cards fade into the background with exponential backoff (consecutive easy sessions multiply intervals exponentially).

**Adaptive Difficulty Tracking** - Struggle history is tracked separately from intervals, ensuring difficult material gets frequent reviews even when intervals suggest otherwise.

## File Structure

```
data/
  ├── spanish_vocab.txt        # Your text decks
  ├── english_jokes.txt
  └── decks/
      ├── spanish_vocab.json    # Auto-generated (don't edit)
      └── english_jokes.json
```

Edit the text files to add or remove vocabulary. The JSON files are automatically managed by the sync system.

## Requirements

- Python 3.11+

No dependencies required—uses only Python standard library.

