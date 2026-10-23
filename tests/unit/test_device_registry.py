"""
Tests unitaires pour le registre d'équipements médicaux.
"""

import pytest
from src.device_mgmt.registry import (
    DeviceRegistry,
    DeviceStatus,
    MedicalDeviceType,
)


@pytest.mark.unit
class TestDeviceRegistry:

    def test_register_device_success(self, registry: DeviceRegistry):
        dev = registry.register_device(
            device_id="PUMP-003",
            device_type=MedicalDeviceType.INSULIN_PUMP,
            manufacturer="DiabetesCare",
            firmware_version="3.0",
            hardware_uid="HW-9988",
        )
        assert dev.device_id == "PUMP-003"
        assert dev.status == DeviceStatus.ACTIVE
        assert registry.is_authorized("PUMP-003") is True

    def test_register_duplicate_fails(self, registry: DeviceRegistry):
        with pytest.raises(ValueError):
            registry.register_device(
                device_id="TEST-OX-001",  # déjà dans la fixture
                device_type=MedicalDeviceType.PULSE_OXIMETER,
                manufacturer="Any",
                firmware_version="1.0",
                hardware_uid="HW-00",
            )

    def test_revoke_device(self, registry: DeviceRegistry):
        assert registry.is_authorized("TEST-OX-001") is True
        revoked = registry.revoke_device("TEST-OX-001")
        assert revoked is True
        assert registry.is_authorized("TEST-OX-001") is False

    def test_quarantine_device(self, registry: DeviceRegistry):
        quarantined = registry.quarantine_device("TEST-ECG-002")
        assert quarantined is True
        dev = registry.get_device("TEST-ECG-002")
        assert dev.status == DeviceStatus.QUARANTINED
        assert registry.is_authorized("TEST-ECG-002") is False
