"""Backlog picker for the /vocab skill.

Two subcommands:
  pick [N]   sample N unused pairs from backlog/spanish.txt, print as TSV
  append     read final TSV pairs on stdin, append to the tail of data/spanish.txt

Reads the backlog by blank-line-separated blocks and keeps only clean 2-line
blocks, so a stray orphan line in the archive cannot shift the pairing the way
parser.py's consecutive-line pairing would.
"""
import random
import re
import sys
import unicodedata

BACKLOG = "backlog/spanish.txt"
DECK = "data/spanish.txt"


def norm(s):
    """Fold for duplicate comparison: no accents, no punctuation, lowercase."""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^\w\s]", "", s, flags=re.UNICODE)
    return re.sub(r"\s+", " ", s).strip().lower()


def read_pairs(path):
    try:
        txt = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        return []
    pairs = []
    for block in re.split(r"(?:\r?\n){2,}", txt):
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if len(lines) == 2:
            pairs.append((lines[0], lines[1]))
    return pairs


def deck_keys():
    """Normalized English and Spanish sides already in the live deck."""
    en, es = set(), set()
    for t, d in read_pairs(DECK):
        en.add(norm(t))
        es.add(norm(d))
    return en, es


def cmd_pick(n):
    en, es = deck_keys()
    pool = [p for p in read_pairs(BACKLOG)
            if norm(p[0]) not in en and norm(p[1]) not in es]
    seen = set()
    unique = []
    for t, d in pool:
        k = (norm(t), norm(d))
        if k not in seen:
            seen.add(k)
            unique.append((t, d))
    n = min(n, len(unique))
    for t, d in random.sample(unique, n):
        print(f"{t}\t{d}")
    print(f"# {n} picked from {len(unique)} unused of {len(read_pairs(BACKLOG))}",
          file=sys.stderr)


def cmd_append():
    en, es = deck_keys()
    new = []
    for line in sys.stdin.read().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" not in line:
            sys.exit(f"ERROR: not a TSV pair: {line!r}")
        t, d = (x.strip() for x in line.split("\t", 1))
        if not t or not d:
            sys.exit(f"ERROR: empty side: {line!r}")
        if norm(t) in en or norm(d) in es:
            print(f"skip (already in deck): {t}", file=sys.stderr)
            continue
        en.add(norm(t))
        es.add(norm(d))
        new.append((t, d))
    if not new:
        print("nothing to append", file=sys.stderr)
        return
    block = "".join(f"\r\n{t}\r\n{d}\r\n" for t, d in new)
    with open(DECK, "a", encoding="utf-8", newline="") as f:
        f.write(block)
    print(f"appended {len(new)} cards ({len(new) * 2} lines)", file=sys.stderr)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "pick":
        cmd_pick(int(args[1]) if len(args) > 1 else 10)
    elif args[0] == "append":
        cmd_append()
    else:
        sys.exit(__doc__)
