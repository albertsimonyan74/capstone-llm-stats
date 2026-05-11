# baseline/bayesian/markov_chains.py
"""
Markov chain computations for Lectures 30–33.

Covers: transition matrix validation, n-step probabilities,
Chapman-Kolmogorov, accessibility, communication classes,
recurrence/transience, stationary distribution, ergodicity,
two-state closed-form solution, and gambler's ruin.
"""
from __future__ import annotations

from typing import Any, Dict, List, Set

import numpy as np


# ── helpers ───────────────────────────────────────────────────────────────────

def _check_square(P: np.ndarray, name: str = "P") -> int:
    if P.ndim != 2 or P.shape[0] != P.shape[1]:
        raise ValueError(f"{name} must be a square 2-D array, got shape {P.shape}")
    return P.shape[0]


# ── Concept 1 — Transition matrix validation ─────────────────────────────────

def is_valid_transition_matrix(P: np.ndarray) -> Dict[str, Any]:
    """
    Check that P is a valid stochastic (transition) matrix.

    Conditions:
      1. Square 2-D array.
      2. All entries >= 0.
      3. Each row sums to 1 (within tol=1e-10).

    Args:
        P: Candidate transition matrix.

    Returns:
        dict with "valid" (bool) and "errors" (list of problem descriptions).
    """
    errors: List[str] = []
    try:
        n = _check_square(P, "P")
    except ValueError as e:
        return {"valid": False, "errors": [str(e)]}

    if np.any(P < 0):
        errors.append(f"Negative entries found: min={P.min():.6g}")

    row_sums = P.sum(axis=1)
    bad_rows = np.where(np.abs(row_sums - 1.0) > 1e-10)[0]
    if len(bad_rows) > 0:
        errors.append(
            f"Rows not summing to 1 (tol=1e-10): rows {bad_rows.tolist()}, "
            f"sums={row_sums[bad_rows].tolist()}"
        )

    return {"valid": len(errors) == 0, "errors": errors}


# ── Concept 2 — n-step transition probabilities ───────────────────────────────

def n_step_transition(P: np.ndarray, n: int) -> np.ndarray:
    """
    Compute the n-step transition matrix P^n.

    By the Chapman-Kolmogorov equations, the (i,j)-entry of P^n gives
    the probability of moving from state i to state j in exactly n steps.

    Args:
        P: Valid transition matrix.
        n: Number of steps. Must be >= 0.

    Returns:
        P^n as a numpy array.
    """
    _check_square(P, "P")
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n}")
    return np.linalg.matrix_power(P, n)


# ── Concept 3 — Chapman-Kolmogorov verification ───────────────────────────────

def chapman_kolmogorov_check(
    P: np.ndarray,
    r: int,
    n: int,
) -> Dict[str, Any]:
    """
    Verify the Chapman-Kolmogorov equation: P^n = P^r @ P^(n-r).

    The Chapman-Kolmogorov equations state that for any 0 <= r <= n:
      p_{ij}^(n) = sum_k p_{ik}^(r) * p_{kj}^(n-r)
    i.e. P^n = P^r * P^(n-r).

    Args:
        P: Transition matrix.
        r: Intermediate step count. Must satisfy 0 <= r <= n.
        n: Total steps. Must be >= r.

    Returns:
        dict with "verified" (bool) and "max_diff" (float).
    """
    if not (0 <= r <= n):
        raise ValueError(f"Must have 0 <= r <= n, got r={r}, n={n}")
    Pn = n_step_transition(P, n)
    Pr_Pnr = n_step_transition(P, r) @ n_step_transition(P, n - r)
    max_diff = float(np.max(np.abs(Pn - Pr_Pnr)))
    return {"verified": max_diff < 1e-10, "max_diff": max_diff}


# ── Concept 4 — State accessibility ──────────────────────────────────────────

def is_accessible(
    P: np.ndarray,
    i: int,
    j: int,
    max_steps: int = 100,
) -> bool:
    """
    Check whether state j is accessible from state i (i -> j).

    State j is accessible from i if P^n[i, j] > 0 for some n >= 1.
    Checked iteratively up to max_steps.

    Args:
        P:         Transition matrix.
        i:         Starting state (0-indexed).
        j:         Target state (0-indexed).
        max_steps: Maximum number of steps to check.

    Returns:
        True if j is reachable from i within max_steps steps.
    """
    n = _check_square(P, "P")
    if not (0 <= i < n and 0 <= j < n):
        raise ValueError(f"States i={i}, j={j} out of range [0, {n-1}]")
    Pk = P.copy()
    for _ in range(max_steps):
        if Pk[i, j] > 0:
            return True
        Pk = Pk @ P
    return False


# ── Concept 5 — Communication classes ────────────────────────────────────────

