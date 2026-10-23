"""
Tests de sécurité : Blocage des capteurs non enregistrés ou révoqués (Zero Trust).
"""

import json
import time
import pytest
from src.crypto.lightweight_crypto import IoMTCryptoEngine
from src.device_mgmt.registry import DeviceRegistry
from src.gateway.edge_gateway import IoMTEdgeGateway
from src.telemetry.schemas import TelemetryFrame


@pytest.mark.security
class TestUnauthorizedDevice:

    def test_rogue_device_rejected(
        self, edge_gateway: IoMTEdgeGateway, crypto_engine: IoMTCryptoEngine
    ):
        # Capteur fantôme non inscrit dans le DeviceRegistry
        rogue_id = "ROGUE-DEVICE-666"
        now = time.time()
        metrics = {"heart_rate": 80.0}
        sig = crypto_engine.generate_frame_hmac(rogue_id, 1, now, json.dumps(metrics, sort_keys=True))

        frame = TelemetryFrame(
            device_id=rogue_id,
            sequence_number=1,
            timestamp=now,
            metrics=metrics,
            hmac_signature=sig,
        )

        res = edge_gateway.process_telemetry_frame(frame)
        assert res.status == "REJECTED"
        assert "non autorisé" in res.message.lower()

    def test_revoked_device_blocked_immediately(
        self, edge_gateway: IoMTEdgeGateway, registry: DeviceRegistry, crypto_engine: IoMTCryptoEngine
    ):
        device_id = "TEST-OX-001"
        # Révocation du dispositif (ex: capteur volé ou compromis)
        registry.revoke_device(device_id)

        now = time.time()
        metrics = {"heart_rate": 72.0}
        sig = crypto_engine.generate_frame_hmac(device_id, 1, now, json.dumps(metrics, sort_keys=True))

        frame = TelemetryFrame(
            device_id=device_id,
            sequence_number=1,
            timestamp=now,
            metrics=metrics,
            hmac_signature=sig,
        )

        res = edge_gateway.process_telemetry_frame(frame)
        assert res.status == "REJECTED"
        assert "révoqué" in res.message.lower() or "non autorisé" in res.message.lower()
