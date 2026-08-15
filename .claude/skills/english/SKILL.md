---
name: english
description: Expands vocabulary in MemoryFlashcards `data/english.txt` using the gloss/headword + minimal-swap paired-sentence pattern (two cards per item). Use when editing the English deck.
disable-model-invocation: true
---

# English deck (`data/english.txt`)

## Format

One vocabulary item = **two cards** (four lines + blank):

```
very bad
abysmal

The team's performance was terrible in last night's game.
The team's performance was abysmal in last night's game.

```

**Card 1:** gloss → headword  
**Card 2:** plain example sentence → same sentence with only the headword swapped in

## Minimal-swap rule

- Identical sentence frames; second line differs by **one substitution**
- Multiword headwords: swap the whole phrase as one unit
- Do not compose a second sentence from scratch

## After editing

`python main.py` syncs on startup — append at the **tail** only.
