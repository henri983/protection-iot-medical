"""
Tests IA : Détection d'attaques par gel de signal (Freeze Attack).
"""

import time
import pytest
from src.ai.detectors.signal_anomaly_detector import IoMTSignalAnomalyDetector


@pytest.mark.ai
class TestFreezeAttackDetection:

    def test_natural_variable_signal_is_normal(self):
        detector = IoMTSignalAnomalyDetector()
        device_id = "DEV-OX-NORMAL"
        t0 = time.time()

        # Flux physiologique normal avec variabilité naturelle du rythme cardiaque
        normal_bpm = [72.1, 73.0, 71.8, 72.5, 73.2, 72.0, 71.5]
        for i, val in enumerate(normal_bpm):
            res = detector.ingest_and_evaluate(device_id, t0 + i * 1.0, {"heart_rate": val})

        assert res.is_anomaly is False
        assert res.risk_score < 0.5
        assert res.suggested_action == "allow"

    def test_freeze_attack_triggers_quarantine(self):
        detector = IoMTSignalAnomalyDetector()
        device_id = "DEV-OX-FROZEN"
        t0 = time.time()

        # Attaque : injection répétée de la valeur exacte 75.00000 sans aucune micro-variabilité
        frozen_bpm = [75.0, 75.0, 75.0, 75.0, 75.0, 75.0]
        final_res = None
        for i, val in enumerate(frozen_bpm):
            final_res = detector.ingest_and_evaluate(device_id, t0 + i * 1.0, {"heart_rate": val})

        assert final_res is not None
        assert final_res.is_anomaly is True
        assert final_res.risk_score >= 0.8
        assert final_res.suggested_action == "quarantine"
        assert any("freeze attack" in r.lower() for r in final_res.reasons)
