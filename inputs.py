"""The ONLY file you edit on recompute.

Get the numbers from the predictions app:
  https://wc2026-predictions.streamlit.app/

Three inputs (everything else is derived):

1. q_group            -- P(a group produces a qualifying third), summed over the group's
                         four teams, for ALL 12 groups A..L. Drives the Poisson-binomial
                         weights over the 495 qualifying sets.
                         NOTE: entries for A,B,C,D,F are recomputed from `third_and_qualify`
                         below (their sum), so values you put here for those five are only
                         used as a consistency cross-check, not as the live value.

2. p_E_win            -- P(each Group E team finishes 1st in Group E). Should sum ~1.

3. third_and_qualify  -- For each group that can ever play the Group-E winner
                         (A, B, C, D, F only -- per Annex C no other group feeds slot 1E),
                         P(team finishes 3rd AND qualifies as a best-eight third), per team.
                         Per-group sum = that group's q_group; normalized within group it
                         gives which team is the qualifying third.

Stub values below are placeholders so the model runs end-to-end. Replace with real numbers.
"""

GROUPS = "ABCDEFGHIJKL"

# --- Input 2: P(team wins Group E) -----------------------------------------
# Group E (2026): Germany, Ecuador, Ivory Coast, Curaçao.
p_E_win = {
    "Germany": 0.61,
    "Ecuador": 0.18,
    "Ivory Coast": 0.21,
    "Curaçao": 0.00,
}

# --- Input 3: P(team finishes 3rd AND qualifies) for the 5 routable groups --
# Only A, B, C, D, F can ever be routed to the Group-E winner (slot 1E).
third_and_qualify = {
    # Group A: Mexico, South Korea, South Africa, Czech Republic
    "A": {"Mexico": 0.30, "South Korea": 0.20, "South Africa": 0.10, "Czech Republic": 0.07},
    # Group B: Canada, Switzerland, Qatar, Bosnia and Herzegovina
    "B": {"Canada": 0.25, "Switzerland": 0.20, "Qatar": 0.15, "Bosnia and Herzegovina": 0.07},
    # Group C: Brazil, Morocco, Scotland, Haiti
    "C": {"Brazil": 0.35, "Morocco": 0.20, "Scotland": 0.10, "Haiti": 0.05},
    # Group D: United States, Turkey, Paraguay, Australia
    "D": {"United States": 0.30, "Turkey": 0.22, "Paraguay": 0.10, "Australia": 0.05},
    # Group F: Netherlands, Japan, Sweden, Tunisia
    "F": {"Netherlands": 0.28, "Japan": 0.20, "Sweden": 0.12, "Tunisia": 0.07},
}

# --- Input 1: P(group produces a qualifying third), all 12 groups -----------
# A,B,C,D,F here are cross-checked against the sums of third_and_qualify (and
# overridden by them at runtime). E,G,H,I,J,K,L are used as-is.
q_group = {
    "A": 0.67,  # cross-check vs sum(third_and_qualify["A"]) = 0.67
    "B": 0.67,  # cross-check vs sum(third_and_qualify["B"]) = 0.67
    "C": 0.70,  # cross-check vs sum(third_and_qualify["C"]) = 0.70
    "D": 0.67,  # cross-check vs sum(third_and_qualify["D"]) = 0.67
    "F": 0.67,  # cross-check vs sum(third_and_qualify["F"]) = 0.67
    "E": 0.67,
    "G": 0.67,
    "H": 0.67,
    "I": 0.67,
    "J": 0.67,
    "K": 0.67,
    "L": 0.67,
}
