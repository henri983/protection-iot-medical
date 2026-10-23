"""
Tests de sécurité : Protection contre les attaques par rejeu de trames IoMT.
"""

import json
import time
import pytest
from src.crypto.lightweight_crypto import IoMTCryptoEngine
from src.gateway.edge_gateway import IoMTEdgeGateway
from src.telemetry.schemas import TelemetryFrame


@pytest.mark.security
class TestReplayAttacks:

    def test_replayed_frame_rejected(
        self, edge_gateway: IoMTEdgeGateway, crypto_engine: IoMTCryptoEngine
    ):
        device_id = "TEST-OX-001"
        seq = 10
        now = time.time()
        metrics = {"heart_rate": 72.0, "spo2": 99.0}
        data_str = json.dumps(metrics, sort_keys=True)
        sig = crypto_engine.generate_frame_hmac(device_id, seq, now, data_str)

        frame = TelemetryFrame(
            device_id=device_id,
            sequence_number=seq,
            timestamp=now,
            metrics=metrics,
            hmac_signature=sig,
        )

        # 1. Premier envoi légitime : doit être accepté
        first_res = edge_gateway.process_telemetry_frame(frame)
        assert first_res.status == "ACCEPTED"

        # 2. Deuxième envoi identique (attaque par rejeu) : doit être rejeté
        replay_res = edge_gateway.process_telemetry_frame(frame)
        assert replay_res.status == "REJECTED"
        assert "rejeu" in replay_res.message.lower() or "échec" in replay_res.message.lower()

    def test_older_sequence_number_rejected(
        self, edge_gateway: IoMTEdgeGateway, crypto_engine: IoMTCryptoEngine
    ):
        device_id = "TEST-OX-001"
        now = time.time()

        # Envoyer séquence 20
        metrics = {"heart_rate": 70.0}
        sig20 = crypto_engine.generate_frame_hmac(device_id, 20, now, json.dumps(metrics, sort_keys=True))
        edge_gateway.process_telemetry_frame(
            TelemetryFrame(device_id=device_id, sequence_number=20, timestamp=now, metrics=metrics, hmac_signature=sig20)
        )

        # Tenter d'injecter une séquence passée (15)
        sig15 = crypto_engine.generate_frame_hmac(device_id, 15, now, json.dumps(metrics, sort_keys=True))
        res = edge_gateway.process_telemetry_frame(
            TelemetryFrame(device_id=device_id, sequence_number=15, timestamp=now, metrics=metrics, hmac_signature=sig15)
        )
        assert res.status == "REJECTED"
