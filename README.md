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

### Unique Session-Based Algorithm

Unlike traditional spaced repetition algorithms (like Anki's SM-2), this system uses a **session-based approach** with several key differences:

**1. First Impression Matters**
- Your **first rating** in each session determines the difficulty adjustment, not your final rating
- If you struggle initially (rate 1-3) but eventually master it (rate 4), the algorithm still recognizes the initial difficulty
- This prevents easy cards from being scheduled too far out if you just had a momentary lapse

**2. Session Completion Required**
- Cards rated 1-3 stay in the current session until you rate them 4 (Easy)
- You can't move on until you've truly mastered the card in that session
- This ensures active recall rather than passive recognition

**3. Exponential Backoff for Mastery**
- Cards you consistently rate as Easy (4) get exponentially longer intervals
- Each consecutive easy session multiplies the interval, allowing well-known cards to fade into the background
- This prevents over-reviewing material you've already mastered

**4. Smart Prioritization**
- Cards you're actively struggling with (in-session) appear first
- Within sessions, cards you've attempted more times get priority
- This focuses your attention on what needs the most work

**5. Fixed-Distance Reinsertion**
- Cards rated 1 (Hard) reappear immediately at the front of the queue
- Cards rated 2 (Medium-Hard) reappear 10-20 cards ahead (fixed distance, clamped)
- Cards rated 3 (Medium) reappear 20-30 cards ahead (fixed distance, clamped)
- Unlike proportional systems, this ensures you see struggling cards again within a predictable window
- Works seamlessly for both small decks (20 cards) and large decks (3000+ cards)
- Prevents cards from being buried thousands of positions back in large decks

**6. Adaptive Difficulty Tracking**
- The system tracks your struggle history separately from interval calculations
- Cards you've struggled with get more frequent reviews, even if intervals suggest otherwise
- This ensures difficult material doesn't get forgotten

## Rating System

- **1 = Hard/Repeat**: Card shown again immediately at the front of the queue (stays in session)
- **2 = Medium-Hard**: Card reappears 10-20 cards ahead (fixed distance, stays in session)
- **3 = Medium**: Card reappears 20-30 cards ahead (fixed distance, stays in session)
- **4 = Easy**: Card completed for session (removed from queue, scheduled for future review)

Cards must be rated 4 to complete a session. Your first rating determines how the algorithm adjusts the card's difficulty and scheduling. The fixed-distance reinsertion ensures you'll see cards rated 2-3 again within 10-30 cards, preventing them from being buried thousands of positions back in large decks.

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

