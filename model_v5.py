"""Match 74 opponent model -- v5 (exact Annex C routing).

Which third-placed team does the Winner of Group E play in the Round of 32 (Match 74)?

Approach (no fudge):
  - Enumerate the 495 qualifying sets S (each = 8 of 12 groups produce a qualifying third).
  - Poisson-binomial weight  P(S) = prod_{g in S} q[g] * prod_{g not in S} (1 - q[g]),
    then RENORMALIZE over the 495 sets. This conditions on "exactly 8 thirds qualified",
    which is the real-world constraint -- a legitimate renormalization, not v4's seam fudge.
  - For each S, the official Annex C table (annex_c.csv, slot_1E column) deterministically
    names the group g* whose third plays the Group-E winner. That set contributes the
    within-group team split p_team_given_group_qualifies[g*], weighted by P(S).
  - Opponent distribution = sum_S P(S) * split(slot_1E(S)).
  - Cross with p_E_win for the full (E winner x opponent) table of absolute probabilities.

Stdlib only.
"""
import csv
import itertools
from collections import defaultdict

import inputs

CSV_PATH = "annex_c.csv"
ROUTABLE = ("A", "B", "C", "D", "F")  # only these can feed slot_1E (per Annex C)
TOL = 1e-9


def load_annex_c(path=CSV_PATH):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 495:
        raise SystemExit(f"{path} has {len(rows)} rows, expected 495 -- run validate.py")
    return rows


def build_q_group():
    """Full 12-group q vector. A,B,C,D,F derived from third_and_qualify (overriding inputs.q_group)."""
    q = dict(inputs.q_group)
    warnings = []
    for g in ROUTABLE:
        derived = sum(inputs.third_and_qualify[g].values())
        stated = inputs.q_group.get(g)
        if stated is not None and abs(stated - derived) > 1e-6:
            warnings.append(
                f"q_group[{g}]={stated} differs from sum(third_and_qualify[{g}])={derived:.4f}; using derived."
            )
        q[g] = derived
    missing = [g for g in inputs.GROUPS if g not in q]
    if missing:
        raise SystemExit(f"q_group missing groups: {missing}")
    return q, warnings


def build_team_splits():
    """Within-group conditional: P(team is the qualifying third | group qualifies)."""
    splits = {}
    for g, teams in inputs.third_and_qualify.items():
        total = sum(teams.values())
        if total <= 0:
            raise SystemExit(f"third_and_qualify[{g}] sums to {total}")
        splits[g] = {t: v / total for t, v in teams.items()}
    return splits


def set_weights(rows, q):
    """Renormalized Poisson-binomial weight per qualifying set."""
    weights = []
    for r in rows:
        S = set(r["qualifying_groups"])
        w = 1.0
        for g in inputs.GROUPS:
            w *= q[g] if g in S else (1.0 - q[g])
        weights.append(w)
    total = sum(weights)
    if total <= 0:
        raise SystemExit("All set weights are zero -- check q_group values.")
    return [w / total for w in weights]


def compute():
    rows = load_annex_c()
    q, warnings = build_q_group()
    splits = build_team_splits()
    weights = set_weights(rows, q)

    opp_team = defaultdict(float)   # opponent team -> probability
    opp_group = defaultdict(float)  # opponent group -> probability
    for r, w in zip(rows, weights):
        g = r["slot_1E"]
        opp_group[g] += w
        for team, frac in splits[g].items():
            opp_team[team] += w * frac

    # Full joint table: (E winner, opponent team) -> absolute probability.
    joint = {}
    for e_team, pe in inputs.p_E_win.items():
        for opp, po in opp_team.items():
            joint[(e_team, opp)] = pe * po

    return {
        "q_group": q,
        "warnings": warnings,
        "opp_team": dict(opp_team),
        "opp_group": dict(opp_group),
        "joint": joint,
    }


def _fmt_pct(x):
    return f"{100 * x:6.2f}%"


def main():
    res = compute()

    for w in res["warnings"]:
        print(f"[warn] {w}")
    if res["warnings"]:
        print()

    print("Effective q_group (P group yields a qualifying third):")
    for g in inputs.GROUPS:
        print(f"  {g}: {res['q_group'][g]:.4f}")
    print()

    print("Marginal P(opponent's GROUP) for the Group-E winner (Match 74):")
    for g, p in sorted(res["opp_group"].items(), key=lambda kv: -kv[1]):
        print(f"  3{g}: {_fmt_pct(p)}")
    print(f"  total: {_fmt_pct(sum(res['opp_group'].values()))}")
    print()

    print("Marginal P(opponent TEAM) for the Group-E winner:")
    for t, p in sorted(res["opp_team"].items(), key=lambda kv: -kv[1]):
        print(f"  {t}: {_fmt_pct(p)}")
    print(f"  total: {_fmt_pct(sum(res['opp_team'].values()))}")
    print()

    print("Full Match-74 table  (E winner  x  opponent third)  -- absolute probabilities:")
    for (e_team, opp), p in sorted(res["joint"].items(), key=lambda kv: -kv[1]):
        print(f"  1E={e_team:>3}  vs  {opp:>3}:  {_fmt_pct(p)}")
    print(f"  total: {_fmt_pct(sum(res['joint'].values()))}")


if __name__ == "__main__":
    main()
