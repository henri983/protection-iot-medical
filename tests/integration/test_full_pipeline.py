"""
Tests d'intégration de bout en bout de l'API Passerelle IoMT.
"""

import json
import time
import pytest
from httpx import AsyncClient
from src.crypto.lightweight_crypto import IoMTCryptoEngine

TEST_SECRET = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


@pytest.mark.integration
class TestFullIoMTPipeline:

    async def test_health_check(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "active_devices" in data

    async def test_device_registration_and_list(self, client: AsyncClient):
        # Enregistrer un nouveau capteur
        resp = await client.post(
            "/api/v1/devices/register",
            json={
                "device_id": "PULSE-NEW-101",
                "device_type": "pulse_oximeter",
                "manufacturer": "BioSensor EU",
                "firmware_version": "v3.0.1",
                "hardware_uid": "HW-UNIQUE-101",
                "patient_id": "PAT-4402",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["device_id"] == "PULSE-NEW-101"

        # Vérifier présence dans la liste
        list_resp = await client.get("/api/v1/devices/")
        assert list_resp.status_code == 200
        devices = list_resp.json()
        assert any(d["device_id"] == "PULSE-NEW-101" for d in devices)

    async def test_telemetry_ingestion_endpoint(self, client: AsyncClient):
        device_id = "PULSE-TEST-INGEST"
        # Enregistrer d'abord le capteur dans l'app
        await client.post(
            "/api/v1/devices/register",
            json={
                "device_id": device_id,
                "device_type": "pulse_oximeter",
                "manufacturer": "BioSensor",
                "firmware_version": "v1.0",
                "hardware_uid": "HW-9999",
            },
        )

        crypto = IoMTCryptoEngine(shared_secret_hex=TEST_SECRET)
        seq = 100
        now = time.time()
        metrics = {"heart_rate": 74.0, "spo2": 98.5}
        sig = crypto.generate_frame_hmac(device_id, seq, now, json.dumps(metrics, sort_keys=True))

        resp = await client.post(
            "/api/v1/telemetry/ingest",
            json={
                "device_id": device_id,
                "sequence_number": seq,
                "timestamp": now,
                "metrics": metrics,
                "hmac_signature": sig,
            },
        )
        assert resp.status_code == 200
        res_data = resp.json()
        assert res_data["status"] == "ACCEPTED"
        assert res_data["device_id"] == device_id
