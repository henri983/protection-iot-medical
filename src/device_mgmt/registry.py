"""
Registre de gestion et d'enrôlement des dispositifs médicaux (IoMT Device Inventory).
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
import uuid


class DeviceStatus(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    QUARANTINED = "quarantined"
    PENDING_VERIFICATION = "pending_verification"


class MedicalDeviceType(str, Enum):
    PULSE_OXIMETER = "pulse_oximeter"
    ECG_MONITOR = "ecg_monitor"
    INSULIN_PUMP = "insulin_pump"
    TEMP_SENSOR = "temperature_sensor"
    BLOOD_PRESSURE = "blood_pressure_monitor"


@dataclass
class MedicalDevice:
    """Représentation d'un dispositif médical connecté sous MDR UE 2017/745."""

    device_id: str
    device_type: MedicalDeviceType
    manufacturer: str
    firmware_version: str
    hardware_uid: str
    patient_id: Optional[str] = None
    status: DeviceStatus = DeviceStatus.ACTIVE
    registered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_seen: Optional[str] = None
    security_score: float = 1.0


class DeviceRegistry:
    """Gestionnaire d'inventaire sécurisé et contrôle d'accès des équipements."""

    def __init__(self) -> None:
        self._devices: Dict[str, MedicalDevice] = {}

    def register_device(
        self,
        device_id: str,
        device_type: MedicalDeviceType,
        manufacturer: str,
        firmware_version: str,
        hardware_uid: str,
        patient_id: Optional[str] = None,
    ) -> MedicalDevice:
        """Enrôle un nouvel équipement après validation de conformité."""
        if device_id in self._devices:
            raise ValueError(f"Le dispositif {device_id} est déjà enregistré.")

        device = MedicalDevice(
            device_id=device_id,
            device_type=device_type,
            manufacturer=manufacturer,
            firmware_version=firmware_version,
            hardware_uid=hardware_uid,
            patient_id=patient_id,
            status=DeviceStatus.ACTIVE,
        )
        self._devices[device_id] = device
        return device

    def get_device(self, device_id: str) -> Optional[MedicalDevice]:
        """Consulte les caractéristiques d'un dispositif."""
        return self._devices.get(device_id)

    def revoke_device(self, device_id: str, reason: str = "Compromission de sécurité") -> bool:
        """Révoque immédiatement l'accès d'un dispositif (Kill Switch)."""
        device = self.get_device(device_id)
        if not device:
            return False
        device.status = DeviceStatus.REVOKED
        return True

    def quarantine_device(self, device_id: str) -> bool:
        """Isole un dispositif suspecté de dysfonctionnement ou d'anomalie IA."""
        device = self.get_device(device_id)
        if not device:
            return False
        device.status = DeviceStatus.QUARANTINED
        return True

    def is_authorized(self, device_id: str) -> bool:
        """Vérifie si le dispositif a le droit d'émettre de la télémétrie."""
        device = self.get_device(device_id)
        if not device:
            return False
        return device.status == DeviceStatus.ACTIVE

    def list_devices(self) -> List[MedicalDevice]:
        """Retourne l'ensemble de la flotte de capteurs."""
        return list(self._devices.values())
