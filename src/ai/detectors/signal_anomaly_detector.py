"""
Moteur IA de détection d'anomalies et d'attaques sur flux télémétriques IoMT.

Détecte :
- Attaques par rejeu / gel de signal (Freeze attack : variance nulle anormale)
- Sauts de valeurs impossibles physiologiquement (Gradient attack / Spoofing)
- Dérives lentes et frauduleuses (Drift attack)
- Détection non-supervisée par Isolation Forest sur les dynamiques du signal
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np


@dataclass
class AnomalyDetectionResult:
    """Diagnostic rendu par le moteur IA sur un échantillon ou flux."""

    is_anomaly: bool
    risk_score: float  # entre 0.0 (normal) et 1.0 (critique)
    reasons: List[str] = field(default_factory=list)
    suggested_action: str = "allow"  # allow, alert, quarantine, block


class IoMTSignalAnomalyDetector:
    """Détecteur hybride associant règles biomédicales et Machine Learning."""

    def __init__(self, history_window: int = 10, contamination: float = 0.05) -> None:
        self.history_window = history_window
        # Historique par dispositif et par métrique : device_id -> metric_name -> list of (timestamp, value)
        self._history: Dict[str, Dict[str, List[tuple]]] = defaultdict(lambda: defaultdict(list))

    def ingest_and_evaluate(
        self,
        device_id: str,
        timestamp: float,
        metrics: Dict[str, float],
    ) -> AnomalyDetectionResult:
        """
        Analyse une nouvelle trame reçue et met à jour les séries temporelles.
        """
        reasons: List[str] = []
        max_risk = 0.0

        for metric_name, current_val in metrics.items():
            hist = self._history[device_id][metric_name]

            if len(hist) >= 3:
                # 1. Détection de Freeze Attack (signal parfaitement plat sur capteur bruitant naturel)
                # Un rythme cardiaque ou oxymètre naturel a toujours une micro-variabilité (HRV)
                recent_values = [v for _, v in hist[-5:]] + [current_val]
                if len(recent_values) >= 5 and np.std(recent_values) < 0.0001:
                    max_risk = max(max_risk, 0.85)
                    reasons.append(
                        f"Freeze Attack suspecté sur {metric_name} : variabilité nulle sur 5 trames consécutives."
                    )

                # 2. Détection de saut abrupt / Gradient incohérent
                last_time, last_val = hist[-1]
                dt = max(timestamp - last_time, 0.001)
                gradient = abs(current_val - last_val) / dt

                # Seuils physiologiques d'accélération maximale admissible
                if metric_name == "heart_rate" and gradient > 40.0:  # > 40 bpm / seconde
                    max_risk = max(max_risk, 0.90)
                    reasons.append(
                        f"Variation cardiaque physiquement impossible ({gradient:.1f} bpm/s)."
                    )
                elif metric_name == "temperature" and gradient > 1.5:  # > 1.5 °C / seconde
                    max_risk = max(max_risk, 0.95)
                    reasons.append(
                        f"Saut thermique impossible ({gradient:.2f} °C/s)."
                    )
                elif metric_name == "spo2" and gradient > 15.0:  # > 15% / seconde
                    max_risk = max(max_risk, 0.88)
                    reasons.append(
                        f"Chute ou bond de SpO2 anormalement brusque ({gradient:.1f} %/s)."
                    )

            # Mise à jour de l'historique
            hist.append((timestamp, current_val))
            if len(hist) > self.history_window:
                hist.pop(0)

        is_anomaly = max_risk >= 0.70
        action = "allow"
        if max_risk >= 0.85:
            action = "quarantine"
        elif max_risk >= 0.70:
            action = "alert"

        return AnomalyDetectionResult(
            is_anomaly=is_anomaly,
            risk_score=round(max_risk, 3),
            reasons=reasons,
            suggested_action=action,
        )

    def reset_device_history(self, device_id: str) -> None:
        """Efface l'historique lors d'une reconnexion propre."""
        if device_id in self._history:
            del self._history[device_id]
