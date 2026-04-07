"""
benchmark_datasets.py
=====================
Three benchmark datasets (small, medium, large) for comparing chase variants.

Why the previous medium dataset hung
--------------------------------------
The original medium schema had a cycle: J -> A, combined with A,F -> ... -> J.
In the 2-row implication chase this terminates fine (row2 converges to row1
in one pass). The hang came from benchmark_implication calling saturation(),
which materialises ALL implied FDs via augmentation. With 10 attributes and a
cycle, augmentation generates exponentially many compound FDs and never
converges within a reasonable time.

Fix applied here
-----------------
1. benchmark_implication now accepts a `skip_saturation` flag. It is set
   automatically when attrs > 5, since saturation is only tractable up to ~5
   attributes in the current implementation.
2. The medium and large datasets avoid cycles in their FD sets. Cycles are
   fine for the chase and closure algorithms, but make augmentation-based
   saturation diverge.
3. The datasets still contain redundant FDs (FDs implied by others) so that
   the restricted chase has real work to skip.

Dataset designs
---------------
Small  (5 attrs,  3 FDs):           AB->C, C->D, D->E. Textbook 3NF chain.
                                     Saturation runs (<=5 attrs).

Medium (10 attrs, 11 FDs, 3 redund): Two chains (A->...->E and AF->...->I)
                                     merging at EI->J. No cycle.
                                     Saturation skipped (>5 attrs).

Large  (14 attrs, 13 FDs, 4 redund): Deep branching chain AB->C->D,E->...->N.
                                     No cycle. Saturation skipped.
"""

import sys
import os
import time
import itertools
from collections import defaultdict

"""
Chase algorithm variants and benchmarking harness.
 
Algorithms implemented:
  - algo1              : attribute closure (fixed-point)
  - chase              : oblivious chase (dependency implication)
  - lossless_chase     : oblivious chase (lossless decomposition)
  - restricted_chase   : restricted chase (dependency implication + lossless)
  - saturation         : saturation / canonical closure (dependency implication)
"""
 
 
# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
 
def _freeze(s):
    """Return a frozenset from any iterable."""
    return frozenset(s)
 
 
# ---------------------------------------------------------------------------
# Existing algorithms (unchanged except minor type annotations)
# ---------------------------------------------------------------------------
 
def algo1(R, FDs):
    """Attribute closure of R under FDs (fixed-point)."""
    res = set(R)
    unused = FDs.copy()
    update = True
    while update:
        update = False
        for lhs, rhs in FDs:
            if (lhs, rhs) not in unused:
                continue
            if lhs <= res:
                unused.remove((lhs, rhs))
                res.update(rhs)
                update = True
    return res
 
 
def lossless_table(attrs, decom):
    res = []
    for i, d in enumerate(decom, start=1):
        row = {attr: "X" if attr in d else f"{attr}{i}" for attr in attrs}
        res.append(row)
    return res
 
 
def lossless_chase(attrs, FD, decom):
    """Oblivious chase for lossless decomposition checking."""
    tbl = lossless_table(sorted(attrs), decom)
    changed = True
    while changed:
        changed = False
        for lhs, rhs in FD:
            for i, row_i in enumerate(tbl):
                for j, row_j in enumerate(tbl):
                    if i >= j:
                        continue
                    if not all(row_i[attr] == row_j[attr] for attr in lhs):
                        continue
                    for attr in rhs:
                        if row_i[attr] == "X" and row_j[attr] != "X":
                            row_j[attr] = "X"
                            changed = True
                        elif row_j[attr] == "X" and row_i[attr] != "X":
                            row_i[attr] = "X"
                            changed = True
        if any(all(v == "X" for v in row.values()) for row in tbl):
            return (True, tbl)
    return (False, tbl)
 
 
def make_table(attrs):
    row1 = {attr: f"a{j+1}" for j, attr in enumerate(attrs)}
    row2 = {attr: f"b{j+1}" for j, attr in enumerate(attrs)}
    return [row1, row2]
 
 
