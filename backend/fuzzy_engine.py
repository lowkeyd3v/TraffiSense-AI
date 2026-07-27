import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def get_fuzzy_system():
    """Builds an IRC:SP:55 / MoRTH-aligned fuzzy system.

    Inputs:
      - predicted_duration: minutes (0–300)
      - corridor_priority: 1 (Low), 2 (Medium), 3 (High)

    Outputs:
      - personnel_required: 0–12 (capable of matching MoRTH teams)
      - barricades_needed: 0–50 (IRC-aligned spacing and taper lengths)
    """
    # Antecedents (Inputs)
    predicted_duration = ctrl.Antecedent(np.arange(0, 301, 1), 'predicted_duration')
    corridor_priority = ctrl.Antecedent(np.arange(1, 4, 1), 'corridor_priority')

    # Consequents (Outputs)
    personnel_required = ctrl.Consequent(np.arange(0, 13, 1), 'personnel_required')  # 0–12
    barricades_needed = ctrl.Consequent(np.arange(0, 51, 1), 'barricades_needed')    # 0–50

    # -----------------------
    # Duration tiers (severity)
    # Minor: <45 mins (quick clearance)
    # Major: 30–120 mins (standard incident)
    # Severe: >90 mins (long-term / complex)
    predicted_duration['minor'] = fuzz.trapmf(predicted_duration.universe, [0, 0, 20, 45])
    predicted_duration['major'] = fuzz.trimf(predicted_duration.universe, [30, 75, 120])
    predicted_duration['severe'] = fuzz.trapmf(predicted_duration.universe, [90, 150, 300, 300])

    # -----------------------
    # Corridor priority (speed / importance)
    corridor_priority['low'] = fuzz.trimf(corridor_priority.universe, [1, 1, 2])
    corridor_priority['medium'] = fuzz.trimf(corridor_priority.universe, [1, 2, 3])
    corridor_priority['high'] = fuzz.trimf(corridor_priority.universe, [2, 3, 3])

    # -----------------------
    # Outputs — membership functions aligned to IRC / MoRTH guidance
    # Personnel: Minimal (1–3), Standard (4–7), Heavy (8–12)
    personnel_required['minimal'] = fuzz.trimf(personnel_required.universe, [0, 1, 3])
    personnel_required['standard'] = fuzz.trimf(personnel_required.universe, [3, 5.5, 8])
    personnel_required['heavy'] = fuzz.trapmf(personnel_required.universe, [7, 9, 12, 12])

    # Barricades: Low (5–15), Medium (15–30), High (30–50)
    barricades_needed['low'] = fuzz.trimf(barricades_needed.universe, [0, 5, 15])
    barricades_needed['medium'] = fuzz.trimf(barricades_needed.universe, [12, 20, 30])
    barricades_needed['high'] = fuzz.trapmf(barricades_needed.universe, [28, 35, 50, 50])

    # -----------------------
    # Rules mapping (9 core combinations)
    rules = []

    # Minor duration
    rules.append(ctrl.Rule(predicted_duration['minor'] & corridor_priority['low'],
                           (personnel_required['minimal'], barricades_needed['low'])))
    rules.append(ctrl.Rule(predicted_duration['minor'] & corridor_priority['medium'],
                           (personnel_required['minimal'], barricades_needed['medium'])))
    rules.append(ctrl.Rule(predicted_duration['minor'] & corridor_priority['high'],
                           (personnel_required['standard'], barricades_needed['medium'])))

    # Major duration
    rules.append(ctrl.Rule(predicted_duration['major'] & corridor_priority['low'],
                           (personnel_required['standard'], barricades_needed['medium'])))
    rules.append(ctrl.Rule(predicted_duration['major'] & corridor_priority['medium'],
                           (personnel_required['standard'], barricades_needed['medium'])))
    rules.append(ctrl.Rule(predicted_duration['major'] & corridor_priority['high'],
                           (personnel_required['heavy'], barricades_needed['high'])))

    # Severe duration
    rules.append(ctrl.Rule(predicted_duration['severe'] & corridor_priority['low'],
                           (personnel_required['standard'], barricades_needed['medium'])))
    rules.append(ctrl.Rule(predicted_duration['severe'] & corridor_priority['medium'],
                           (personnel_required['heavy'], barricades_needed['high'])))
    rules.append(ctrl.Rule(predicted_duration['severe'] & corridor_priority['high'],
                           (personnel_required['heavy'], barricades_needed['high'])))

    resource_ctrl = ctrl.ControlSystem(rules)
    resource_sim = ctrl.ControlSystemSimulation(resource_ctrl)

    return resource_sim


def compute_resources(duration_mins: float, priority: int, personnel_cap: int = 12, barricade_cap: int = 50):
    """Compute personnel and barricade recommendations.

    Caps default to `personnel_cap=12` and `barricade_cap=50` per plan; caller may override.
    """
    sim = get_fuzzy_system()

    # Cap inputs
    dur = max(0.0, min(300.0, float(duration_mins)))
    pri = int(max(1, min(3, int(priority))))

    sim.input['predicted_duration'] = dur
    sim.input['corridor_priority'] = pri

    # Compute
    sim.compute()

    personnel = int(round(sim.output['personnel_required']))
    barricades = int(round(sim.output['barricades_needed']))

    # Apply caps
    personnel = max(0, min(personnel_cap, personnel))
    barricades = max(0, min(barricade_cap, barricades))

    return personnel, barricades


if __name__ == "__main__":
    # Verification examples: these should approximate the target values in the plan
    examples = [ (15, 1), (150, 3) ]
    for d, p in examples:
        per, bar = compute_resources(d, p)
        print(f"Duration {d}m, Priority {p} -> Personnel: {per}, Barricades: {bar}")
