---
name: spanish
description: Grow the Spanish deck by translating a list of bullets into cards. Use when the user invokes /spanish, pastes a "FLASHCARDS" list, or hands over words/phrases they want to learn in Spanish.
---

# spanish

Append English→Spanish cards to the tail of `data/spanish.txt`, print what was added, stop.

This is a 30-second workflow. No preamble, no plan, no approval gate. Do the work.

## Input is always a list

`/spanish` takes bullets — usually pasted from Google Keep, sometimes headed `FLASHCARDS`.
There is no other mode. If the message has no list, ask for one in a single line; do not
invent cards, and do not go looking for a source to pull from.

Bullets are unstructured — English only, Spanish only, or a pair he already wrote.
Normalize each into **English on top, Spanish below**:

| Bullet form | What to do |
|---|---|
| English only — `Shark` | Translate to Spanish |
| Spanish only — `Todos los demás` | Write the English prompt for it, fix spelling/accents |
| A pair — `aqui entrenos - between you and me` | **His pair wins.** Only reorder to English-first and fix accents. Do not "improve" the translation. |

**One bullet = one card.** Never expand a bullet into several related cards. Never merge two.

## Write for the mouth, not the eye

The deck exists so he can *say* these, fast, in a real conversation. That shapes the
Spanish side:

- **CDMX usage over neutral-textbook or Spain forms.** `carro` not `coche`, `depa` not
  `apartamento`, `chido` not `guay`.
- **`tú` by default.** Infer `usted` only from clear context; it's rare.
- **The register he'd actually use** — casual, contracted, spoken. `Ahorita voy` beats
  `Voy a ir en este momento`.
- **Keep the English prompt specific enough to cue one answer.** A vague prompt trains
  nothing, because any of five phrases would satisfy it.

## Ambiguous bullets — skip and ask

If a bullet cannot become one card without guessing — a reference you can't resolve
(`lyrics from yesterday bad bunny song`), a bullet that's really several cards, a word
whose meaning depends on context you don't have — **do not write it and do not guess.**

Write every clear bullet. Then ask about the unclear ones **in the main chat reply**, all in
one batch. He answers in the thread and you append those next turn. Never ask one at a time.

A merely *ambiguous translation* (two valid CDMX words for one thing) is not a skip — write
your best pick and note the alternative in the output table.

## Writing to the file

Only ever `data/spanish.txt`. The other decks in `data/` are not grown by this skill.

Append directly. The rules:

1. **Append at the tail only.** Never insert mid-file, never reorder, never rewrite an
   existing card unless he asks.
2. **Always an even number of lines.** Blank line between cards, blank line before the first
   appended card.
3. **CRLF line endings, UTF-8.** Match the existing file.
4. **Never touch `data/decks/*.json`.** Auto-managed and gitignored.
5. **Check for duplicates first** against the whole of `data/spanish.txt`, accent- and
   case-insensitively, on the Spanish side. Drop a bullet that's already a card and say so.

Rules 1 and 2 are not style — `parser.py` pairs consecutive non-empty lines from the top of
the file and hashes `term|definition` for the card ID. An odd-line insertion mid-file
re-pairs every card after it, changes every ID, and silently wipes review progress for the
whole deck.

## Output

Print a compact table of what was appended — English, Spanish, and a short note only where
one is genuinely useful (a register fix, a regional swap, a dropped duplicate). Then the
batched questions, if any.

Do not commit on your own. Offer it in one line at the end — and when he says yes,
**commit and push to the remote in the same step.** A yes to "commit?" is a yes to pushing;
never leave the commit sitting local.
