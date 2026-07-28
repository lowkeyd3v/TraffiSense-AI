from app.models.traffic import Traffic


def generate_prediction(traffic: Traffic):
    """
    Dummy AI prediction.
    Later this function will call the real ML model.
    """

    if traffic.vehicle_count >= 250:
        return {
            "predicted_congestion": "High",
            "risk_score": 0.90,
            "recommended_action": "Increase green signal duration",
            "incident_type": "Heavy Traffic",
        }

    elif traffic.vehicle_count >= 120:
        return {
            "predicted_congestion": "Medium",
            "risk_score": 0.60,
            "recommended_action": "Monitor traffic flow",
            "incident_type": None,
        }

    return {
        "predicted_congestion": "Low",
        "risk_score": 0.20,
        "recommended_action": "Normal operation",
        "incident_type": None,
    }