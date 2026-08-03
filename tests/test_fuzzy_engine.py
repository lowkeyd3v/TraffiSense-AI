import os
import sys

import pytest

# backend/ has no __init__.py, so add it to sys.path to import directly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fuzzy_engine import (  # noqa: E402
    compute_resources,
    compute_severity_score,
    score_to_level,
    _rule_table,
)


# ── compute_severity_score ───────────────────────────────────────────────────

def test_severity_score_is_bounded():
    for kw in (True, False):
        for closure in (True, False):
            score = compute_severity_score(kw, "accident", "heavy_vehicle", closure)
            assert 0.0 <= score <= 10.0


def test_severity_score_higher_risk_cause_scores_higher():
    low = compute_severity_score(False, "pot_holes", "auto", False)
    high = compute_severity_score(False, "accident", "auto", False)
    assert high > low


def test_severity_score_heavier_vehicle_scores_higher():
    low = compute_severity_score(False, "congestion", "auto", False)
    high = compute_severity_score(False, "congestion", "heavy_vehicle", False)
    assert high > low


def test_severity_score_keyword_and_closure_increase_score():
    base = compute_severity_score(False, "congestion", "private_car", False)
    with_keyword = compute_severity_score(True, "congestion", "private_car", False)
    with_closure = compute_severity_score(False, "congestion", "private_car", True)
    with_both = compute_severity_score(True, "congestion", "private_car", True)

    assert with_keyword > base
    assert with_closure > base
    assert with_both > with_keyword
    assert with_both > with_closure


def test_severity_score_unknown_cause_and_vehicle_use_defaults():
    # Should not raise, and should fall back to the documented defaults
    # rather than crash on an unrecognized category.
    score = compute_severity_score(False, "not_a_real_cause", "not_a_real_vehicle", False)
    assert 0.0 <= score <= 10.0


# ── Rule table (FAM) ──────────────────────────────────────────────────────

def test_rule_table_covers_every_combination_exactly_once():
    table = list(_rule_table())
    keys = [(d, p, s, c) for d, p, s, c, *_ in table]
    assert len(table) == 81
    assert len(set(keys)) == 81  # no duplicate antecedent combinations


def test_rule_table_output_levels_in_range():
    for d, p, s, c, per, bar, res, resp in _rule_table():
        assert d in (0, 1, 2) and p in (0, 1, 2) and s in (0, 1, 2) and c in (0, 1, 2)
        assert per in (0, 1, 2)
        assert bar in (0, 1, 2)
        assert res in (0, 1, 2, 3)
        assert resp in (0, 1, 2, 3)


def test_rule_table_monotonic_in_each_antecedent():
    """Increasing any single antecedent, holding the others fixed, should
    never *decrease* any output level (personnel/barricades/resource/
    response). This is the core sanity property of the FAM table.
    """
    table = list(_rule_table())
    for axis in range(4):  # 0=duration,1=priority,2=severity,3=crowd
        grouped = {}
        for row in table:
            key = tuple(v for i, v in enumerate(row[:4]) if i != axis)
            grouped.setdefault(key, []).append((row[axis], row[4], row[5], row[6], row[7]))
        for key, vals in grouped.items():
            vals.sort()
            for i in range(1, len(vals)):
                prev, cur = vals[i - 1], vals[i]
                assert cur[1] >= prev[1], f"personnel regressed on axis {axis}: {key}"
                assert cur[2] >= prev[2], f"barricades regressed on axis {axis}: {key}"
                assert cur[3] >= prev[3], f"resource_allocation regressed on axis {axis}: {key}"
                assert cur[4] >= prev[4], f"response_priority regressed on axis {axis}: {key}"


# ── score_to_level ────────────────────────────────────────────────────────

@pytest.mark.parametrize("score,expected", [
    (0.0, "Low"), (3.4, "Low"),
    (3.5, "Medium"), (6.4, "Medium"),
    (6.5, "High"), (8.9, "High"),
    (9.0, "Critical"), (10.0, "Critical"),
])
def test_score_to_level_thresholds(score, expected):
    assert score_to_level(score) == expected


# ── compute_resources (end-to-end fuzzy inference) ──────────────────────────
# Requires scikit-fuzzy to actually be installed to run (it builds and
# simulates the real control system), same as the rest of the fuzzy engine.

def test_compute_resources_returns_four_values_within_caps():
    personnel, barricades, resource_alloc, response_pri = compute_resources(
        duration_mins=60, priority=2, severity_score=5.0, crowd_size=200,
    )
    assert 0 <= personnel <= 30
    assert 0 <= barricades <= 80
    assert 0.0 <= resource_alloc <= 10.0
    assert 0.0 <= response_pri <= 10.0


def test_compute_resources_higher_severity_yields_more_resources():
    """Same duration/priority/crowd; only severity differs (issue #21:
    'Events with similar crowd sizes but different causes ... should
    produce different deployment strategies')."""
    low_sev = compute_severity_score(False, "pot_holes", "auto", False)
    high_sev = compute_severity_score(True, "accident", "heavy_vehicle", True)
    assert high_sev > low_sev

    p1, b1, r1, resp1 = compute_resources(60, 2, low_sev, 100)
    p2, b2, r2, resp2 = compute_resources(60, 2, high_sev, 100)

    assert p2 >= p1
    assert b2 >= b1
    assert r2 >= r1
    assert resp2 >= resp1
    # At least one output should meaningfully differ, not just tie.
    assert (p2, b2, r2, resp2) != (p1, b1, r1, resp1)


def test_compute_resources_larger_crowd_increases_barricades():
    _, small_barricades, _, _ = compute_resources(60, 2, 4.0, crowd_size=20)
    _, large_barricades, _, _ = compute_resources(60, 2, 4.0, crowd_size=1500)
    assert large_barricades >= small_barricades


def test_compute_resources_different_causes_same_crowd_diverge():
    """Two events with identical duration/priority/crowd but different
    event_cause + veh_type should not collapse to identical deployments.
    """
    breakdown_sev = compute_severity_score(False, "vehicle_breakdown", "private_car", False)
    protest_sev = compute_severity_score(True, "protest", "bmtc_bus", True)

    breakdown = compute_resources(45, 3, breakdown_sev, 300)
    protest = compute_resources(45, 3, protest_sev, 300)

    assert breakdown != protest
