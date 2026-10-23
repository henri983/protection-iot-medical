"""
Cryptographie légère adaptée aux dispositifs IoMT à ressources contraintes.

Implémente :
- ChaCha20-Poly1305 (hautes performances sur microcontrôleurs sans accélération matérielle AES)
- AES-128-GCM (standard pour dispositifs avec coprocesseur cryptographique)
- HMAC-SHA256 pour l'intégrité des trames
- Protection anti-rejeu (Replay Protection) via nonces et fenêtres temporelles
"""

import hmac
import hashlib
import os
import time
from typing import Dict, Tuple, Optional
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305, AESGCM


class IoMTCryptoEngine:
    """Moteur cryptographique léger pour capteurs et passerelle Edge."""

    def __init__(self, shared_secret_hex: Optional[str] = None) -> None:
        if shared_secret_hex:
            self.key = bytes.fromhex(shared_secret_hex)
        else:
            self.key = os.urandom(32)

        if len(self.key) != 32:
            raise ValueError("La clé secrète partagée doit faire exactement 32 octets (256 bits).")

        self.chacha = ChaCha20Poly1305(self.key)
        self.aes = AESGCM(self.key[:16])  # Clé 128 bits pour AES-128-GCM léger

        # Registre pour la protection anti-rejeu : device_id -> dernier sequence_number
        self._last_sequences: Dict[str, int] = {}

    def encrypt_payload_chacha(self, plaintext: str, associated_data: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """Chiffre avec ChaCha20-Poly1305 (recommandé IoMT faible consommation)."""
        nonce = os.urandom(12)
        ciphertext = self.chacha.encrypt(nonce, plaintext.encode("utf-8"), associated_data)
        return nonce, ciphertext

    def decrypt_payload_chacha(self, nonce: bytes, ciphertext: bytes, associated_data: Optional[bytes] = None) -> str:
        """Déchiffre un payload chiffré en ChaCha20-Poly1305."""
        plaintext_bytes = self.chacha.decrypt(nonce, ciphertext, associated_data)
        return plaintext_bytes.decode("utf-8")

    def generate_frame_hmac(self, device_id: str, seq_num: int, timestamp: float, data_str: str) -> str:
        """Calcule la signature d'intégrité HMAC-SHA256 d'une trame."""
        message = f"{device_id}:{seq_num}:{timestamp:.3f}:{data_str}".encode("utf-8")
        return hmac.new(self.key, message, hashlib.sha256).hexdigest()

    def verify_frame_integrity(
        self,
        device_id: str,
        seq_num: int,
        timestamp: float,
        data_str: str,
        provided_hmac: str,
        max_time_drift_seconds: float = 60.0,
    ) -> bool:
        """
        Vérifie l'authenticité, l'intégrité et l'absence de rejeu d'une trame.
        """
        # 1. Vérification de dérive d'horloge
        now = time.time()
        if abs(now - timestamp) > max_time_drift_seconds:
            return False

        # 2. Vérification anti-rejeu sur numéro de séquence
        last_seq = self._last_sequences.get(device_id, -1)
        if seq_num <= last_seq:
            return False

        # 3. Vérification de la signature HMAC (temps constant)
        expected_hmac = self.generate_frame_hmac(device_id, seq_num, timestamp, data_str)
        if not hmac.compare_digest(expected_hmac, provided_hmac):
            return False

        # Mise à jour de la séquence acceptée
        self._last_sequences[device_id] = seq_num
        return True