def chase(attrs, FD, c):
    """Oblivious chase for dependency implication checking."""
    tbl = make_table(sorted(attrs))
    l, r = c
    for a in l:
        tbl[1][a] = tbl[0][a]
    changed = True
    while changed:
        changed = False
        for lhs, rhs in FD:
            match = all(tbl[1][atr] == tbl[0][atr] for atr in lhs)
            if match:
                for atr in rhs:
                    if tbl[1][atr] != tbl[0][atr]:
                        tbl[1][atr] = tbl[0][atr]
                        changed = True
    res = all(tbl[0][a] == tbl[1][a] for a in r)
    return res, tbl
 
 
# ---------------------------------------------------------------------------
# Restricted Chase
# ---------------------------------------------------------------------------
 
def _fd_satisfied(row_i, row_j, lhs, rhs):
    """
    Check whether applying FD lhs->rhs to the pair (row_i, row_j) is
    *necessary*, i.e. their LHS values match but at least one RHS value differs.
    Returns True if the FD is not yet satisfied for this pair.
    """
    lhs_match = all(row_i[attr] == row_j[attr] for attr in lhs)
    if not lhs_match:
        return False   # precondition not met — FD doesn't apply
    rhs_match = all(row_i[attr] == row_j[attr] for attr in rhs)
    return not rhs_match   # True means "still needs to be fixed"
 
 
def restricted_chase_lossless(attrs, FD, decom):
    """
    Optimized restricted chase for lossless decomposition.

    Improvements:
    - No pair list creation
    - No function call overhead (_fd_satisfied removed)
    - Early exit on LHS mismatch
    - RHS checked only if needed
    """

    tbl = lossless_table(sorted(attrs), decom)
    n = len(tbl)

    changed = True
    while changed:
        changed = False

        for lhs, rhs in FD:
            for i in range(n):
                row_i = tbl[i]
                for j in range(i + 1, n):
                    row_j = tbl[j]

                    # ---- LHS check (early exit) ----
                    lhs_match = True
                    for attr in lhs:
                        if row_i[attr] != row_j[attr]:
                            lhs_match = False
                            break
                    if not lhs_match:
                        continue

                    # ---- RHS check (only if needed) ----
                    rhs_match = True
                    for attr in rhs:
                        if row_i[attr] != row_j[attr]:
                            rhs_match = False
                            break
                    if rhs_match:
                        continue  # skip (this is the restriction)

                    # ---- Apply update ----
                    for attr in rhs:
                        if row_i[attr] == "X" and row_j[attr] != "X":
                            row_j[attr] = "X"
                            changed = True
                        elif row_j[attr] == "X" and row_i[attr] != "X":
                            row_i[attr] = "X"
                            changed = True

        # ---- Check termination ----
        for row in tbl:
            if all(v == "X" for v in row.values()):
                return True, tbl

    return False, tbl
 
 
def restricted_chase_implication(attrs, FD, c):
    """
    Restricted chase for dependency implication checking.
 
    Difference from oblivious chase:
      Only applies an FD when its LHS matches in the tableau but RHS does not —
      i.e., the FD is not yet locally satisfied.  This is the key restriction
      that gives the algorithm its name.
 
    Returns (implied: bool, table: list[dict])
    """
    tbl = make_table(sorted(attrs))
    l, r = c
    for a in l:
        tbl[1][a] = tbl[0][a]
 
    changed = True
    while changed:
        changed = False
        for lhs, rhs in FD:
            # Restricted: only apply when LHS matches AND RHS not yet equal
            lhs_ok = all(tbl[1][atr] == tbl[0][atr] for atr in lhs)
            rhs_ok = all(tbl[1][atr] == tbl[0][atr] for atr in rhs)
            if lhs_ok and not rhs_ok:   # <-- the restriction
                for atr in rhs:
                    if tbl[1][atr] != tbl[0][atr]:
                        tbl[1][atr] = tbl[0][atr]
                        changed = True
 
    implied = all(tbl[0][a] == tbl[1][a] for a in r)
    return implied, tbl
 
 
# ---------------------------------------------------------------------------
# Saturation Algorithm
# ---------------------------------------------------------------------------
 
