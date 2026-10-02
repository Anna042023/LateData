#!/usr/bin/env python3
"""Reference implementation of the uniform-charge single-query certified planner.

This is a compact manuscript-facing implementation of the rule in R11.114.
It is not represented as the original experimental driver.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import floor
from typing import Iterable, Sequence

@dataclass(frozen=True)
class Plan:
    read_indices: tuple[int, ...]
    read_tail: bool
    cost: float
    certified_omitted_charge: float


def _tail_conditioned_plan(
    byte_costs: Sequence[float],
    lambda_charge: float,
    epsilon: float,
    tail_certificate: float,
    tail_cost: float,
    read_tail: bool,
) -> Plan | None:
    if lambda_charge <= 0:
        raise ValueError("lambda_charge must be positive")
    if epsilon < 0 or tail_certificate < 0 or tail_cost < 0:
        raise ValueError("budgets/certificates/costs must be nonnegative")
    if any(c < 0 for c in byte_costs):
        raise ValueError("byte costs must be nonnegative")

    residual_budget = epsilon - (0.0 if read_tail else tail_certificate)
    if residual_budget < 0:
        return None

    n = len(byte_costs)
    max_unread = floor(residual_budget / lambda_charge)
    k = max(0, n - max_unread)
    ranked = sorted(range(n), key=lambda i: (byte_costs[i], i))
    chosen = tuple(sorted(ranked[:k]))
    chosen_cost = sum(byte_costs[i] for i in chosen) + (tail_cost if read_tail else 0.0)
    omitted = (n - k) * lambda_charge + (0.0 if read_tail else tail_certificate)
    return Plan(chosen, read_tail, chosen_cost, omitted)


def plan_uniform_charge(
    byte_costs: Iterable[float],
    lambda_charge: float,
    epsilon: float,
    tail_certificate: float = 0.0,
    tail_cost: float = 0.0,
) -> Plan:
    """Return the minimum-byte plan over the two residual-tail states."""
    costs = tuple(float(x) for x in byte_costs)
    candidates = [
        p for p in (
            _tail_conditioned_plan(costs, lambda_charge, epsilon, tail_certificate, tail_cost, False),
            _tail_conditioned_plan(costs, lambda_charge, epsilon, tail_certificate, tail_cost, True),
        ) if p is not None
    ]
    if not candidates:
        raise ValueError("no feasible certified plan")
    return min(candidates, key=lambda p: (p.cost, p.read_tail, p.read_indices))


def _self_test() -> None:
    p = plan_uniform_charge([9, 2, 5, 1], lambda_charge=3, epsilon=6)
    assert p.read_indices == (1, 3), p
    assert p.certified_omitted_charge <= 6

    q = plan_uniform_charge([9, 2, 5, 1], lambda_charge=3, epsilon=4,
                            tail_certificate=2, tail_cost=0.25)
    assert q.certified_omitted_charge <= 4
    print("balanced_cert_reference: PASS")

if __name__ == "__main__":
    _self_test()
