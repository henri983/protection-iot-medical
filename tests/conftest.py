"""
Fixtures pytest pour la plateforme de protection IoMT.
"""

import time
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.config import Settings
from src.crypto.lightweight_crypto import IoMTCryptoEngine
from src.device_mgmt.registry import (
    DeviceRegistry,
    MedicalDevice,
    MedicalDeviceType,
)
from src.gateway.edge_gateway import IoMTEdgeGateway
from src.main import create_app

TEST_SECRET_HEX = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


@pytest.fixture
def crypto_engine() -> IoMTCryptoEngine:
    return IoMTCryptoEngine(shared_secret_hex=TEST_SECRET_HEX)


@pytest.fixture
def registry() -> DeviceRegistry:
    reg = DeviceRegistry()
    reg.register_device(
        device_id="TEST-OX-001",
        device_type=MedicalDeviceType.PULSE_OXIMETER,
        manufacturer="HealthCorp",
        firmware_version="1.0.0",
        hardware_uid="HW-12345",
        patient_id="PAT-001",
    )
    reg.register_device(
        device_id="TEST-ECG-002",
        device_type=MedicalDeviceType.ECG_MONITOR,
        manufacturer="CardioCare",
        firmware_version="2.1.0",
        hardware_uid="HW-67890",
        patient_id="PAT-002",
    )
    return reg


@pytest.fixture
def edge_gateway(crypto_engine, registry) -> IoMTEdgeGateway:
    return IoMTEdgeGateway(crypto_engine=crypto_engine, registry=registry)


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        GATEWAY_SECRET_KEY=TEST_SECRET_HEX,
        ENVIRONMENT="test",
    )


@pytest_asyncio.fixture
async def app_instance(test_settings):
    return create_app(settings=test_settings)


@pytest_asyncio.fixture
async def client(app_instance) -> AsyncClient:
    transport = ASGITransport(app=app_instance)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
