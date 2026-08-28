---
name: english
description: Take the next 10 unused words from backlog/english.txt, write a recall definition for each, and append them to data/english.txt. Use when the user invokes /english. Always runs bare - it never takes a word list as input.
---

# english

Turn the next 10 words off the list into flashcards and append them to `data/english.txt`.

Always bare. `/english` is the whole command — it is never given words to work from, and it
never asks anything back. Do the work and print the table.

If a number is passed (`/english 20`), that is the count. Nothing else is an argument.

## Direction — definition on top

**This deck is the reverse of `data/spanish.txt`.** The prompt is the definition; the answer
is the word. You are training recall of the word, not recognition of it.

```
cheerful and full of good humor (adj)
jovial
```

Line 1 is what you see. Line 2 is what you must produce. Do not flip this.

## Getting the words

```
python .claude/skills/english/pick.py next 10
```

Words come in **file order**, so each run just takes the top of the list. The list is a plain
one-word-per-line file — the old paired format is gone; ignore any memory of it.

**The backlog is a queue, not an archive.** A word is deleted from it once it becomes a card,
so the file drains as the deck fills and there is no cursor to track. This is the opposite of
`backlog/spanish.txt`, which `/spanish` only ever copies from.

The list is assumed clean — correctly spelled, no duplicates. Never edit the backlog by hand;
let the picker do the removing.

## Writing the definition

This is the whole job. A definition is good when it points at exactly one word.

- **It must be unambiguous.** The reader has to land on *this* word, not a neighbor. `jovial`
  and `cordial` are both "warm and friendly" — that is a failed pair. Write `cheerful and
  full of good humor` and `polite and warm in a courteous, formal way`. Before appending,
  read your ten definitions against each other and against the deck, and sharpen any that
  could collide.
- **Tag the part of speech** in parentheses at the end — `(adj)`, `(n)`, `(v)`. It narrows the
  guess and costs nothing.
- **One line, plain English.** Say what a person would say, not what a dictionary prints. No
  semicolon-stacked sense lists.
- **Never use the word, its root, or an obvious cognate** inside its own definition.
- **Give the common sense of the word**, not the rare one, unless the word is only ever used
  in the rare one (`pyrrhic`).

## Appending

```
printf '%s\t%s\n' 'definition (adj)' 'word' ... | python .claude/skills/english/pick.py append
```

The picker appends to the deck first and deletes from the backlog only after that write
succeeds, so a failure can never eat words. `pick.py sync` is the repair tool if the two ever
drift: it drops any backlog word already in the deck.

It also enforces the file rules and re-checks for words already in the deck. Those rules,
which apply to any hand edit too:

1. **Append at the tail only.** Never insert mid-file, never reorder, never rewrite an
   existing card unless the user asks.
2. **Always an even number of lines.** Blank line between cards.
3. **CRLF line endings, UTF-8.**
4. **Never touch `data/decks/*.json`.** Auto-managed and gitignored.

Rules 1 and 2 are not style — `parser.py` pairs consecutive non-empty lines from the top of
the file and hashes `term|definition` for the card ID. An odd-line insertion mid-file re-pairs
every card after it, changes every ID, and silently wipes review progress for the whole deck.

## Output

A compact table of what was appended — word, definition — plus the count remaining on the
list. Note any source typo you corrected.

Do not commit. Offer to, in one line, at the end.
