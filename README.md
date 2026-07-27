# MemoryFlashcards

A personal spaced-repetition flashcard CLI with automatic syncing and a session-based review algorithm, built for effective vocabulary and phrase learning.

## Quick Start

1. **Add your vocabulary**: Create TSV files in `data/decks/`. One card per line — tab-separated prompt and answer:
   ```
   term	definition
   Roof	Tejado
   Step aside!	Golpe avisa!
   ```

2. **Run the program**:
   ```bash
   python main.py
   ```

3. **Select a deck** and start reviewing!

That's it! No setup required—just add your vocabulary and run the program.

## Features

### Automatic Syncing

The system automatically syncs deck content (`.tsv`) with progress storage on startup. It:
- **Preserves** cards that exist in both (keeps your progress and review history)
- **Adds** new cards from deck TSV files
- **Removes** cards that you've deleted from deck TSV files

Your review progress is never lost—only the source content (deck TSV) is synced, while all learning metadata stays intact.

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

**Sequential Rating Progression** - Ratings must progress sequentially (1→2→3→4), preventing you from skipping from "Hard" directly to "Easy". This encourages gradual mastery and prevents premature completion. If you rate a card 3, then forget it and rate it 1, you'll need to progress through 1→2→3→4 again. New cards (never seen in the session) can still be rated 1-4 freely.

**Fixed-Distance Reinsertion** - Unlike proportional systems that can bury struggling cards thousands of positions back in large decks, fixed distances work identically for 20 cards or 3000+ cards. Hard cards reappear randomly in positions 2-5 (not immediately) to force cognitive refocusing—the unpredictable brief gap prevents short-term/muscle memory from masquerading as true learning.

**Smart Prioritization** - Active session cards (struggling) appear first. Due cards are shuffled each session so bulk-added content does not play out in one block. Well-mastered cards fade into the background with exponential backoff (consecutive easy sessions multiply intervals exponentially).

**Adaptive Difficulty Tracking** - Struggle history is tracked separately from intervals, ensuring difficult material gets frequent reviews even when intervals suggest otherwise.

**Daily Session Limit** - Each deck introduces at most **10 due cards per day** (configurable via `DEFAULT_DAILY_LIMIT` in `spaced_repetition.py`). Active in-session cards are always included; reinsertions from ratings 1–3 do not pull extra cards from the backlog. Remaining due cards stay queued for future days — show up daily rather than marathon sessions. Set `SHOW_BACKLOG_IN_MENU = True` in `main.py` to display the full overdue count in the deck menu.

## Decks

All decks live in `data/decks/` as `*.tsv` files. Main decks:

| Deck | Purpose |
|------|---------|
| `spanish.tsv` | Main vocabulary — English prompt → Spanish answer |
| `verbs.tsv` | Grammar constructions — full example sentences |
| `english.tsv` | English vocabulary — minimal-swap paired sentences |
| `mexican.tsv` | Mexican food, culture, geography — English descriptions |
| `numbers.tsv` | Digits 1–100 → Spanish number words |
| `DOP.tsv` | Direct/indirect object pronoun drills |
| `flirt.tsv`, `jokes.tsv`, `chistes.tsv` | Couple talk, English jokes, Spanish wordplay |
| `lawsofpower.tsv`, `longphrases.tsv` | Side decks |

Progress mirrors deck names in `data/progress/` (auto-managed, gitignored).

## Verbs deck

`data/decks/verbs.tsv` is **hand-maintained**. Cards are grouped by **construction** (preterite sampler, imperfect, subjunctive triggers, accidental se, etc.) — not by conjugation grids.

When adding a new construction block:

- Pick verbs from `full_verb_list.txt` that sound **natural** with that pattern.
- **Append** new rows at the end — blank lines between blocks are fine.
- One English prompt, one Spanish answer per line.
- Vary subjects and mix in clitics where the pattern allows.
- Match the short narrative style already in the file.

## English deck

`data/decks/english.tsv` uses **two TSV rows per vocabulary item**: gloss → headword, then a plain example sentence → the same sentence with only the headword swapped in. See `.cursor/skills/english/SKILL.md` for the full pattern.

## File Structure

```
data/
  ├── decks/           # Deck content — edit these (one card per line)
  │   ├── spanish.tsv
  │   ├── verbs.tsv
  │   └── ...
  └── progress/        # Review state (auto-managed, gitignored)
      ├── spanish.tsv
      ├── verbs.tsv
      └── ...
```

Edit files in `data/decks/` to add or remove cards. Progress in `data/progress/` is managed automatically on startup.

## Requirements

- Python 3.11+

No dependencies required—uses only Python standard library.

## Daily 8:30 AM task

Same pattern as **Sarita Romance Daily** and **DailyConnections** — opens a terminal window; press Enter to close when done.

Register once (PowerShell, from repo root):

```powershell
.\scripts\install_scheduler.ps1
```

Creates **MemoryFlashcards Daily Review** — runs `scripts/run_daily.ps1` every morning at **8:30 AM**.

If the PC is asleep or off at 8:30, the task runs **as soon as you log in** after wake (StartWhenAvailable). It will not wake the computer from sleep on its own.

To test immediately:

```powershell
Start-ScheduledTask -TaskName "MemoryFlashcards Daily Review"
```

To remove later:

```powershell
Unregister-ScheduledTask -TaskName "MemoryFlashcards Daily Review" -Confirm:$false
```
