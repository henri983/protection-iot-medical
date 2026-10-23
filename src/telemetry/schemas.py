"""
Schémas de validation des flux de télémétrie médicale IoMT.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class TelemetryFrame(BaseModel):
    """Trame télémétrique brute émise par un capteur médical connecté."""

    device_id: str = Field(..., description="Identifiant unique du capteur")
    sequence_number: int = Field(..., ge=0, description="Numéro de séquence incrémental anti-rejeu")
    timestamp: float = Field(..., description="Horodatage UNIX en secondes")
    metrics: Dict[str, float] = Field(..., description="Données physiologiques brutes")
    hmac_signature: str = Field(..., description="Signature d'intégrité de la trame")


class TelemetryValidationResult(BaseModel):
    """Résultat du contrôle d'intégrité et physiologique."""

    is_valid: bool
    device_id: str
    errors: list[str] = []
    sanitized_metrics: Optional[Dict[str, float]] = None
