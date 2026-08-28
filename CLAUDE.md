# MemoryFlashcards

Personal **Spanish flashcard CLI**. Python 3.11+, stdlib only.

Run: `python main.py` → pick a deck → English prompt → reveal Spanish → rate 1–4.

## The daily loop

Chase keeps a running list of words and phrases in Google Keep during the day, then pastes
it into Claude Code and runs `/spanish`. The skill translates each bullet and appends it to
`data/spanish.txt`. Claude's whole job is that append. Review happens in the CLI, not here.

`/spanish` **with nothing else** in the message is the other mode: pull 10 random unused pairs
from the `backlog/spanish.txt` archive instead. For days with no list, or to keep folding the
old bulk vocab back in a bite at a time.

`/english` is the same idea for the English deck, and only ever runs bare: it takes the next
10 words off `backlog/english.txt`, writes a definition for each, and appends them.

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
| `.claude/skills/spanish/` | The `/spanish` skill — bullets → cards |
| `.claude/skills/spanish/pull.py` | Backlog picker — samples unused pairs, enforces the tail-append rules |
| `.claude/skills/english/` | The `/english` skill — next 10 words → definition cards |
| `.claude/skills/english/pick.py` | Word picker — next unused words, enforces the tail-append rules |

## Decks

**Live — `data/`:**

| Deck | Direction | Grown by |
|------|-----------|----------|
| `spanish.txt` | English prompt → Spanish answer | `/spanish` — daily bullets, or a bare pull from the archive |
| `english.txt` | **Definition prompt → word answer** | `/english` — next 10 words off the list |

The two decks run in opposite directions on purpose. Spanish trains *producing the phrase*
from an English cue. English trains *recalling the word* from its meaning, so the definition
is on top and the word is the answer.

**Roadmap — `backlog/`.** These are parked, not deleted. Good material, but not phrases
Chase says every day, so they don't earn deck slots yet. Promote one into `data/` when it
becomes a priority, and teach `/spanish` its card direction at the same time.

`mexican.txt` (food, culture, geography) · `verbs.txt` (grammar construction sentences,
hand-maintained) · `flirt.txt` · `chistes.txt` · `jokes.txt` · `slang.txt` · `DOP.txt` ·
`numbers.txt` · `longphrases.txt` · `lawsofpower.txt`.

**Two backlog files are sources, not parked decks.** They feed the skills and stay put:

- `backlog/spanish.txt` — ~8300 pairs, the old bulk vocab list. Source for a bare `/spanish`.
  **Copied from, never emptied.** It stays a full archive; repeats are prevented by matching
  candidates against the live deck.
- `backlog/english.txt` — a plain one-word-per-line list. Source for `/english`, which writes
  the definitions. **A queue, not an archive** — a word is deleted from it once it becomes a
  card, so the file drains as the deck fills. It used to hold minimal-swap pairs; that format
  is gone, ignore it.

Neither is waiting to be promoted into `data/`, and neither needs a cursor or state file —
one tracks position by deleting, the other by comparing against the deck.

`backlog/spanish.txt` once had a stray unpaired line at the top that shifted `parser.py`'s
pairing for the whole file — fixed. Both pickers read their source by blank-line-separated
blocks rather than by consecutive-line pairing, so a future orphan gets skipped instead of
silently mis-pairing everything after it.

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
