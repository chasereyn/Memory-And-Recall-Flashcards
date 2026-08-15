---
name: spanish
description: Appends vocabulary to MemoryFlashcards `data/spanish.txt` (English prompt, Spanish answer, blank line between cards). Use when editing the main Spanish vocab deck.
disable-model-invocation: true
---

# Spanish vocab deck (`data/spanish.txt`)

## Format

One card = term line, definition line, blank line:

```
English prompt
Spanish answer

Who's laughing now?
¿quién se ríe ahora?
```

- **Append** at the **tail** only
- One English prompt + one Spanish answer per card (no minimal-swap pattern)

## Style

- Phrases often **lowercase** unless ¿ / ¡ required
- Countable nouns: include article where the deck uses one (`el buzón`, `la lluvia de ideas`)
- Ambiguous English: split into two cards (e.g. noun vs verb senses)
- Match **Latin American–leaning** usage already in the file

## After editing

`python main.py` syncs on startup — new cards get default progress.