def _closure_from_fds(X, FDs):
    """Compute attribute closure of set X under FDs."""
    closure = set(X)
    changed = True
    while changed:
        changed = False
        for lhs, rhs in FDs:
            if lhs <= closure and not rhs <= closure:
                closure |= rhs
                changed = True
    return frozenset(closure)
 
 
def saturation(attrs, FDs):
    """
    Saturation algorithm for computing the canonical / saturated set of FDs.
 
    Strategy:
      Repeatedly derive new FDs implied by the current set using Armstrong's
      axioms (reflexivity, augmentation, transitivity / union) until no new
      FDs can be added.  The result is a saturated set from which membership
      of any FD lhs->rhs can be checked in O(1).
 
    This is equivalent to computing the closure of every subset, but is
    structured as a fixed-point loop over the FD set itself.
 
    Returns frozenset of (frozenset lhs, frozenset rhs) pairs.
    """
    # Normalise to frozensets
    saturated = {(_freeze(lhs), _freeze(rhs)) for lhs, rhs in FDs}
    all_attrs = _freeze(attrs)
 
    changed = True
    while changed:
        changed = False
        new_fds = set()
 
        # Reflexivity: X -> Y whenever Y ⊆ X
        # We only materialise non-trivial ones that are not already present.
 
        # Transitivity / pseudo-transitivity:
        # If X->Y and Y->Z (or Y ⊆ closure(X)) then X->Z
        for lhs, rhs in list(saturated):
            derived_rhs = _closure_from_fds(lhs, list(saturated))
            # Every attribute reachable from lhs forms an FD lhs -> {attr}
            for attr in derived_rhs - lhs:
                candidate = (_freeze(lhs), _freeze({attr}))
                if candidate not in saturated:
                    new_fds.add(candidate)
 
        # Augmentation: X->Y  =>  XZ->YZ  for every Z ⊆ attrs
        # Full augmentation is exponential; we limit to single-attribute
        # augmentations for tractability in benchmarks.
        for lhs, rhs in list(saturated):
            for attr in all_attrs - lhs:
                aug_lhs = lhs | {attr}
                aug_rhs = rhs | {attr}
                candidate = (_freeze(aug_lhs), _freeze(aug_rhs))
                if candidate not in saturated:
                    new_fds.add(candidate)
 
        if new_fds:
            saturated |= new_fds
            changed = True
 
    return frozenset(saturated)
 
 
def saturation_implies(attrs, FDs, query_lhs, query_rhs):
    """
    Use the saturation algorithm to check whether FDs imply lhs -> rhs.
 
    Returns (implied: bool, saturated_fds: frozenset)
    """
    sat = saturation(attrs, FDs)
    ql = _freeze(query_lhs)
    qr = _freeze(query_rhs)
    # lhs->rhs is implied iff qr ⊆ closure(ql) under saturated set
    closure = _closure_from_fds(ql, [(l, r) for l, r in sat])
    implied = qr <= closure
    return implied, sat

# ---------------------------------------------------------------------------
# Timing helper
# ---------------------------------------------------------------------------
def _time_it(fn, runs=100):
    result = None
    total = 0.0
    for _ in range(runs):
        t0 = time.perf_counter()
        result = fn()
        total += time.perf_counter() - t0
    return result, total / runs


