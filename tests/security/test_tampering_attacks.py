"""
Tests de sécurité : Détection des altérations de données en transit (Man-in-the-Middle).
"""

import json
import time
import pytest
from src.crypto.lightweight_crypto import IoMTCryptoEngine
from src.gateway.edge_gateway import IoMTEdgeGateway
from src.telemetry.schemas import TelemetryFrame


@pytest.mark.security
class TestTamperingAttacks:

    def test_forged_metrics_fail_hmac(
        self, edge_gateway: IoMTEdgeGateway, crypto_engine: IoMTCryptoEngine
    ):
        device_id = "TEST-OX-001"
        seq = 50
        now = time.time()
        legitimate_metrics = {"heart_rate": 75.0, "spo2": 98.0}
        legit_data_str = json.dumps(legitimate_metrics, sort_keys=True)
        sig = crypto_engine.generate_frame_hmac(device_id, seq, now, legit_data_str)

        # Un attaquant intercepte et falsifie les métriques sans pouvoir recalculer le HMAC secret
        tampered_metrics = {"heart_rate": 180.0, "spo2": 70.0}
        tampered_frame = TelemetryFrame(
            device_id=device_id,
            sequence_number=seq,
            timestamp=now,
            metrics=tampered_metrics,
            hmac_signature=sig,
        )

        result = edge_gateway.process_telemetry_frame(tampered_frame)
        assert result.status == "REJECTED"
        assert result.risk_score >= 0.9
