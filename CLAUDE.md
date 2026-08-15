# MemoryFlashcards

Personal **Spanish flashcard CLI**. Python 3.11+, stdlib only.

Run: `python main.py` → pick a deck → English prompt → reveal Spanish → rate 1–4.

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

## Decks (`data/*.txt`)

| Deck | Notes |
|------|-------|
| `spanish.txt` | Main vocab (~8000 cards) — English prompt → Spanish answer |
| `verbs.txt` | Grammar construction example sentences (hand-maintained) |
| `english.txt` | English vocab — minimal-swap paired sentences |
| `mexican.txt` | Mexican food, culture, geography — English descriptions |
| `DOP.txt` `numbers.txt` `jokes.txt` `flirt.txt` `chistes.txt` `slang.txt` `longphrases.txt` `lawsofpower.txt` | Side decks |

Default card format:

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
- **Mexican Spanish** — natural MX choices, neutral register
- **Keep the long vocab list** — `spanish.txt` is the main deck

## Conventions

- **Extend content at the tail** of `data/*.txt`. Do not rewrite existing cards unless asked.
- Deck-specific skills exist for authoring: `spanish`, `english`, `mexican`.
- Windows PowerShell: chain with `;`, not `&&`.
- Commit only when explicitly asked.

## Do not

- Edit `data/decks/*.json` by hand
- Bulk-rewrite register (tú/usted) on old cards without being asked
