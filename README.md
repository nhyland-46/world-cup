# Match 74 opponent model — v5 (exact Annex C routing)

Which third-placed team does the **Winner of Group E** play in **Match 74** (Round of 32)
of the 2026 FIFA World Cup — and with what probability?

The R32 pairs each group winner against one of the 8 best third-placed teams. FIFA's **Annex C**
table assigns *which* third goes to *which* winner based on the exact identity of the 8 groups
that produced qualifying thirds. v5 conditions on the actual qualifying set, reads the
deterministic Annex C assignment, and weights by how likely each set is — no aggregate-fraction
fudge, no output renormalization seam.

## Files

| File | Role |
|---|---|
| `annex_c.csv` | The official 495-row Annex C routing table (ground truth). |
| `validate.py` | The **gate**. Must pass before the model is trusted. |
| `inputs.py` | The **only** file you edit to recompute. Holds the three inputs. |
| `model_v5.py` | The model. |
| `build_annex_c.py` | One-off: regenerates `annex_c.csv` from the Wikipedia template wikitext. |

## The three inputs (`inputs.py`)

Get the numbers from the predictions app: **https://wc2026-predictions.streamlit.app/**

1. **`q_group`** — P(a group produces a qualifying third), summed over the group's four teams,
   for all 12 groups A–L. Drives the per-set weights. *Entries for A, B, C, D, F are recomputed
   from input 3 (their sum) and only cross-checked against what you put here.*
2. **`p_E_win`** — P(each Group E team finishes 1st in Group E). Sums ~1.
3. **`third_and_qualify`** — for groups **A, B, C, D, F only**, P(team finishes 3rd AND qualifies),
   per team. Per-group sum = that group's `q_group`; normalized within the group it gives which
   team is the qualifying third.

### Why only A, B, C, D, F for input 3?

Per Annex C, the **only** groups whose third can ever be routed to the Group-E-winner slot are
C, D, F, A, B (with frequencies 231, 212, 35, 16, 1 out of 495). No other group ever feeds slot
1E, so their internal team splits are never used. `validate.py` asserts these exact totals.

## Slot semantics (Match 74 → 1E)

The Annex C table (Wikipedia's *Combinations of matches in the round of 32*) lists eight winner
slots: **1A, 1B, 1D, 1E, 1G, 1I, 1K, 1L**. The column **`slot_1E`** is the group whose
**third-placed team** is routed to play the **winner of Group E** — i.e. the Match 74 opponent.
That is the only slot this model consumes. (The CSV keeps all eight slots for completeness.)

## The exact-routing logic (`model_v5.py`)

1. Enumerate the 495 qualifying sets S (each = 8 of the 12 groups produce a qualifying third).
2. **Poisson-binomial weight**: `P(S) = Π_{g∈S} q[g] · Π_{g∉S} (1 − q[g])`, then **renormalize**
   over the 495 sets so they sum to 1.
3. For each S, read `slot_1E(S) = g*` from the CSV. That set contributes the within-group team
   split of g*, weighted by `P(S)`.
4. Opponent distribution `= Σ_S P(S) · split(slot_1E(S))`.
5. Cross with `p_E_win` → full `(E winner × opponent third)` table of **absolute** probabilities,
   sorted descending. Also prints the marginal opponent-team and opponent-group distributions.

### Why the renormalization here is principled (unlike v4)

Exactly 8 thirds qualify by the rules of the tournament. Every one of the 495 sets has exactly 8
qualifiers by construction, so renormalizing `P(S)` over them is simply **conditioning on the true
event "exactly 8 thirds qualified."** v4's old "seam normalization" rescaled the *output*
distribution to paper over an aggregate-fraction approximation; v5 has no such step — the only
normalization is this legitimate conditioning, and the final table sums to 1 on its own.

## How to recompute

```bash
# 1. edit your three inputs
$EDITOR inputs.py

# 2. confirm the routing table is still trustworthy (must print ALL CHECKS PASSED)
python3 validate.py

# 3. run the model
python3 model_v5.py
```

Standard library only (`csv`, `itertools`, `math`, `collections`).

## Regenerating `annex_c.csv` (rarely needed)

`annex_c.csv` is parsed verbatim from the official table — we do **not** derive the routing rule.
Source: `Template:2026 FIFA World Cup third-place table` on Wikipedia (Annex C of the tournament
regulations). To rebuild from a fresh copy of the template wikitext saved as `tmpl_raw.txt`:

```bash
python3 build_annex_c.py   # writes annex_c.csv
python3 validate.py        # gate it
```
