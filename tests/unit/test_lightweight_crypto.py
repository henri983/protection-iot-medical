"""
Tests unitaires pour la cryptographie légère IoMT.
"""

import time
import pytest
from src.crypto.lightweight_crypto import IoMTCryptoEngine


@pytest.mark.unit
class TestLightweightCrypto:

    def test_chacha20_encrypt_decrypt_roundtrip(self, crypto_engine: IoMTCryptoEngine):
        data = "ECG_WAVEFORM_SAMPLE_DATA_72BPM"
        nonce, ciphertext = crypto_engine.encrypt_payload_chacha(data)
        assert ciphertext != data.encode("utf-8")
        decrypted = crypto_engine.decrypt_payload_chacha(nonce, ciphertext)
        assert decrypted == data

    def test_chacha20_tampered_ciphertext_fails(self, crypto_engine: IoMTCryptoEngine):
        data = "CONFIDENTIAL_PATIENT_METRICS"
        nonce, ciphertext = crypto_engine.encrypt_payload_chacha(data)
        tampered = bytearray(ciphertext)
        tampered[0] ^= 0xFF  # Altération d'un bit
        with pytest.raises(Exception):
            crypto_engine.decrypt_payload_chacha(nonce, bytes(tampered))

    def test_hmac_frame_integrity_valid(self, crypto_engine: IoMTCryptoEngine):
        now = time.time()
        device_id = "DEV-01"
        seq = 1
        data = '{"spo2": 98.0}'
        sig = crypto_engine.generate_frame_hmac(device_id, seq, now, data)
        assert crypto_engine.verify_frame_integrity(device_id, seq, now, data, sig) is True

    def test_hmac_tampered_data_rejected(self, crypto_engine: IoMTCryptoEngine):
        now = time.time()
        device_id = "DEV-01"
        seq = 1
        data = '{"spo2": 98.0}'
        sig = crypto_engine.generate_frame_hmac(device_id, seq, now, data)
        # Donnée falsifiée en transit
        assert crypto_engine.verify_frame_integrity(device_id, seq, now, '{"spo2": 60.0}', sig) is False
