"""Word picker for the /english skill.

  next [N]   list the next N words from backlog/english.txt
  append     read TSV `definition<TAB>word` on stdin, append to data/english.txt,
             then delete those words from the backlog
  sync       delete any backlog word that is already in the deck

The deck is definition-on-top: line 1 is the prompt (the definition), line 2 is
the answer (the word to recall). That is the opposite of data/spanish.txt.

The backlog is a queue, not an archive - a word leaves it once it is a card, so
the file shrinks as the deck grows and there is no cursor to track.
"""
import os
import re
import sys
import unicodedata

WORDS = "backlog/english.txt"
DECK = "data/english.txt"


def norm(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^\w\s]", "", s, flags=re.UNICODE)
    return re.sub(r"\s+", " ", s).strip().lower()


def read_words():
    return [w for w in (l.strip() for l in open(WORDS, encoding="utf-8")) if w]


def deck_words():
    """Normalized answers already in the deck (the second line of each pair)."""
    try:
        txt = open(DECK, encoding="utf-8").read()
    except FileNotFoundError:
        return set()
    got = set()
    for block in re.split(r"(?:\r?\n){2,}", txt):
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if len(lines) == 2:
            got.add(norm(lines[1]))
    return got


def drop_from_backlog(words):
    """Remove the given words, keeping the order of everything left behind."""
    targets = {norm(w) for w in words}
    kept = [w for w in read_words() if norm(w) not in targets]
    with open(WORDS, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(kept) + ("\n" if kept else ""))


def cmd_next(n):
    todo = read_words()
    for w in todo[:n]:
        print(w)
    print(f"# {min(n, len(todo))} of {len(todo)} left on the list", file=sys.stderr)


def cmd_append():
    have = deck_words()
    new = []
    for line in sys.stdin.read().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" not in line:
            sys.exit(f"ERROR: need `definition<TAB>word`: {line!r}")
        d, w = (x.strip() for x in line.split("\t", 1))
        if not d or not w:
            sys.exit(f"ERROR: empty side: {line!r}")
        if norm(w) in have:
            print(f"skip (already in deck): {w}", file=sys.stderr)
            continue
        have.add(norm(w))
        new.append((d, w))
    if not new:
        print("nothing to append", file=sys.stderr)
        return

    lead = "\r\n" if os.path.exists(DECK) and os.path.getsize(DECK) else ""
    block = lead + "\r\n\r\n".join(f"{d}\r\n{w}" for d, w in new) + "\r\n"
    with open(DECK, "a", encoding="utf-8", newline="") as f:
        f.write(block)
    print(f"appended {len(new)} cards ({len(new) * 2} lines)", file=sys.stderr)

    # Only after the deck write succeeds, so a failure can never eat words.
    drop_from_backlog(w for _, w in new)
    print(f"removed {len(new)} from the backlog ({len(read_words())} left)",
          file=sys.stderr)


def cmd_sync():
    have = deck_words()
    stale = [w for w in read_words() if norm(w) in have]
    if not stale:
        print("backlog already clean", file=sys.stderr)
        return
    drop_from_backlog(stale)
    print(f"removed {len(stale)} already in the deck ({len(read_words())} left): "
          f"{', '.join(stale)}", file=sys.stderr)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "next":
        cmd_next(int(args[1]) if len(args) > 1 else 10)
    elif args[0] == "append":
        cmd_append()
    elif args[0] == "sync":
        cmd_sync()
    else:
        sys.exit(__doc__)
