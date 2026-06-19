"""Parse the official Annex C table (Wikipedia's transcluded template) into a clean CSV.

Source: Template:2026 FIFA World Cup third-place table (raw wikitext in tmpl_raw.txt),
which reproduces Annex C of the FIFA 2026 tournament regulations: the 495 possible
combinations of which eight third-placed teams qualify, and which group winner each one
plays in the round of 32.

We do NOT derive the routing rule. We ingest the official table verbatim.

Table layout per row (in the wikitext):
  - 12 group-membership cells for groups A..L: bolded letter '''X''' means group X's
    third qualified; empty cell means it did not. Exactly 8 are bolded.
  - 8 assignment cells, in the fixed winner-slot order: 1A, 1B, 1D, 1E, 1G, 1I, 1K, 1L.
    Each holds a token '3X' = the third-placed team of group X routed to that winner.

The union of the eight '3X' groups equals the qualifying set (cross-checked below).
slot_1E is the 4th assignment column: the group whose third plays the Group-E winner
(Match 74).
"""
import csv
import re

SRC = "tmpl_raw.txt"
OUT = "annex_c.csv"

# Fixed winner-slot order as defined by the table header.
SLOT_ORDER = ["1A", "1B", "1D", "1E", "1G", "1I", "1K", "1L"]
SLOT_COLS = [f"slot_{s}" for s in SLOT_ORDER]

ROW_START = re.compile(r'^!\s*scope="row"\s*\|\s*(\d+)\s*$')
BOLD_GROUP = re.compile(r"'''([A-L])'''")
THIRD_TOKEN = re.compile(r"\b3([A-L])\b")


def parse_rows(text):
    lines = text.splitlines()
    # Collect each row as: the row number + the wikitext lines belonging to it,
    # up to the next row start (or end of table).
    rows = []
    i = 0
    n = len(lines)
    while i < n:
        m = ROW_START.match(lines[i].strip())
        if not m:
            i += 1
            continue
        rownum = int(m.group(1))
        i += 1
        block = []
        while i < n and not ROW_START.match(lines[i].strip()):
            # Stop at table terminator.
            if lines[i].strip().startswith("|}"):
                break
            block.append(lines[i])
            i += 1
        rows.append((rownum, "\n".join(block)))
    return rows


def main():
    with open(SRC, encoding="utf-8") as f:
        text = f.read()

    parsed = parse_rows(text)
    if len(parsed) != 495:
        raise SystemExit(f"Expected 495 rows, parsed {len(parsed)}")

    out_rows = []
    for rownum, block in parsed:
        bolded = BOLD_GROUP.findall(block)
        thirds = THIRD_TOKEN.findall(block)

        if len(bolded) != 8:
            raise SystemExit(f"Row {rownum}: expected 8 bolded groups, got {len(bolded)}: {bolded}")
        if len(thirds) != 8:
            raise SystemExit(f"Row {rownum}: expected 8 third tokens, got {len(thirds)}: {thirds}")

        qualifying = "".join(sorted(set(bolded)))
        if len(qualifying) != 8:
            raise SystemExit(f"Row {rownum}: bolded groups not distinct: {bolded}")

        # Cross-check: the union of routed thirds must equal the qualifying set.
        if "".join(sorted(set(thirds))) != qualifying:
            raise SystemExit(
                f"Row {rownum}: routed thirds {sorted(set(thirds))} != qualifying set {qualifying}"
            )

        record = {"no": rownum, "qualifying_groups": qualifying}
        for col, g in zip(SLOT_COLS, thirds):
            record[col] = g
        out_rows.append(record)

    fieldnames = ["no", "qualifying_groups"] + SLOT_COLS
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)

    print(f"Wrote {len(out_rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