def communication_classes(P: np.ndarray) -> Dict[str, Any]:
    """
    Find all communication classes of the Markov chain.

    States i and j communicate (i <-> j) if i -> j AND j -> i.
    Communication is an equivalence relation; its equivalence classes
    partition the state space.

    Args:
        P: Transition matrix.

    Returns:
        dict with:
          "classes"       – list of sets of communicating states
          "is_irreducible" – True if there is exactly one class (all states communicate)
    """
    n = _check_square(P, "P")

    # Build accessibility matrix (reachable[i, j] = True if i -> j in <= n steps)
    reachable = np.zeros((n, n), dtype=bool)
    Pk = P.copy()
    for _ in range(n):
        reachable |= (Pk > 0)
        Pk = Pk @ P

    # i and j communicate iff reachable[i,j] and reachable[j,i]
    communicate = reachable & reachable.T
    # Also: every state communicates with itself (reflexive)
    np.fill_diagonal(communicate, True)

    # Union-Find to extract classes
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> None:
        parent[find(x)] = find(y)

    for i in range(n):
        for j in range(i + 1, n):
            if communicate[i, j]:
                union(i, j)

    classes_dict: Dict[int, Set[int]] = {}
    for i in range(n):
        root = find(i)
        classes_dict.setdefault(root, set()).add(i)

    classes = list(classes_dict.values())
    return {
        "classes": classes,
        "is_irreducible": len(classes) == 1,
    }


# ── Concept 6 — Recurrence vs transience classification ──────────────────────

def classify_states(P: np.ndarray) -> Dict[str, Any]:
    """
    Classify each state as recurrent or transient.

    A communication class C is closed if P[i, j] = 0 for all i in C,
    j not in C (the chain cannot leave C). States in a closed class are
    recurrent; all other states are transient.

    Lecture 32: a finite Markov chain always has at least one recurrent state.
    Transient states are those from which the chain can escape to a closed class.

    Args:
        P: Transition matrix.

    Returns:
        dict with:
          "states"    – {state_index: "recurrent"|"transient"}
          "recurrent" – sorted list of recurrent state indices
          "transient" – sorted list of transient state indices
    """
    n = _check_square(P, "P")
    result = communication_classes(P)
    classes = result["classes"]

    all_states = set(range(n))
    recurrent_states: Set[int] = set()

    for cls in classes:
        # Check if class is closed: no probability mass leaves cls
        is_closed = all(
            abs(sum(P[i, j] for j in all_states - cls)) < 1e-10
            for i in cls
        )
        if is_closed:
            recurrent_states.update(cls)

    transient_states = all_states - recurrent_states
    state_labels = {
        i: ("recurrent" if i in recurrent_states else "transient")
        for i in range(n)
    }
    return {
        "states": state_labels,
        "recurrent": sorted(recurrent_states),
        "transient": sorted(transient_states),
    }


# ── Concept 7 — Stationary distribution ──────────────────────────────────────

def stationary_distribution(
    P: np.ndarray,
    tol: float = 1e-10,
) -> np.ndarray:
    """
    Compute the stationary distribution pi of an irreducible Markov chain.

    Solves pi @ P = pi subject to sum(pi) = 1. Uses the left eigenvector
    of P corresponding to eigenvalue 1 (guaranteed to exist for stochastic P).

    Lecture 33 Theorem: for an ergodic (irreducible, aperiodic) chain,
    pi is unique and P^n[i,j] -> pi[j] as n -> infinity regardless of
    starting state i.

    Args:
        P:   Transition matrix (should be irreducible for unique stationary dist.).
        tol: Tolerance for zero-checking eigenvalues.

    Returns:
        1-D array pi with pi[j] = stationary probability of state j.
    """
    _check_square(P, "P")
    # Solve (P^T - I) pi^T = 0 with constraint sum = 1
    # Use left eigenvectors: eigenvalues of P^T, eigenvectors are columns
    eigenvalues, eigenvectors = np.linalg.eig(P.T)
    # Find eigenvector for eigenvalue closest to 1
    idx = np.argmin(np.abs(eigenvalues - 1.0))
    pi = np.real(eigenvectors[:, idx])
    # Normalise to sum to 1
    pi = pi / pi.sum()
    # Ensure non-negative (flip sign if all negative)
    if np.any(pi < -tol):
        pi = -pi
    return pi


# ── Concept 8 — Ergodicity check ─────────────────────────────────────────────

def is_ergodic(
    P: np.ndarray,
    max_power: int = 100,
) -> bool:
    """
    Check whether the Markov chain is ergodic (irreducible and aperiodic).

    Sufficient condition used here: the chain is ergodic if some power P^n
    (n = 1 to max_power) has all strictly positive entries. This guarantees
    that every state is reachable from every other state in exactly n steps,
    implying both irreducibility and aperiodicity.

    Lecture 33 eq 23.1: a chain satisfying this condition converges to a
    unique stationary distribution from any initial state.

    Args:
        P:         Transition matrix.
        max_power: Maximum power to check.

    Returns:
        True if P^n has all positive entries for some n in 1..max_power.
    """
    _check_square(P, "P")
    Pk = P.copy()
    for _ in range(max_power):
        if np.all(Pk > 0):
            return True
        Pk = Pk @ P
    return False


