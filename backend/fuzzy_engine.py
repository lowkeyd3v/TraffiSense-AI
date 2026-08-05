"""Fuzzy logic decision engine for resource deployment (IRC:SP:55 / MoRTH aligned).

Inputs
------
  - predicted_duration : minutes (0-300)              [existing]
  - corridor_priority   : 1 (Low), 2 (Medium), 3 (High) [existing]
  - severity_score       : 0-10 composite risk score derived from the
                            severity keyword flag, event cause and vehicle
                            type (see `compute_severity_score`)            [new]
  - crowd_size           : estimated people at the scene, 0-2000+          [new]

`severity_score` folds three of the inputs requested in issue #21 — severity
keyword, vehicle type and event cause — into a single 0-10 antecedent rather
than adding three more raw categorical antecedents to the fuzzy system
(which would blow up the rule base combinatorially: 3 additional 3-valued
antecedents means 3^5 = 243 raw rules instead of 3^4 = 81). Event cause and
vehicle type are mapped to numeric risk weights via lookup tables, blended
with the severity keyword flag and road-closure flag, and the result feeds
the fuzzy system as a normal numeric antecedent.

`requires_road_closure` (the other "existing" input named in the issue) is
folded into `severity_score` as well, since a closure reliably signals a
more serious/complex event — this avoids a fifth antecedent while still
letting road closures shift every output.

Outputs
-------
  - personnel_required   : 0-30  (headcount)                     [existing, range widened]
  - barricades_needed    : 0-80  (IRC-aligned spacing/taper)      [existing, range widened]
  - resource_allocation  : 0-10  (overall deployment intensity)   [new]
  - response_priority    : 0-10  (urgency / dispatch priority)    [new]

The 81-combination rule base (duration x priority x severity x crowd, each
3-valued) is generated programmatically from a small weighted-scoring
function (`_rule_table`) rather than hand-written line by line — this is a
standard Fuzzy Associative Memory (FAM) table technique and keeps the rule
base auditable (the weights and thresholds are the "rules", not 81 lines of
boilerplate).
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# ── Risk-weight lookup tables (0-10 scale) ──────────────────────────────────
# Used only to build `severity_score`; keeps event_cause / veh_type out of
# the fuzzy antecedent set directly while still letting them influence every
# output. Unseen values fall back to a moderate default.
EVENT_CAUSE_RISK = {
    'accident': 8.5, 'protest': 8.0, 'procession': 7.0, 'tree_fall': 6.5,
    'water_logging': 6.0, 'public_event': 6.0, 'vip_movement': 5.0,
    'construction': 4.0, 'congestion': 3.5, 'road_conditions': 3.0,
    'vehicle_breakdown': 3.0, 'pot_holes': 2.0, 'others': 4.0,
}
DEFAULT_EVENT_CAUSE_RISK = 4.0

VEH_TYPE_RISK = {
    'heavy_vehicle': 8.0, 'truck': 7.0, 'lcv': 5.0, 'bmtc_bus': 6.0,
    'ksrtc_bus': 6.0, 'private_bus': 6.0, 'private_car': 3.0, 'taxi': 3.0,
    'auto': 2.0, 'others': 4.0, 'unknown': 4.0,
}
DEFAULT_VEH_TYPE_RISK = 4.0


def compute_severity_score(has_severity_keyword: bool, event_cause: str,
                            veh_type: str, requires_road_closure: bool) -> float:
    """Blend severity keyword / event cause / vehicle type / road closure
    into a single 0-10 composite fed to the fuzzy system as `severity_score`.
    """
    cause_risk = EVENT_CAUSE_RISK.get((event_cause or '').lower(), DEFAULT_EVENT_CAUSE_RISK)
    veh_risk = VEH_TYPE_RISK.get((veh_type or '').lower(), DEFAULT_VEH_TYPE_RISK)

    score = (0.45 * cause_risk) + (0.25 * veh_risk)
    score += 3.0 if has_severity_keyword else 0.0
    score += 1.5 if requires_road_closure else 0.0

    return round(max(0.0, min(10.0, score)), 2)


# ── FAM (Fuzzy Associative Memory) table generation ─────────────────────────
# Level index 0/1/2 maps to the low/medium/high term of each antecedent.
_LEVELS = (0, 1, 2)

# Weight of each antecedent toward each composite output. Tuned so that
# duration + severity dominate personnel/priority, while duration + crowd
# dominate barricades (crowd control needs more physical barriers, not more
# people per se), matching real-world deployment practice.
_PERSONNEL_W = dict(duration=1.3, priority=1.0, severity=1.4, crowd=0.8)
_BARRICADE_W = dict(duration=1.4, priority=0.6, severity=1.1, crowd=1.4)
_PRIORITY_W = dict(duration=1.1, priority=1.6, severity=1.5, crowd=0.5)


def _composite(weights: dict, d: int, p: int, s: int, c: int) -> float:
    return (weights['duration'] * d + weights['priority'] * p +
            weights['severity'] * s + weights['crowd'] * c)


def _bucket3(value: float, low_max: float, mid_max: float) -> int:
    """Map a composite score to a 3-level bucket: 0=low/minimal, 1=mid, 2=high."""
    if value < low_max:
        return 0
    if value < mid_max:
        return 1
    return 2


def _bucket4(value: float, thresholds: tuple) -> int:
    """Map a composite score to a 4-level bucket (low/medium/high/critical)."""
    low_max, mid_max, high_max = thresholds
    if value < low_max:
        return 0
    if value < mid_max:
        return 1
    if value < high_max:
        return 2
    return 3


def _rule_table():
    """Yield (duration_lvl, priority_lvl, severity_lvl, crowd_lvl,
    personnel_lvl, barricade_lvl, resource_lvl, response_lvl) for every
    combination of the four antecedents.
    """
    for d in _LEVELS:
        for p in _LEVELS:
            for s in _LEVELS:
                for c in _LEVELS:
                    pc = _composite(_PERSONNEL_W, d, p, s, c)   # max 9.0
                    bc = _composite(_BARRICADE_W, d, p, s, c)   # max 9.0
                    rp = _composite(_PRIORITY_W, d, p, s, c)    # max 9.4

                    personnel_lvl = _bucket3(pc, 3.0, 6.2)
                    barricade_lvl = _bucket3(bc, 3.0, 6.2)

                    # Overall deployment intensity blends both composites.
                    resource_score = (pc + bc) / 1.8  # rescaled to ~0-10
                    resource_lvl = _bucket4(resource_score, (2.5, 5.0, 7.5))
                    response_lvl = _bucket4(rp, (2.9, 5.6, 8.0))

                    yield d, p, s, c, personnel_lvl, barricade_lvl, resource_lvl, response_lvl


def _build_control_system() -> ctrl.ControlSystem:
    """Builds the IRC:SP:55 / MoRTH-aligned fuzzy ControlSystem (see module
    docstring). This constructs the antecedents, consequents, membership
    functions and the full 81-rule base — the expensive, but constant, part
    of the fuzzy system. It is called exactly once per process (see
    `_RESOURCE_CONTROL_SYSTEM` below); callers should never call this
    directly on the request path.
    """
    # ── Antecedents (Inputs) ────────────────────────────────────────────────
    predicted_duration = ctrl.Antecedent(np.arange(0, 301, 1), 'predicted_duration')
    corridor_priority = ctrl.Antecedent(np.arange(1, 4, 1), 'corridor_priority')
    severity_score = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'severity_score')
    crowd_size = ctrl.Antecedent(np.arange(0, 2001, 1), 'crowd_size')

    # ── Consequents (Outputs) ────────────────────────────────────────────────
    personnel_required = ctrl.Consequent(np.arange(0, 31, 1), 'personnel_required')     # 0-30
    barricades_needed = ctrl.Consequent(np.arange(0, 81, 1), 'barricades_needed')       # 0-80
    resource_allocation = ctrl.Consequent(np.arange(0, 10.1, 0.1), 'resource_allocation')  # 0-10
    response_priority = ctrl.Consequent(np.arange(0, 10.1, 0.1), 'response_priority')      # 0-10

    # ── Duration tiers (existing) ────────────────────────────────────────────
    predicted_duration['minor'] = fuzz.trapmf(predicted_duration.universe, [0, 0, 20, 45])
    predicted_duration['major'] = fuzz.trimf(predicted_duration.universe, [30, 75, 120])
    predicted_duration['severe'] = fuzz.trapmf(predicted_duration.universe, [90, 150, 300, 300])

    # ── Corridor priority (existing) ─────────────────────────────────────────
    corridor_priority['low'] = fuzz.trimf(corridor_priority.universe, [1, 1, 2])
    corridor_priority['medium'] = fuzz.trimf(corridor_priority.universe, [1, 2, 3])
    corridor_priority['high'] = fuzz.trimf(corridor_priority.universe, [2, 3, 3])

    # ── Severity score (new) ─────────────────────────────────────────────────
    severity_score['low'] = fuzz.trapmf(severity_score.universe, [0, 0, 2, 4.5])
    severity_score['moderate'] = fuzz.trimf(severity_score.universe, [3, 5, 7])
    severity_score['high'] = fuzz.trapmf(severity_score.universe, [5.5, 8, 10, 10])

    # ── Crowd size (new) ──────────────────────────────────────────────────────
    crowd_size['small'] = fuzz.trapmf(crowd_size.universe, [0, 0, 20, 80])
    crowd_size['moderate'] = fuzz.trimf(crowd_size.universe, [50, 200, 600])
    crowd_size['large'] = fuzz.trapmf(crowd_size.universe, [400, 1000, 2000, 2000])

    # ── Output membership functions ─────────────────────────────────────────
    # Personnel: Minimal / Standard / Heavy
    personnel_required['minimal'] = fuzz.trapmf(personnel_required.universe, [0, 0, 3, 7])
    personnel_required['standard'] = fuzz.trimf(personnel_required.universe, [4, 12, 20])
    personnel_required['heavy'] = fuzz.trapmf(personnel_required.universe, [15, 22, 30, 30])

    # Barricades: Low / Medium / High
    barricades_needed['low'] = fuzz.trapmf(barricades_needed.universe, [0, 0, 10, 25])
    barricades_needed['medium'] = fuzz.trimf(barricades_needed.universe, [15, 35, 55])
    barricades_needed['high'] = fuzz.trapmf(barricades_needed.universe, [40, 60, 80, 80])

    # Resource allocation / Response priority: Low / Medium / High / Critical
    for consequent in (resource_allocation, response_priority):
        consequent['low'] = fuzz.trapmf(consequent.universe, [0, 0, 1.5, 3.5])
        consequent['medium'] = fuzz.trimf(consequent.universe, [2.5, 4.5, 6.5])
        consequent['high'] = fuzz.trimf(consequent.universe, [5.5, 7.2, 9])
        consequent['critical'] = fuzz.trapmf(consequent.universe, [8, 9.2, 10, 10])

    # ── Rule base ─────────────────────────────────────────────────────────────
    duration_terms = ['minor', 'major', 'severe']
    priority_terms = ['low', 'medium', 'high']
    severity_terms = ['low', 'moderate', 'high']
    crowd_terms = ['small', 'moderate', 'large']
    personnel_terms = ['minimal', 'standard', 'heavy']
    barricade_terms = ['low', 'medium', 'high']
    tier4_terms = ['low', 'medium', 'high', 'critical']

    rules = []
    for d, p, s, c, per_lvl, bar_lvl, res_lvl, resp_lvl in _rule_table():
        antecedent = (
            predicted_duration[duration_terms[d]] &
            corridor_priority[priority_terms[p]] &
            severity_score[severity_terms[s]] &
            crowd_size[crowd_terms[c]]
        )
        consequent = (
            personnel_required[personnel_terms[per_lvl]],
            barricades_needed[barricade_terms[bar_lvl]],
            resource_allocation[tier4_terms[res_lvl]],
            response_priority[tier4_terms[resp_lvl]],
        )
        rules.append(ctrl.Rule(antecedent, consequent))

    return ctrl.ControlSystem(rules)


# Built once at import time (i.e. once per worker process on startup), not
# per-request. The ControlSystem holds the antecedents/consequents/rules,
# all of which are read-only once built, so it's safe to share across
# concurrently-handled requests. See issue #42.
_RESOURCE_CONTROL_SYSTEM = _build_control_system()


def get_fuzzy_system() -> ctrl.ControlSystemSimulation:
    """Returns a fresh `ControlSystemSimulation` bound to the cached, shared
    `ControlSystem`. A new simulation is created per call (cheap) because
    `ControlSystemSimulation` carries request-specific input/output state
    that is NOT safe to share across concurrent requests — `/api/predict`
    is a sync endpoint, so FastAPI runs it in a threadpool and multiple
    requests can genuinely execute this concurrently.
    """
    return ctrl.ControlSystemSimulation(_RESOURCE_CONTROL_SYSTEM)


def compute_resources(duration_mins: float, priority: int, severity_score: float = 0.0,
                       crowd_size: float = 0.0, personnel_cap: int = 30,
                       barricade_cap: int = 80):
    """Compute personnel, barricade, resource-allocation and response-priority
    recommendations from the combined event characteristics.

    Returns
    -------
    (personnel, barricades, resource_allocation_score, response_priority_score)
        personnel / barricades are integer counts (capped by *_cap).
        resource_allocation_score / response_priority_score are 0-10 floats
        representing overall deployment intensity / dispatch urgency.
    """
    sim = get_fuzzy_system()

    # Cap inputs to the antecedent universes.
    dur = max(0.0, min(300.0, float(duration_mins)))
    pri = int(max(1, min(3, int(priority))))
    sev = max(0.0, min(10.0, float(severity_score)))
    crowd = max(0.0, min(2000.0, float(crowd_size)))

    sim.input['predicted_duration'] = dur
    sim.input['corridor_priority'] = pri
    sim.input['severity_score'] = sev
    sim.input['crowd_size'] = crowd

    sim.compute()

    personnel = int(round(sim.output['personnel_required']))
    barricades = int(round(sim.output['barricades_needed']))
    resource_alloc = round(float(sim.output['resource_allocation']), 2)
    response_pri = round(float(sim.output['response_priority']), 2)

    personnel = max(0, min(personnel_cap, personnel))
    barricades = max(0, min(barricade_cap, barricades))

    return personnel, barricades, resource_alloc, response_pri


def score_to_level(score: float) -> str:
    """Map a 0-10 resource_allocation / response_priority score to a
    Low/Medium/High/Critical label, matching the fuzzy consequent terms.
    """
    if score < 3.5:
        return "Low"
    if score < 6.5:
        return "Medium"
    if score < 9.0:
        return "High"
    return "Critical"


if __name__ == "__main__":
    # Validation scenarios (acceptance criterion: validate with multiple
    # traffic event scenarios). Same crowd size, different cause/vehicle/
    # severity should produce different deployment strategies.
    scenarios = [
        # (label, duration, priority, has_kw, event_cause, veh_type, closure, crowd)
        ("Minor breakdown, low priority, no crowd",
         15, 1, False, 'vehicle_breakdown', 'private_car', False, 0),
        ("Same duration/priority but severe accident + heavy vehicle",
         15, 1, True, 'accident', 'heavy_vehicle', True, 0),
        ("Major congestion, high priority corridor, moderate crowd",
         80, 3, False, 'congestion', 'private_bus', False, 150),
        ("Protest, high priority, large crowd, road closed",
         180, 3, True, 'protest', 'bmtc_bus', True, 1200),
        ("Severe duration but low priority corridor, no crowd",
         200, 1, False, 'water_logging', 'truck', True, 0),
    ]

    for label, dur, pri, kw, cause, veh, closure, crowd in scenarios:
        sev = compute_severity_score(kw, cause, veh, closure)
        per, bar, res, resp = compute_resources(dur, pri, sev, crowd)
        print(f"{label}")
        print(f"  severity_score={sev:.2f}  ->  personnel={per}, barricades={bar}, "
              f"resource_allocation={res:.2f} ({score_to_level(res)}), "
              f"response_priority={resp:.2f} ({score_to_level(resp)})")