# ---------------------------------------------------------------------------
# Benchmark functions
# ---------------------------------------------------------------------------
def benchmark_implication(attrs, FDs, query_lhs, query_rhs,
                           expected=None, runs=100, dataset="?",
                           skip_saturation=None):
    """
    Time all dependency-implication algorithms on one query.

    Parameters
    ----------
    attrs            : iterable of attribute names
    FDs              : list of (frozenset lhs, frozenset rhs)
    query_lhs/rhs    : iterables
    expected         : optional bool — asserts all results match
    runs             : timing repetitions
    dataset          : label for error messages
    skip_saturation  : auto-True when len(attrs) > 5

    Returns dict  algo_name -> {"result": bool, "avg_s": float, "skipped": bool}
    """
    attrs = sorted(attrs)
    ql = frozenset(query_lhs)
    qr = frozenset(query_rhs)
    if skip_saturation is None:
        skip_saturation = len(attrs) > 5

    results = {}

    # algo1 (attribute closure)
    _, t = _time_it(lambda: algo1(ql, FDs), runs=runs)
    res = qr <= algo1(ql, FDs)
    results["algo1"] = {"result": res, "avg_s": t, "skipped": False}

    # oblivious chase
    _, t = _time_it(lambda: chase(attrs, FDs, (ql, qr)), runs=runs)
    res, _ = chase(attrs, FDs, (ql, qr))
    results["chase (oblivious)"] = {"result": res, "avg_s": t, "skipped": False}

    # restricted chase
    _, t = _time_it(
        lambda: restricted_chase_implication(attrs, FDs, (ql, qr)), runs=runs
    )
    res, _ = restricted_chase_implication(attrs, FDs, (ql, qr))
    results["chase (restricted)"] = {"result": res, "avg_s": t, "skipped": False}

    # saturation
    if skip_saturation:
        results["saturation"] = {
            "result": None, "avg_s": None, "skipped": True,
            "note": f"skipped: {len(attrs)} attrs > 5 (augmentation explodes)",
        }
    else:
        _, t = _time_it(lambda: saturation_implies(attrs, FDs, ql, qr), runs=runs)
        res, _ = saturation_implies(attrs, FDs, ql, qr)
        results["saturation"] = {"result": res, "avg_s": t, "skipped": False}

    if expected is not None:
        for name, data in results.items():
            if not data["skipped"] and data["result"] != expected:
                raise AssertionError(
                    f"[{dataset}] {name}: expected {expected}, got {data['result']}"
                )

    return results


def benchmark_lossless(attrs, FDs, decom, expected=None, runs=100, dataset="?"):
    """
    Time lossless-decomposition algorithms.

    Returns dict  algo_name -> {"result": bool, "avg_s": float}
    """
    attrs = sorted(attrs)
    results = {}

    _, t = _time_it(lambda: lossless_chase(attrs, FDs, decom), runs=runs)
    res, _ = lossless_chase(attrs, FDs, decom)
    results["lossless_chase (oblivious)"] = {"result": res, "avg_s": t}

    _, t = _time_it(
        lambda: restricted_chase_lossless(attrs, FDs, decom), runs=runs
    )
    res, _ = restricted_chase_lossless(attrs, FDs, decom)
    results["lossless_chase (restricted)"] = {"result": res, "avg_s": t}

    if expected is not None:
        for name, data in results.items():
            if data["result"] != expected:
                raise AssertionError(
                    f"[{dataset}] {name}: expected {expected}, got {data['result']}"
                )

    return results


def print_benchmark(title, results):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    width = max(len(k) for k in results)
    for algo, data in results.items():
        label = algo.ljust(width)
        if data.get("skipped"):
            print(f"  {label}  SKIPPED  ({data.get('note', '')})")
        else:
            result = "YES" if data["result"] else "NO "
            us = data["avg_s"] * 1_000_000
            print(f"  {label}  result={result}  time={us:8.2f} µs")
    print()


# ===========================================================================
# DATASET DEFINITIONS
# ===========================================================================

# ---------------------------------------------------------------------------
# Small: R(A, B, C, D, E) — 5 attrs, 3 FDs, no redundancy, no cycle
#
# FDs:   AB -> C,  C -> D,  D -> E
# Decomp: {ABC}, {CD}, {DE}     — lossless (C is key of {CD})
# Queries: AB -> E (YES), B -> E (NO)
# Saturation: runs (only 5 attrs)
# ---------------------------------------------------------------------------
SMALL_ATTRS  = list("ABCDE")
SMALL_FDS    = [
    (frozenset({"A", "B"}), frozenset({"C"})),
    (frozenset({"C"}),       frozenset({"D"})),
    (frozenset({"D"}),       frozenset({"E"})),
]
SMALL_DECOM   = [{"A", "B", "C"}, {"C", "D"}, {"D", "E"}]
SMALL_QUERY   = (frozenset({"A", "B"}), frozenset({"E"}))   # YES
SMALL_QUERY_N = (frozenset({"B"}),      frozenset({"E"}))   # NO

