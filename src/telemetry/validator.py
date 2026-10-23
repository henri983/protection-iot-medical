"""
Validateur de cohérence physiologique et sanitaire des métriques médicales.
"""

from typing import Dict, List, Tuple


# Bornes physiologiques plausibles pour éviter les injections de valeurs aberrantes
PHYSIOLOGICAL_RANGES = {
    "heart_rate": (30.0, 240.0),          # BPM
    "spo2": (50.0, 100.0),                # Pourcentage d'oxygénation
    "temperature": (32.0, 43.0),          # Degrés Celsius
    "blood_glucose": (20.0, 600.0),       # mg/dL
    "systolic_bp": (50.0, 260.0),         # mmHg
    "diastolic_bp": (30.0, 160.0),        # mmHg
    "respiratory_rate": (5.0, 60.0),      # Respiration / minute
    "insulin_rate": (0.0, 25.0),          # Unités / heure
}


class TelemetryValidator:
    """Vérifie que les métriques restent dans les limites humaines physiquement possibles."""

    @staticmethod
    def validate_metrics(metrics: Dict[str, float]) -> Tuple[bool, List[str]]:
        """Contrôle chaque mesure rapportée."""
        errors: List[str] = []

        if not metrics:
            return False, ["Aucune métrique fournie dans la trame."]

        for key, value in metrics.items():
            if key in PHYSIOLOGICAL_RANGES:
                min_val, max_val = PHYSIOLOGICAL_RANGES[key]
                if value < min_val or value > max_val:
                    errors.append(
                        f"Valeur aberrante pour {key}: {value} (plage valide : [{min_val}, {max_val}])"
                    )

        return len(errors) == 0, errors
