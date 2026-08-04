---
name: init
description: Onboards agents to MemoryFlashcards — personal Spanish flashcard CLI, txt/json storage, decks, review algorithm, and content philosophy. Use when the user runs /init or asks to get up to speed on this project.
disable-model-invocation: true
---

# MemoryFlashcards — Project Init

When invoked, treat this skill as your baseline context for this repo. Confirm you are oriented, then wait for the user's task.

## What this repo is

**MemoryFlashcards** is a **personal Spanish flashcard CLI**.

- **Content:** text files in `data/*.txt` (term + definition pairs, blank line between cards)
- **Storage:** JSON in `data/decks/*.json` (auto-managed, gitignored — do not edit)
- **Stack:** Python 3.11+, stdlib only

Run: `python main.py` → pick a deck → English prompt → reveal Spanish → rate 1–4.

## Philosophy

- **Context over grammar** — phrases and stories, not rule drills
- **Personal over generic** — Sarah, family, Mexico trips, real stories
- **Mexican Spanish** — natural MX choices, neutral register
- **Keep the long vocab list** — `spanish.txt` is the main deck (~8000 cards)

## Architecture

| File | Role |
|------|------|
| `main.py` | Entry point, deck menu, review session |
| `parser.py` | Parses `data/*.txt` → flashcards |
| `flashcard.py` | Card model |
| `spaced_repetition.py` | Session-based SRS, queue prioritization |
| `storage.py` | JSON load/save, sync txt ↔ json on startup |
| `test_algorithm.py` | SRS logic tests |

**Sync** on startup: preserve progress for matching ids, add new cards from txt, remove deleted cards.

## Decks (`data/*.txt`)

| Deck | Notes |
|------|-------|
| `spanish.txt` | Main vocab — English prompt → Spanish answer |
| `verbs.txt` | Grammar construction example sentences (hand-maintained) |
| `english.txt` | English vocab — minimal-swap paired sentences (see `english` skill) |
| `mexican.txt` | Mexican food, culture, geography — English descriptions |
| `DOP.txt`, `numbers.txt`, `jokes.txt`, `flirt.txt`, `chistes.txt`, `slang.txt`, `longphrases.txt`, `lawsofpower.txt` | Side decks |

## Card format (default)

```
English prompt
Spanish answer

Next prompt
Next answer
```

## Review algorithm

Session-based (not Anki SM-2). Cards must reach rating **4** to complete a session.

**Ratings:** 1=Hard, 2=Medium-Hard, 3=Medium, 4=Easy

- Progress **1 → 2 → 3 → 4** within a session (can drop back to 1)
- **First rating** drives long-term scheduling when you hit 4
- Re-insertion: 1 → positions 2–5; 2 → 10–25 ahead; 3 → 20–40 ahead; 4 → done
- All due cards appear in session (no daily cap)

## How to help

- **Extend content** at the **tail** of `data/*.txt` — do not rewrite existing cards unless asked
- Use deck-specific skills: `spanish`, `english`, `mexican`
- **Windows:** PowerShell — chain with `;`, not `&&`
- **Git:** commit only when explicitly asked

## Do not

- Edit `data/decks/*.json` by hand
- Bulk-rewrite register (tú/usted) on old cards without being asked

## After /init

Reply briefly that you understand MemoryFlashcards and are ready. Ask what they want to work on.
