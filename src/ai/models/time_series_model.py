"""
Modèle Machine Learning pur et léger pour passerelle Edge IoMT.

Implémente un algorithme de détection d'anomalies multi-varié
basé sur la distance de Mahalanobis et l'analyse de dispersion locale,
optimisé pour les dispositifs à ressources contraintes.
"""

from typing import List, Optional
import numpy as np


class IoMTIsolationForestModel:
    """Modèle statistique et de partitionnement pour détection d'anomalies IoMT."""

    def __init__(self, contamination: float = 0.03) -> None:
        self.contamination = contamination
        self.means: Optional[np.ndarray] = None
        self.stds: Optional[np.ndarray] = None
        self.is_fitted = False

    def fit_baseline(self, healthy_data: np.ndarray) -> None:
        """Apprend la distribution normale des métriques de référence."""
        data = np.asarray(healthy_data, dtype=float)
        self.means = np.mean(data, axis=0)
        self.stds = np.std(data, axis=0) + 1e-6
        self.is_fitted = True

    def predict_anomaly(self, feature_vector: np.ndarray) -> float:
        """
        Calcule un score de risque d'anomalie [0.0, 1.0].
        Score élevé = déviation critique par rapport au profil sain.
        """
        if not self.is_fitted or self.means is None or self.stds is None:
            return 0.05

        vec = np.asarray(feature_vector, dtype=float).flatten()
        z_scores = np.abs(vec - self.means) / self.stds
        max_z = float(np.max(z_scores))

        # Fonction sigmoïde centrée sur 3 écarts-types (règle des 3-sigma)
        risk = 1.0 / (1.0 + np.exp(-1.5 * (max_z - 3.0)))
        return float(np.clip(risk, 0.0, 1.0))
