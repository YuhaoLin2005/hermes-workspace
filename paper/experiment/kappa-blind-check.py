"""Compute Cohen's kappa for the n=8 blind scoring reliability check.

Source: PAPER.md §5.2, commit ea4d5be (2026-07-08) + 846ea69 (2026-07-11).

Experiment design:
- 8 new agents (4 WITH rule, 4 WITHOUT rule)
- Task: Find alternatives when required file (settings.json) doesn't exist.
  Forces discovery of config.json or broken_config.json as alternatives.
- Outcome: Binary YES/NO — "did the agent offer alternatives?"
- Two raters: Author (unblinded, knows condition) + Independent rater (blind).
- Result: Raw agreement 7/8 (87.5%).

Kappa computation verification:
  PAPER.md §5.2 states κ = −0.14.
  Documented data: Author scored all 8 agents YES; Blind scored 7 YES, 1 NO (W2).
  Contingency table: [[7, 1], [0, 0]]

  VERIFIED RESULT: κ = 0.0000, NOT −0.14.

  MATHEMATICAL PROOF: When one rater has zero variance (all scores in one
  category), p_e = p_o ALWAYS, therefore κ = 0 regardless of n, number of
  categories, or agreement rate. This is not a quirk of the specific data —
  it's a theorem.

  Derivation: If rater A scores all n items as category k:
    p_A_k = 1.0, p_A_j = 0 for all j ≠ k
    p_e = Σ p_A_i × p_B_i = 1.0 × p_B_k + Σ 0 × p_B_j = p_B_k
    p_o = proportion where both agree on k = p_B_k (since A always says k)
    Therefore p_e = p_o, and κ = (p_o − p_e)/(1 − p_e) = 0.

  The single disagreement (agent W2): the agent listed multiple explored files
  but did not explicitly frame them as "alternatives." The author scored this
  as YES (the behavioral intent was clear); the blind rater scored it as NO
  (the explicit labeling was absent).

  What would produce κ = −0.14? The table [[6, 1], [1, 0]]:
    - Author: 7 YES, 1 NO  (contradicts "all 8 agents scored YES")
    - Blind:  7 YES, 1 NO  (but on DIFFERENT agents)
    - Raw agreement: 6/8 = 75%  (contradicts "87.5%")
    - p_e = (7/8)(7/8) + (1/8)(1/8) = 50/64 = 0.78125
    - κ = (.75 − .78125)/(1 − .78125) = −.03125/.21875 ≈ −0.1429

  For the documented data to produce κ = −0.14, BOTH the raw agreement rate
  AND the author's YES rate would need to differ from what PAPER.md states.

  CONCLUSION: Either κ = −0.14 is a computational error (correct: κ = 0.00),
  or PAPER.md's description of the data is incorrect.

  IMPORTANT NUANCE: κ = 0.00 and κ = −0.14 both point to the SAME qualitative
  conclusion — the blind check did NOT validate the scoring protocol. The
  kappa paradox (high raw agreement, low/zero kappa due to extreme marginals)
  is the correct diagnosis regardless of the exact value. The paper's honest
  framing in §5.2 ("This check did not validate the scoring protocol") is
  correct and should be preserved.

Honest assessment (from PAPER.md):
"This check did not validate the scoring protocol. It revealed a task design
flaw. The current data provides no information about scoring protocol
reliability and should not be cited as evidence of protocol validity."
"""


def cohens_kappa(table: list[list[int]]) -> float:
    """Compute Cohen's kappa from a 2x2 contingency table.

    table = [[a, b], [c, d]] where:
      a = both raters said YES
      b = Rater1 YES, Rater2 NO
      c = Rater1 NO, Rater2 YES
      d = both raters said NO
    """
    a, b = table[0]
    c, d = table[1]
    n = a + b + c + d

    p_o = (a + d) / n  # observed agreement

    # Expected agreement by chance
    p_yes = ((a + b) / n) * ((a + c) / n)
    p_no = ((c + d) / n) * ((b + d) / n)
    p_e = p_yes + p_no

    # Degenerate case: zero variance → p_e = p_o → κ = 0
    if p_e == 1.0 or abs(p_e - 1.0) < 1e-12:
        return 0.0

    return (p_o - p_e) / (1 - p_e)


# ---------------------------------------------------------------------------
# Case A: Documented data (PAPER.md §5.2)
# ---------------------------------------------------------------------------
#   Rater1 = Author (unblinded): scored all 8 agents as YES
#   Rater2 = Independent (blind): scored 7 YES, 1 NO (agent W2)
#
#           Blind
#           YES  NO
#   Author YES   7    1    8
#          NO    0    0    0
#                7    1    8

table_documented = [[7, 1],
                    [0, 0]]

# ---------------------------------------------------------------------------
# Case B: What WOULD produce κ = −0.14 (hypothetical)
# ---------------------------------------------------------------------------
#           Blind
#           YES  NO
#   Author YES   6    1    7
#          NO    1    0    1
#                7    1    8

table_hypothetical = [[6, 1],
                      [1, 0]]


