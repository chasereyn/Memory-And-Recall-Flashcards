# MemoryFlashcards

Personal **Spanish flashcard CLI**. Python 3.11+, stdlib only.

Run: `python main.py` → pick a deck → English prompt → reveal Spanish → rate 1–4.

## The daily loop

Chase keeps a running list of words and phrases in Google Keep during the day, then pastes
it into Claude Code and runs `/vocab`. The skill translates each bullet and appends it to
`data/spanish.txt`. Claude's whole job is that append. Review happens in the CLI, not here.

`/vocab` **with nothing else** in the message is the other mode: pull 10 random unused pairs
from the `backlog/spanish.txt` archive instead. For days with no list, or to keep folding the
old bulk vocab back in a bite at a time.

The point of the repo is **learning to say the things he actually says** — not working
through a generic vocab list. Something he wished he could say today should be memorized
by tomorrow.

## Storage

| What | Where | Editable? |
|------|-------|-----------|
| Card content | `data/*.txt` — term + definition pairs, blank line between cards | ✅ yes |
| Progress state | `data/decks/*.json` — auto-managed, gitignored | ❌ **never edit by hand** |

**Sync on startup:** preserves progress for matching ids, adds new cards from txt,
removes deleted cards.

## Architecture

| File | Role |
|------|------|
| `main.py` | Entry point, deck menu, review session |
| `parser.py` | Parses `data/*.txt` → flashcards |
| `flashcard.py` | Card model |
| `spaced_repetition.py` | Session-based SRS, queue prioritization |
| `storage.py` | JSON load/save, sync txt ↔ json on startup |
| `test_algorithm.py` | SRS logic tests |
| `.claude/skills/vocab/` | The `/vocab` skill — bullets → cards |
| `.claude/skills/vocab/pull.py` | Backlog picker — samples unused pairs, enforces the tail-append rules |

## Decks

**Live — `data/`:**

| Deck | Notes |
|------|-------|
| `spanish.txt` | The only active deck. English prompt → Spanish answer. Grown daily via `/vocab`. |

**Roadmap — `backlog/`.** These are parked, not deleted. Good material, but not phrases
Chase says every day, so they don't earn deck slots yet. Promote one into `data/` when it
becomes a priority, and teach `/vocab` its card direction at the same time.

`english.txt` (English vocab, minimal-swap pairs) · `mexican.txt` (food, culture, geography)
· `verbs.txt` (grammar construction sentences, hand-maintained) · `flirt.txt` · `chistes.txt`
· `jokes.txt` · `slang.txt` · `DOP.txt` · `numbers.txt` · `longphrases.txt` ·
`lawsofpower.txt` · a 284KB `spanish.txt` archive of the old bulk vocab list.

`backlog/spanish.txt` is special — it is the source for a bare `/vocab` pull, not a deck
waiting to be promoted. It stays intact; pulled pairs are copied, never moved, and repeats
are prevented by matching against the live deck.

It once had a stray unpaired line at the top that shifted `parser.py`'s pairing for the whole
file — fixed. `pull.py` reads it by blank-line-separated blocks and keeps only 2-line ones,
so a future orphan would be skipped rather than silently mis-pairing everything after it.

Card format:

```
English prompt
Spanish answer

Next prompt
Next answer
```

## Review algorithm

Session-based (**not** Anki SM-2). Cards must reach rating **4** to complete a session.

Ratings: 1=Hard, 2=Medium-Hard, 3=Medium, 4=Easy

- Progress **1 → 2 → 3 → 4** within a session (can drop back to 1)
- **First rating** drives long-term scheduling when you hit 4
- Re-insertion: 1 → positions 2–5; 2 → 10–25 ahead; 3 → 20–40 ahead; 4 → done
- All due cards appear in session (no daily cap)

## Content philosophy

- **Context over grammar** — phrases and stories, not rule drills
- **Personal over generic** — real people, family, Mexico trips, real stories
- **Mexico City Spanish** — prefer CDMX usage over neutral-textbook or Spain forms
- **`tú` by default** — infer `usted` only from clear context; it's rare
- **Minimal by design** — plain txt decks you can read and edit without being overwhelmed

## Conventions

- **Extend content at the tail** of `data/*.txt`. Do not rewrite existing cards unless asked.
- Windows PowerShell: chain with `;`, not `&&`.
- Commit only when explicitly asked.

## Do not

- Edit `data/decks/*.json` by hand
- **Insert or reorder cards mid-file.** `parser.py` pairs consecutive non-empty lines from
  the top and hashes `term|definition` for the card ID. An odd-line insertion re-pairs every
  card below it, changes every ID, and silently wipes review progress for the whole deck.
  Append at the tail, always in even line counts.
- Bulk-rewrite register (tú/usted) on old cards without being asked
