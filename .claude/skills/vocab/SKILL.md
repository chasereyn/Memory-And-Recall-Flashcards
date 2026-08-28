---
name: vocab
description: Grow the Spanish deck. With a bullet list, translate each bullet into a card. Bare, with no list, pull 10 random unused pairs from the backlog archive. Use when the user invokes /vocab, pastes a "FLASHCARDS" list, or hands over words/phrases they want to learn in Spanish.
---

# vocab

Append English→Spanish cards to the tail of `data/spanish.txt`, print what was added, stop.

This is a 30-second workflow. No preamble, no plan, no approval gate. Do the work.

## Routing — pick one mode, never both

| Input | Mode |
|---|---|
| `/vocab` **alone**, nothing else in the message | **Backlog pull** — 10 random unused pairs from the archive |
| `/vocab 20` alone | Backlog pull, 20 cards |
| `/vocab` with a bullet list, or a pasted list | **Translate** — one card per bullet |

If a message has any bullets at all, it is translate mode. Bare means bare.

---

## Mode A — translate a bullet list

The user pastes a list, usually from Google Keep, sometimes headed `FLASHCARDS`. Bullets
are unstructured — English only, Spanish only, or a pair they already wrote.

Normalize each bullet into **English on top, Spanish below**:

| Bullet form | What to do |
|---|---|
| English only — `Shark` | Translate to Spanish |
| Spanish only — `Todos los demás` | Write the English prompt for it, fix spelling/accents |
| A pair — `aqui entrenos - between you and me` | **Their pair wins.** Only reorder to English-first and fix accents. Do not "improve" their translation. |

**One bullet = one card.** Never expand a bullet into several related cards. Never merge two.

### Ambiguous bullets — skip and ask

If a bullet cannot become one card without guessing — a reference you can't resolve
(`lyrics from yesterday bad bunny song`), a bullet that's really several cards, a word
whose meaning depends on context you don't have — **do not write it and do not guess.**

Write every clear bullet. Then ask about the unclear ones **in the main chat reply**, all in
one batch. The user answers in the thread and you append those next turn. Never ask one at
a time.

A merely *ambiguous translation* (two valid CDMX words for one thing) is not a skip — write
your best pick and note the alternative in the output table.

---

## Mode B — backlog pull

Source is `backlog/spanish.txt`, the ~8300-pair archive of the old bulk vocab list. Same
direction as the live deck: English on top, Spanish below.

Run the picker:

```
python .claude/skills/vocab/pull.py pick 10
```

It prints tab-separated pairs, already filtered against everything in `data/spanish.txt`
(both sides, accent- and case-insensitive) and against duplicates inside the archive
itself. Because pulled cards land in the deck, they are never picked again — that is the
whole repeat-protection mechanism. **Nothing is removed from the backlog**; it stays a
pristine archive.

**Review every pick before appending.** The archive is old and uneven:

- **Fix missing accents and inverted marks.** `Que onda?` → `¿Qué onda?`, `como esta usted`
  → `¿Cómo está usted?`. This is typo repair, not rewriting.
- **Re-cast `usted` to `tú`** unless the card is explicitly marked formal or is a fixed
  courtesy formula. The archive leans formal; the deck is tú by default. `¿Puede repetir,
  por favor?` → `¿Puedes repetir, por favor?`
- **Swap Spain forms for CDMX** — `vosotros`, `coger`, `el móvil`, `el ordenador`,
  `conducir`. Note the swap in the output table.
- **Drop a pick entirely** if it is malformed, wrong, or a near-duplicate in meaning of a
  card already in the deck. Say so and let the count come up short; do not silently
  re-roll to keep it at exactly 10.

---

## Writing to the file (both modes)

Only ever `data/spanish.txt`. Other decks live in `backlog/` and are out of scope.

Append with the picker, which enforces the file rules and re-checks duplicates:

```
printf '%s\t%s\n' 'English prompt' 'Spanish answer' ... | python .claude/skills/vocab/pull.py append
```

The rules it enforces, which apply to any hand edit too:

1. **Append at the tail only.** Never insert mid-file, never reorder, never rewrite an
   existing card unless the user asks.
2. **Always an even number of lines.** Blank line between cards, blank line before the first
   appended card.
3. **CRLF line endings, UTF-8.** Match the existing file.
4. **Never touch `data/decks/*.json`.** Auto-managed and gitignored.

Rules 1 and 2 are not style — `parser.py` pairs consecutive non-empty lines from the top of
the file and hashes `term|definition` for the card ID. An odd-line insertion mid-file
re-pairs every card after it, changes every ID, and silently wipes review progress for the
whole deck.

## Output

Print a compact table of what was appended — English, Spanish, and a short note only where
one is genuinely useful (a register fix, a regional swap, a dropped pick). Then the batched
questions, if any.

Do not commit. Offer to, in one line, at the end.

## Roadmap

Only `data/spanish.txt` is in scope. Later the skill takes a deck name (`/vocab flirt`) for
decks promoted out of `backlog/`. Adding one means adding its name and card direction here
— not a redesign.
