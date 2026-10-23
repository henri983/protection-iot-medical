"""
Tests unitaires pour la validation des métriques physiologiques.
"""

import pytest
from src.telemetry.validator import TelemetryValidator


@pytest.mark.unit
class TestTelemetryValidator:

    def test_valid_physiological_metrics(self):
        metrics = {
            "heart_rate": 75.0,
            "spo2": 98.0,
            "temperature": 37.1,
        }
        is_valid, errors = TelemetryValidator.validate_metrics(metrics)
        assert is_valid is True
        assert len(errors) == 0

    def test_aberrant_spo2_rejected(self):
        # SpO2 à 140% est physiquement impossible
        metrics = {"spo2": 140.0}
        is_valid, errors = TelemetryValidator.validate_metrics(metrics)
        assert is_valid is False
        assert any("spo2" in e for e in errors)

    def test_aberrant_temperature_rejected(self):
        # Température corporelle à 12°C est une anomalie ou tentative d'injection
        metrics = {"temperature": 12.0}
        is_valid, errors = TelemetryValidator.validate_metrics(metrics)
        assert is_valid is False
        assert any("temperature" in e for e in errors)

    def test_empty_metrics_rejected(self):
        is_valid, errors = TelemetryValidator.validate_metrics({})
        assert is_valid is False
