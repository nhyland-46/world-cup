"""Gate for annex_c.csv. The whole point of v5 is a provably-correct routing table,
so the model must not run until every assertion here passes.

Run: python3 validate.py   (exit code 0 = green)
"""
import csv
import itertools
import sys
from collections import Counter
from math import comb

GROUPS = "ABCDEFGHIJKL"
SLOT_COLS = ["slot_1A", "slot_1B", "slot_1D", "slot_1E", "slot_1G", "slot_1I", "slot_1K", "slot_1L"]

# Known aggregate totals for slot_1E (groups whose third can ever play the Group-E winner).
EXPECTED_1E = {"C": 231, "D": 212, "F": 35, "A": 16, "B": 1}
# Every group qualifies in exactly C(11,7) of the C(12,8) eight-subsets.
EXPECTED_APPEARANCES = comb(11, 7)  # 330
EXPECTED_TOTAL_SETS = comb(12, 8)   # 495


def fail(msg):
    print(f"  FAIL: {msg}")
    return False


def main(path="annex_c.csv"):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    ok = True
    checks = []

    # 1. Exactly 495 rows.
    if len(rows) != EXPECTED_TOTAL_SETS:
        ok = fail(f"row count {len(rows)} != {EXPECTED_TOTAL_SETS}")
    else:
        checks.append(f"row count == {EXPECTED_TOTAL_SETS}")

    # 2. Each qualifying_groups is a distinct sorted 8-subset of A-L.
    seen = set()
    all_8subsets = {"".join(c) for c in itertools.combinations(GROUPS, 8)}
    for r in rows:
        qg = r["qualifying_groups"]
        if qg in seen:
            ok = fail(f"duplicate qualifying_groups {qg}")
            continue
        seen.add(qg)
        if len(qg) != 8 or any(c not in GROUPS for c in qg):
            ok = fail(f"{qg} is not 8 letters from A-L")
        elif list(qg) != sorted(qg):
            ok = fail(f"{qg} is not sorted")
    missing = all_8subsets - seen
    extra = seen - all_8subsets
    if missing:
        ok = fail(f"{len(missing)} expected 8-subsets missing, e.g. {sorted(missing)[:3]}")
    if extra:
        ok = fail(f"{len(extra)} unexpected sets present, e.g. {sorted(extra)[:3]}")
    if not missing and not extra and len(seen) == EXPECTED_TOTAL_SETS:
        checks.append("qualifying_groups == all 495 distinct sorted 8-subsets of A-L")

    # 3. Per row: every routed group is in the qualifying set; 8 slots are 8 distinct groups.
    routing_ok = True
    for r in rows:
        qg = set(r["qualifying_groups"])
        routed = [r[c] for c in SLOT_COLS]
        for c, g in zip(SLOT_COLS, routed):
            if g not in qg:
                ok = routing_ok = fail(f"row {r['no']}: {c}={g} not in qualifying set {r['qualifying_groups']}")
        if len(set(routed)) != 8:
            ok = routing_ok = fail(f"row {r['no']}: 8 slots not distinct: {routed}")
    if routing_ok:
        checks.append("every routed third belongs to its set; 8 slots are 8 distinct groups")

    # 4a. Aggregate reconstruction of slot_1E.
    counts_1e = Counter(r["slot_1E"] for r in rows)
    if dict(counts_1e) == EXPECTED_1E:
        checks.append(f"slot_1E totals == {EXPECTED_1E} (sum {sum(EXPECTED_1E.values())})")
    else:
        ok = fail(f"slot_1E totals {dict(sorted(counts_1e.items()))} != {EXPECTED_1E}")
    # No other group may feed 1E.
    others = {g: counts_1e.get(g, 0) for g in GROUPS if g not in EXPECTED_1E}
    if any(v != 0 for v in others.values()):
        ok = fail(f"groups outside C/D/F/A/B feed slot_1E: {[g for g,v in others.items() if v]}")
    else:
        checks.append("no group outside C/D/F/A/B ever feeds slot_1E")

    # 4b. Each group appears in exactly C(11,7)=330 qualifying sets.
    appearances = Counter()
    for r in rows:
        for g in r["qualifying_groups"]:
            appearances[g] += 1
    bad = {g: appearances[g] for g in GROUPS if appearances[g] != EXPECTED_APPEARANCES}
    if bad:
        ok = fail(f"appearance counts != {EXPECTED_APPEARANCES}: {bad}")
    else:
        checks.append(f"every group appears in exactly {EXPECTED_APPEARANCES} sets")

    print("Annex C validation")
    print("==================")
    for c in checks:
        print(f"  PASS: {c}")
    print("==================")
    if ok:
        print("ALL CHECKS PASSED — annex_c.csv is trusted.")
        return 0
    print("VALIDATION FAILED — do not run the model.")
    return 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
