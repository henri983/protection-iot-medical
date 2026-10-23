"""
Passerelle Edge de sécurité IoMT (Medical IoT Edge Gateway).

Assure le point d'entrée unique et sécurisé pour les flux capteurs :
- Filtrage des dispositifs non autorisés
- Validation d'intégrité et anti-rejeu cryptographique
- Validation physiologique des métriques
- Inférence IA temps réel pour détecter les attaques par manipulation
"""

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.ai.detectors.signal_anomaly_detector import (
    AnomalyDetectionResult,
    IoMTSignalAnomalyDetector,
)
from src.crypto.lightweight_crypto import IoMTCryptoEngine
from src.device_mgmt.registry import DeviceRegistry, DeviceStatus
from src.telemetry.schemas import TelemetryFrame
from src.telemetry.validator import TelemetryValidator


@dataclass
class GatewayProcessingResult:
    """Résultat complet du traitement d'une trame par la passerelle."""

    status: str  # ACCEPTED, REJECTED, QUARANTINED, ANOMALY_DETECTED
    device_id: str
    message: str
    risk_score: float
    metrics: Optional[Dict[str, float]] = None
    reasons: Optional[List[str]] = None


class IoMTEdgeGateway:
    """Passerelle industrielle intégrant sécurité Zero Trust et IA."""

    def __init__(
        self,
        crypto_engine: IoMTCryptoEngine,
        registry: DeviceRegistry,
        detector: Optional[IoMTSignalAnomalyDetector] = None,
    ) -> None:
        self.crypto = crypto_engine
        self.registry = registry
        self.detector = detector or IoMTSignalAnomalyDetector()

    def process_telemetry_frame(self, frame: TelemetryFrame) -> GatewayProcessingResult:
        """Traite une trame télémétrique de bout en bout."""
        device_id = frame.device_id

        # 1. Vérification d'enregistrement du capteur
        if not self.registry.is_authorized(device_id):
            device = self.registry.get_device(device_id)
            status_desc = device.status.value if device else "UNKNOWN_DEVICE"
            return GatewayProcessingResult(
                status="REJECTED",
                device_id=device_id,
                message=f"Dispositif non autorisé ou révoqué (statut: {status_desc}).",
                risk_score=1.0,
            )

        # 2. Vérification cryptographique (Authenticité, Intégrité, Anti-rejeu)
        metrics_serialized = json.dumps(frame.metrics, sort_keys=True)
        is_crypto_valid = self.crypto.verify_frame_integrity(
            device_id=device_id,
            seq_num=frame.sequence_number,
            timestamp=frame.timestamp,
            data_str=metrics_serialized,
            provided_hmac=frame.hmac_signature,
        )

        if not is_crypto_valid:
            # Possible falsification ou rejeu
            return GatewayProcessingResult(
                status="REJECTED",
                device_id=device_id,
                message="Échec d'authentification ou tentative d'attaque par rejeu.",
                risk_score=0.95,
            )

        # 3. Contrôle de cohérence physiologique
        is_physio_valid, physio_errors = TelemetryValidator.validate_metrics(frame.metrics)
        if not is_physio_valid:
            return GatewayProcessingResult(
                status="REJECTED",
                device_id=device_id,
                message=f"Données physiologiquement impossibles: {'; '.join(physio_errors)}",
                risk_score=0.80,
                reasons=physio_errors,
            )

        # 4. Inférence IA - Détection d'anomalies dynamiques
        ai_result: AnomalyDetectionResult = self.detector.ingest_and_evaluate(
            device_id=device_id,
            timestamp=frame.timestamp,
            metrics=frame.metrics,
        )

        # Si l'IA détecte une attaque critique (Freeze / Gradient impossible)
        if ai_result.suggested_action == "quarantine":
            self.registry.quarantine_device(device_id)
            return GatewayProcessingResult(
                status="QUARANTINED",
                device_id=device_id,
                message="Mise en quarantaine automatique : comportement anormal détecté par l'IA.",
                risk_score=ai_result.risk_score,
                reasons=ai_result.reasons,
                metrics=frame.metrics,
            )

        if ai_result.is_anomaly:
            return GatewayProcessingResult(
                status="ANOMALY_DETECTED",
                device_id=device_id,
                message="Alerte : anomalie télémétrique détectée par l'IA.",
                risk_score=ai_result.risk_score,
                reasons=ai_result.reasons,
                metrics=frame.metrics,
            )

        # Tout est valide et normal
        return GatewayProcessingResult(
            status="ACCEPTED",
            device_id=device_id,
            message="Trame validée avec succès.",
            risk_score=ai_result.risk_score,
            metrics=frame.metrics,
        )