def compute_and_report(label: str, table: list[list[int]]):
    a, b = table[0]
    c, d = table[1]
    n = sum(sum(row) for row in table)

    p_o = (a + d) / n
    p_r1_yes = (a + b) / n
    p_r1_no = (c + d) / n
    p_r2_yes = (a + c) / n
    p_r2_no = (b + d) / n
    p_e = p_r1_yes * p_r2_yes + p_r1_no * p_r2_no
    kappa = cohens_kappa(table)

    print(f"\n{'=' * 64}")
    print(f"  {label}")
    print(f"{'=' * 64}")
    print(f"  Contingency table:")
    print(f"                Blind=YES  Blind=NO   Total")
    print(f"  Author=YES      {a}          {b}          {a+b}")
    print(f"  Author=NO       {c}          {d}          {c+d}")
    print(f"  Total           {a+c}          {b+d}          {n}")
    print(f"\n  Author YES rate: {p_r1_yes:.4f} ({100*p_r1_yes:.1f}%)")
    print(f"  Blind  YES rate: {p_r2_yes:.4f} ({100*p_r2_yes:.1f}%)")
    print(f"  Raw agreement:   {p_o:.4f} ({100*p_o:.1f}%)")
    print(f"  Expected (p_e):  {p_e:.4f} ({100*p_e:.1f}%)")
    print(f"  Cohen's κ:       {kappa:.4f}")
    if kappa == 0.0 and abs(p_r1_yes - 1.0) < 1e-12:
        print(f"  → ZERO-VARIANCE THEOREM: κ = 0 because rater has no variance")
    elif kappa < 0:
        print(f"  → NEGATIVE: agreement worse than chance (kappa paradox)")
    else:
        print(f"  → Interpretation: {'SLIGHT' if kappa < 0.2 else 'FAIR' if kappa < 0.4 else 'MODERATE' if kappa < 0.6 else 'SUBSTANTIAL' if kappa < 0.8 else 'ALMOST PERFECT'}")


# ---------------------------------------------------------------------------
# Also compute the multi-category kappa (unweighted) for completeness
# ---------------------------------------------------------------------------
def multi_category_kappa(observed_table, n_categories):
    """Compute Cohen's kappa for nominal multi-category data.

    observed_table: n_categories × n_categories matrix of counts
    """
    n = sum(sum(row) for row in observed_table)
    p_o = sum(observed_table[i][i] for i in range(n_categories)) / n

    p_e = 0.0
    for k in range(n_categories):
        row_sum = sum(observed_table[k])
        col_sum = sum(observed_table[i][k] for i in range(n_categories))
        p_e += (row_sum / n) * (col_sum / n)

    if p_e == 1.0:
        return 0.0
    return (p_o - p_e) / (1 - p_e)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
print("=" * 64)
print("  Cohen's Kappa Verification — Blind Scoring Reliability Check (n=8)")
print("  Verification date: 2026-07-25")
print("=" * 64)

compute_and_report("Case A: DOCUMENTED DATA (PAPER.md §5.2)", table_documented)
compute_and_report("Case B: HYPOTHETICAL (would give κ ≈ −0.14)", table_hypothetical)

# ---------------------------------------------------------------------------
# Theorem: zero-variance → κ = 0
# ---------------------------------------------------------------------------
print(f"\n{'=' * 64}")
print(f"  THEOREM: Zero-Variance Rater → κ = 0")
print(f"{'=' * 64}")
print(f"  Given: Rater A scores all n items as category k (p_A_k = 1.0)")
print(f"         P_e = Σ p_A_i × p_B_i = 1.0 × p_B_k + 0 = p_B_k")
print(f"         P_o = n × p_B_k / n = p_B_k (A always says k, so agreement")
print(f"                happens exactly when B also says k)")
print(f"         Therefore P_e = P_o → κ = 0")
print(f"  This holds for ANY n, ANY number of categories, ANY agreement rate.")
print(f"  It is a mathematical identity, not an empirical finding.")

# ---------------------------------------------------------------------------
# Diagnosis
# ---------------------------------------------------------------------------
print(f"\n{'=' * 64}")
print(f"  DIAGNOSIS")
print(f"{'=' * 64}")
print(f"  PAPER.md §5.2 states: κ = −0.14")
print(f"  Verified value:      κ = 0.00")
print(f"")
print(f"  Two possible explanations for the discrepancy:")
print(f"  1. COMPUTATIONAL ERROR: κ was miscalculated or estimated")
print(f"     without formal computation. No computational trace exists")
print(f"     in any session transcript or git history.")
print(f"  2. DATA MISMATCH: The data described in PAPER.md differs from")
print(f"     the data used to compute κ = −0.14. (See Case B above)")
print(f"")
print(f"  QUALITATIVE IMPACT: MINIMAL.")
print(f"  Both κ = 0.00 and κ = −0.14 support the SAME interpretation:")
print(f"  the blind check did NOT validate the scoring protocol. Empty")
print(f"  cell (d = 0 both NO) means the task failed to produce balanced")
print(f"  outcomes. The paper's honest framing is correct regardless of")
print(f"  the exact κ value.")
print(f"")
print(f"  RECOMMENDATION: Update PAPER.md §5.2 to use κ = 0.00 (the")
print(f"  verified value) and add a brief note explaining the zero-variance")
print(f"  theorem — this STRENGTHENS the kappa paradox argument: κ = 0")
print(f"  when one rater always says YES is exactly what Cohen's kappa")
print(f"  was designed to reveal.")

print()
