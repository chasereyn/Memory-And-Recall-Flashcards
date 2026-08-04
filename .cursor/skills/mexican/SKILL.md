---
name: mexican
description: Appends cards to MemoryFlashcards `data/mexican.txt` (name or prompt, vivid English definition). Mexican food, culture, geography, history, brands. NOT general Spanish vocab — use spanish.txt for that.
disable-model-invocation: true
---

# Mexican deck (`data/mexican.txt`)

## Format

One card = term line, English description, blank line:

```
pozole
spicy Mexican soup with pork, hominy, radish, cabbage, and lime — often red, white, or green

Tlaloc
Aztec god of rain, lightning, and fertility — goggled eyes, jade offerings, tied to agriculture

```

**In scope:** foods, places, people, traditions, brands, cultural references tied to Mexico  
**Out of scope:** general vocab and English→Spanish phrases (use `spanish.txt`)

## Style

- Food: sensory English description (ingredients, texture, how it's eaten)
- Places/people: what/where/who and why it matters
- Prefer **name → description** over question format

## After editing

`python main.py` syncs on startup — append at the **tail** only.
