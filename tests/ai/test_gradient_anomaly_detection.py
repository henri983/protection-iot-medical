"""
Tests IA : Détection d'anomalies brutales de gradient et sauts physiologiquement impossibles.
"""

import time
import pytest
from src.ai.detectors.signal_anomaly_detector import IoMTSignalAnomalyDetector


@pytest.mark.ai
class TestGradientAnomalyDetection:

    def test_abrupt_cardiac_jump_detected(self):
        detector = IoMTSignalAnomalyDetector()
        device_id = "DEV-ECG-01"
        t0 = time.time()

        # Phase normale
        detector.ingest_and_evaluate(device_id, t0, {"heart_rate": 70.0})
        detector.ingest_and_evaluate(device_id, t0 + 1.0, {"heart_rate": 72.0})
        detector.ingest_and_evaluate(device_id, t0 + 2.0, {"heart_rate": 74.0})

        # Saut impossible : bondit de 74 à 180 bpm en seulement 0.2 seconde
        res = detector.ingest_and_evaluate(device_id, t0 + 2.2, {"heart_rate": 180.0})
        assert res.is_anomaly is True
        assert res.risk_score >= 0.85
        assert any("variation cardiaque" in r.lower() for r in res.reasons)

    def test_thermal_step_jump_detected(self):
        detector = IoMTSignalAnomalyDetector()
        device_id = "DEV-TEMP-01"
        t0 = time.time()

        # Température stable
        detector.ingest_and_evaluate(device_id, t0, {"temperature": 37.0})
        detector.ingest_and_evaluate(device_id, t0 + 1.0, {"temperature": 37.1})
        detector.ingest_and_evaluate(device_id, t0 + 2.0, {"temperature": 37.0})

        # Saut thermique aberrant (37°C à 41°C en 1 seconde)
        res = detector.ingest_and_evaluate(device_id, t0 + 3.0, {"temperature": 41.0})
        assert res.is_anomaly is True
        assert res.risk_score >= 0.90
        assert any("thermique" in r.lower() for r in res.reasons)
