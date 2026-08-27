---
name: vocab
description: Turn a daily bullet list of Spanish words/phrases into flashcards appended to data/spanish.txt. Use when the user invokes /vocab, pastes a "FLASHCARDS" list, or hands over a list of words/phrases they want to learn in Spanish.
---

# vocab

Take a rough bullet list, turn each bullet into one English→Spanish card, append to the
tail of `data/spanish.txt`, print what was added, stop.

This is a 30-second workflow. No preamble, no plan, no approval gate. Do the work.

## Input

The user pastes a list, usually from Google Keep. It may be headed `FLASHCARDS`. Bullets
are unstructured — English only, Spanish only, or a pair the user already wrote.

## Card shape

Every card is two lines, **English on top, Spanish below**, because the deck prompts in
English and answers in Spanish.

```
English prompt
Spanish answer
```

Normalize each bullet into that shape:

| Bullet form | What to do |
|---|---|
| English only — `Shark` | Translate to Spanish |
| Spanish only — `Todos los demás` | Write the English prompt for it, fix spelling/accents |
| A pair — `aqui entrenos - between you and me` | **Their pair wins.** Only reorder to English-first and fix accents. Do not "improve" their translation. |

**One bullet = one card.** Never expand a bullet into several related cards. Never merge
two bullets.

## Spanish register

- **Mexico City Spanish** wherever a regional choice exists. Prefer what is said in CDMX
  over neutral-textbook or Spain forms — `hacer el súper`, `entrar al trabajo`, `¿mande?`.
- **`tú` by default.** Infer `usted` from context only when the bullet clearly implies it:
  a fixed courtesy formula (`a sus órdenes`), a stranger, a service interaction, an elder.
  This is rare. Do not switch register on a hunch.
- Natural over literal. `I'm gonna go grocery shopping` is `Voy a hacer el súper`, not
  `Voy a ir de compras de comestibles`.
- Fix the user's typos and missing accents silently. `aqui entrenos` → `Aquí entre nos`.

## Ambiguous bullets — skip and ask

If a bullet cannot become one card without guessing — a reference you can't resolve
(`lyrics from yesterday bad bunny song`), a bullet that's really several cards, a word
whose meaning depends on context you don't have — **do not write it and do not guess.**

Write every clear bullet. Then ask about the unclear ones **in the main chat reply**, all
of them in one batch. The user answers in the thread, and you append those on the next
turn. Never ask one at a time.

A merely *ambiguous translation* (two valid CDMX words for one thing) is not a skip —
write your best pick and note the alternative in the output table.

## Writing to the file

Only ever `data/spanish.txt`. Other decks live in `backlog/` and are out of scope.

Before appending, grep the English side of the deck for near-duplicates of each new
prompt. If one already exists, skip that bullet and say so — don't append a second
near-identical card.

Then append, obeying these rules exactly:

1. **Append at the tail only.** Never insert mid-file, never reorder, never rewrite an
   existing card unless the user asks.
2. **Always an even number of lines.** Blank line between cards, blank line before the
   first appended card.
3. **CRLF line endings, UTF-8.** Match the existing file.
4. **Never touch `data/decks/*.json`.** They are auto-managed and gitignored.

Rule 1 and 2 are not style — `parser.py` pairs consecutive non-empty lines from the top of
the file and hashes `term|definition` for the card ID. An odd-line insertion mid-file
re-pairs every card after it, changes every ID, and silently wipes review progress for the
whole deck.

## Output

Print a compact table of what was appended — English, Spanish, and a short note only where
one is genuinely useful (a register choice, a regional alternative). Then the batched
questions, if any.

Do not commit. Offer to, in one line, at the end.

## Roadmap

Only `data/spanish.txt` is in scope today. Later the skill takes an optional deck name
(`/vocab flirt`) for other decks promoted out of `backlog/`. Adding one means adding its
name and its card direction here — not a redesign.