# ---------------------------------------------------------------------------
# Medium: R(A, B, C, D, E, F, G, H, I, J) — 10 attrs, 11 FDs, NO cycle
#
# Two convergent chains that merge:
#   Chain 1:  A -> B -> C -> D -> E
#   Chain 2:  A,F -> G -> H -> I
#   Merge:    E,I -> J
#
# Redundant FDs (explicitly stated, implied by chains):
#   A  -> C   (implied by A->B->C)
#   B  -> D   (implied by B->C->D)
#   G  -> I   (implied by G->H->I)
#
# These give the oblivious chase extra FDs to re-check after convergence,
# while the restricted chase skips them once satisfied.
#
# Decomp: {ABCDE}, {AFGHI}, {EIJ}  — lossless
#         Joining on E (from chain1) and I (from chain2) is enough to
#         reconstruct J via EI->J.
# Queries: AF -> J (YES), F -> J (NO)
# Saturation: SKIPPED (10 attrs — augmentation generates ~10^4+ FDs)
# ---------------------------------------------------------------------------
MEDIUM_ATTRS = list("ABCDEFGHIJ")
MEDIUM_FDS   = [
    # Chain 1
    (frozenset({"A"}),       frozenset({"B"})),
    (frozenset({"B"}),       frozenset({"C"})),
    (frozenset({"C"}),       frozenset({"D"})),
    (frozenset({"D"}),       frozenset({"E"})),
    # Chain 2
    (frozenset({"A", "F"}), frozenset({"G"})),
    (frozenset({"G"}),       frozenset({"H"})),
    (frozenset({"H"}),       frozenset({"I"})),
    # Merge point
    (frozenset({"E", "I"}), frozenset({"J"})),
    # Redundant FDs (implied, but stated — extra oblivious work)
    (frozenset({"A"}),       frozenset({"C"})),   # implied by A->B->C
    (frozenset({"B"}),       frozenset({"D"})),   # implied by B->C->D
    (frozenset({"G"}),       frozenset({"I"})),   # implied by G->H->I
]
MEDIUM_DECOM   = [{"A","B","C","D","E"}, {"A","F","G","H","I"}, {"E","I","J"}]
MEDIUM_QUERY   = (frozenset({"A", "F"}), frozenset({"J"}))   # YES
MEDIUM_QUERY_N = (frozenset({"F"}),      frozenset({"J"}))   # NO

# ---------------------------------------------------------------------------
# Large: R(A..N) — 14 attrs, 13 FDs (4 redundant), NO cycle
#
# Deep branching chain:
#   A,B -> C
#   C   -> D, E
#   D   -> F
#   E   -> G
#   F,G -> H, I
#   H   -> J, K
#   I   -> L
#   J   -> M
#   K,L -> N
#
# Redundant FDs (implied):
#   A,B -> D    (via AB->C->D)
#   C,D -> F    (via D->F)
#   H,I -> J    (via H->JK)
#   C   -> F    (via C->D->F)
#
# Decomp: 10-way BCNF split, with one extra overlapping relation {HIJ}
#         to create more redundant pair-checks in the lossless tableau.
# Queries: AB -> N (YES), A -> N (NO)
# Saturation: SKIPPED (14 attrs)
# ---------------------------------------------------------------------------
_L = list("ABCDEFGHIJKLMN")
LARGE_ATTRS = _L
LARGE_FDS   = [
    # Core chain
    (frozenset({"A", "B"}),    frozenset({"C"})),
    (frozenset({"C"}),          frozenset({"D", "E"})),
    (frozenset({"D"}),          frozenset({"F"})),
    (frozenset({"E"}),          frozenset({"G"})),
    (frozenset({"F", "G"}),    frozenset({"H", "I"})),
    (frozenset({"H"}),          frozenset({"J", "K"})),
    (frozenset({"I"}),          frozenset({"L"})),
    (frozenset({"J"}),          frozenset({"M"})),
    (frozenset({"K", "L"}),    frozenset({"N"})),
    # Redundant FDs
    (frozenset({"A", "B"}),    frozenset({"D"})),   # implied by AB->C->D
    (frozenset({"C", "D"}),    frozenset({"F"})),   # implied by D->F
    (frozenset({"H", "I"}),    frozenset({"J"})),   # implied by H->JK
    (frozenset({"C"}),          frozenset({"F"})),   # implied by C->D->F
]
LARGE_DECOM = [
    {"A", "B", "C"},
    {"C", "D", "E"},
    {"D", "F"},
    {"E", "G"},
    {"F", "G", "H", "I"},
    {"H", "J", "K"},
    {"I", "L"},
    {"J", "M"},
    {"K", "L", "N"},
    {"H", "I", "J"},    # overlapping — more redundant pair-checks
]
LARGE_QUERY   = (frozenset({"A", "B"}), frozenset({"N"}))   # YES
LARGE_QUERY_N = (frozenset({"A"}),      frozenset({"N"}))   # NO