# ── Concept 9 — Two-state chain closed-form solution ─────────────────────────

def two_state_chain(
    p12: float,
    p21: float,
    n: int,
) -> Dict[str, Any]:
    """
    Closed-form n-step transition matrix for a two-state Markov chain.

    Transition matrix: P = [[1-p12, p12], [p21, 1-p21]]

    Closed form (Lecture 31 eq 21.9), letting lambda = 1 - p12 - p21:
      P^n[0,0] = p21/(p12+p21) + p12/(p12+p21) * lambda^n
      P^n[0,1] = p12/(p12+p21) - p12/(p12+p21) * lambda^n
      P^n[1,0] = p21/(p12+p21) - p21/(p12+p21) * lambda^n
      P^n[1,1] = p12/(p12+p21) + p21/(p12+p21) * lambda^n  [wait — corrected below]

    Stationary: pi = [p21/(p12+p21),  p12/(p12+p21)]

    Periodic: chain is periodic (period 2) iff p12 + p21 = 2, i.e.
    p12 = p21 = 1 (|lambda| = 1 and lambda = -1).

    Args:
        p12: Probability of going from state 0 to state 1.
        p21: Probability of going from state 1 to state 0.
        n:   Number of steps.

    Returns:
        dict with P_n (2x2 ndarray), stationary (1-D array length 2),
        is_periodic (bool: True iff p12=p21=1).
    """
    if not (0 <= p12 <= 1 and 0 <= p21 <= 1):
        raise ValueError(f"p12 and p21 must be in [0,1], got {p12}, {p21}")
    if p12 + p21 == 0:
        raise ValueError("p12 + p21 must be > 0 (otherwise no movement possible)")
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n}")

    s = p12 + p21
    lam = 1.0 - s  # eigenvalue lambda = 1 - p12 - p21
    lam_n = lam ** n

    pi0 = p21 / s  # stationary prob of state 0
    pi1 = p12 / s  # stationary prob of state 1

    # Closed-form P^n entries
    P_n = np.array([
        [pi0 + pi1 * lam_n,  pi1 - pi1 * lam_n],
        [pi0 - pi0 * lam_n,  pi1 + pi0 * lam_n],
    ])

    is_periodic = abs(p12 - 1.0) < 1e-12 and abs(p21 - 1.0) < 1e-12

    return {
        "P_n": P_n,
        "stationary": np.array([pi0, pi1]),
        "is_periodic": is_periodic,
    }


# ── Concept 10 — Gambler's ruin probability ───────────────────────────────────

def gambling_ruin_probability(
    p: float,
    i: int,
    M: int,
) -> Dict[str, Any]:
    """
    Classic gambler's ruin probability for a random walk on {0, 1, ..., M}.

    At each step the gambler wins £1 with probability p or loses £1 with
    probability q = 1-p. The game ends when fortune reaches 0 (ruin) or M
    (win). Starting from fortune i:

    If p != 0.5:
      P(ruin | start=i) = [(q/p)^i - (q/p)^M] / [1 - (q/p)^M]
                        = [1 - (p/q)^i] / [1 - (p/q)^M]   (equivalent form)

    If p = 0.5 (fair game):
      P(ruin | start=i) = (M - i) / M

    Boundary: i=0 → certain ruin (prob=1); i=M → certain win (prob=0).

    Lecture 32 Example 22.2.

    Args:
        p: Probability of winning each bet. Must be in (0, 1).
        i: Starting fortune. Must satisfy 0 <= i <= M.
        M: Target fortune (absorbing win state). Must be > 0.

    Returns:
        dict with ruin_prob, win_prob, starting_fortune (i), target (M).
    """
    if not (0 < p < 1):
        raise ValueError(f"p must be in (0, 1), got {p}")
    if M <= 0:
        raise ValueError(f"M must be > 0, got {M}")
    if not (0 <= i <= M):
        raise ValueError(f"i must be in [0, M], got i={i}, M={M}")

    # Boundary cases
    if i == 0:
        ruin_prob = 1.0
    elif i == M:
        ruin_prob = 0.0
    elif abs(p - 0.5) < 1e-12:
        # Fair game
        ruin_prob = float(M - i) / M
    else:
        q = 1.0 - p
        ratio = q / p  # (q/p)
        ruin_prob = (ratio ** i - ratio ** M) / (1.0 - ratio ** M)

    return {
        "ruin_prob": float(ruin_prob),
        "win_prob": float(1.0 - ruin_prob),
        "starting_fortune": i,
        "target": M,
    }
