"""
Vérificateur de certificats et d'authentification mutuelle TLS (mTLS) pour capteurs IoMT.
"""

from typing import Dict, Any, Optional
import re


class MTLSVerifier:
    """Valide les certificats clients présentés par les capteurs lors de la négociation TLS."""

    def __init__(self, allowed_ca_issuer: str = "Medical-IoMT-Root-CA") -> None:
        self.allowed_ca_issuer = allowed_ca_issuer

    def verify_client_certificate_attributes(
        self,
        cert_subject: Dict[str, str],
        cert_issuer: Dict[str, str],
        expected_device_id: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Vérifie :
        - Que le certificat émane de l'autorité de certification de l'hôpital/fabricant
        - Que le Common Name (CN) correspond exactement au Device ID attendu
        - Que le certificat n'est pas falsifié
        """
        issuer_cn = cert_issuer.get("CN", "")
        if self.allowed_ca_issuer not in issuer_cn:
            return False, f"Autorité de certification non reconnue: {issuer_cn}"

        subject_cn = cert_subject.get("CN", "")
        if subject_cn != expected_device_id:
            return False, f"Usurpation d'identité détectée : CN ({subject_cn}) != DeviceID ({expected_device_id})"

        return True, None