# ===========================================================================
# Runner
# ===========================================================================
if __name__ == "__main__":
    RUNS = 100

    # ---- Small ----
    print("\n" + "#" * 60)
    print("  SMALL  (5 attrs · 3 FDs · 3-way decomposition)")
    print("#" * 60)

    print("\n--- Implication: AB -> E (should be YES) ---")
    r = benchmark_implication(
        SMALL_ATTRS, SMALL_FDS, *SMALL_QUERY,
        expected=True, runs=RUNS, dataset="small"
    )
    print_benchmark("Implication: AB -> E", r)

    print("--- Implication: B -> E (should be NO) ---")
    r = benchmark_implication(
        SMALL_ATTRS, SMALL_FDS, *SMALL_QUERY_N,
        expected=False, runs=RUNS, dataset="small"
    )
    print_benchmark("Implication: B -> E", r)

    print("--- Lossless: {ABC, CD, DE} (should be YES) ---")
    r = benchmark_lossless(
        SMALL_ATTRS, SMALL_FDS, SMALL_DECOM,
        expected=True, runs=RUNS, dataset="small"
    )
    print_benchmark("Lossless: {ABC, CD, DE}", r)

    print("--- Lossless: {AB, CDE} (should be NO) ---")
    r = benchmark_lossless(
        SMALL_ATTRS, SMALL_FDS, [{"A","B"}, {"C","D","E"}],
        expected=False, runs=RUNS, dataset="small"
    )
    print_benchmark("Lossless: {AB, CDE}", r)

    # ---- Medium ----
    print("\n" + "#" * 60)
    print("  MEDIUM  (10 attrs · 11 FDs · 3 redundant · no cycle)")
    print("#" * 60)

    print("\n--- Implication: AF -> J (should be YES) ---")
    r = benchmark_implication(
        MEDIUM_ATTRS, MEDIUM_FDS, *MEDIUM_QUERY,
        expected=True, runs=RUNS, dataset="medium"
    )
    print_benchmark("Implication: AF -> J", r)

    print("--- Implication: F -> J (should be NO) ---")
    r = benchmark_implication(
        MEDIUM_ATTRS, MEDIUM_FDS, *MEDIUM_QUERY_N,
        expected=False, runs=RUNS, dataset="medium"
    )
    print_benchmark("Implication: F -> J", r)

    print("--- Lossless: {ABCDE, AFGHI, EIJ} (should be YES) ---")
    r = benchmark_lossless(
        MEDIUM_ATTRS, MEDIUM_FDS, MEDIUM_DECOM,
        expected=True, runs=RUNS, dataset="medium"
    )
    print_benchmark("Lossless: {ABCDE, AFGHI, EIJ}", r)

    print("--- Lossless: {ABCDE, FGHIJ} (should be NO) ---")
    r = benchmark_lossless(
        MEDIUM_ATTRS, MEDIUM_FDS,
        [{"A","B","C","D","E"}, {"F","G","H","I","J"}],
        expected=False, runs=RUNS, dataset="medium"
    )
    print_benchmark("Lossless: {ABCDE, FGHIJ}", r)

    # ---- Large ----
    print("\n" + "#" * 60)
    print("  LARGE  (14 attrs · 13 FDs · 4 redundant · no cycle)")
    print("#" * 60)

    print("\n--- Implication: AB -> N (should be YES) ---")
    r = benchmark_implication(
        LARGE_ATTRS, LARGE_FDS, *LARGE_QUERY,
        expected=True, runs=RUNS, dataset="large"
    )
    print_benchmark("Implication: AB -> N", r)

    print("--- Implication: A -> N (should be NO) ---")
    r = benchmark_implication(
        LARGE_ATTRS, LARGE_FDS, *LARGE_QUERY_N,
        expected=False, runs=RUNS, dataset="large"
    )
    print_benchmark("Implication: A -> N", r)

    print("--- Lossless: 10-way BCNF decomposition (should be YES) ---")
    r = benchmark_lossless(
        LARGE_ATTRS, LARGE_FDS, LARGE_DECOM,
        expected=True, runs=RUNS, dataset="large"
    )
    print_benchmark("Lossless: 10-way decomp", r)

    print("--- Lossless: bad split {ABCDE, FGHIJN} (should be NO) ---")
    r = benchmark_lossless(
        LARGE_ATTRS, LARGE_FDS,
        [{"A","B","C","D","E"}, {"F","G","H","I","J","N"}],
        expected=False, runs=RUNS, dataset="large"
    )
    print_benchmark("Lossless: bad split", r)

    # ---------------------------------------------------------------------------
    # Stress Test: Designed to FAVOR restricted chase
    # ---------------------------------------------------------------------------

    STRESS_ATTRS = list("ABCDEFGHIJKLMNO")  # 15 attrs

    STRESS_FDS = [
        # Core cycle (forces repeated checking)
        (frozenset({"A"}), frozenset({"B"})),
        (frozenset({"B"}), frozenset({"C"})),
        (frozenset({"C"}), frozenset({"A"})),  # cycle!

        # Long propagation chain
        (frozenset({"A"}), frozenset({"D"})),
        (frozenset({"D"}), frozenset({"E"})),
        (frozenset({"E"}), frozenset({"F"})),
        (frozenset({"F"}), frozenset({"G"})),
        (frozenset({"G"}), frozenset({"H"})),
        (frozenset({"H"}), frozenset({"I"})),
        (frozenset({"I"}), frozenset({"J"})),
        (frozenset({"J"}), frozenset({"K"})),
        (frozenset({"K"}), frozenset({"L"})),
        (frozenset({"L"}), frozenset({"M"})),
        (frozenset({"M"}), frozenset({"N"})),
        (frozenset({"N"}), frozenset({"O"})),

        # HEAVY redundancy (these kill oblivious)
        (frozenset({"A"}), frozenset({"C"})),
        (frozenset({"B"}), frozenset({"A"})),
        (frozenset({"C"}), frozenset({"B"})),
        (frozenset({"A"}), frozenset({"E"})),
        (frozenset({"A"}), frozenset({"F"})),
        (frozenset({"A"}), frozenset({"G"})),
        (frozenset({"A"}), frozenset({"H"})),
        (frozenset({"A"}), frozenset({"I"})),
        (frozenset({"A"}), frozenset({"J"})),
        (frozenset({"A"}), frozenset({"K"})),
    ]

    # BIG decomposition → many row pairs
    STRESS_DECOM = [
        {"A","B","C"},
        {"A","D","E"},
        {"E","F","G"},
        {"G","H","I"},
        {"I","J","K"},
        {"K","L","M"},
        {"M","N","O"},
        {"A","E","I"},
        {"C","G","K"},
        {"B","F","J"},
        {"D","H","L"},
        {"E","I","M"},
        {"F","J","N"},
        {"G","K","O"},
    ]

    STRESS_QUERY = (frozenset({"A"}), frozenset({"O"}))  # YES

    print("\n" + "#" * 60)
    print("  STRESS TEST (designed to favor restricted chase)")
    print("#" * 60)

    print("\n--- Implication: A -> O (should be YES) ---")
    r = benchmark_implication(
        STRESS_ATTRS, STRESS_FDS, *STRESS_QUERY,
        expected=True, runs=RUNS, dataset="stress"
    )
    print_benchmark("Implication: A -> O", r)

    print("--- Lossless: large decomposition (should be YES) ---")
    r = benchmark_lossless(
        STRESS_ATTRS, STRESS_FDS, STRESS_DECOM,
        expected=True, runs=RUNS, dataset="stress"
    )
    print_benchmark("Lossless: stress decomp", r)