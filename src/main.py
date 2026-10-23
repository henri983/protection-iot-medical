"""
Application FastAPI - Passerelle IoMT et API de Surveillance Médicale.
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from src.config import Settings, get_settings
from src.crypto.lightweight_crypto import IoMTCryptoEngine
from src.device_mgmt.registry import (
    DeviceRegistry,
    DeviceStatus,
    MedicalDevice,
    MedicalDeviceType,
)
from src.gateway.edge_gateway import GatewayProcessingResult, IoMTEdgeGateway
from src.telemetry.schemas import TelemetryFrame


class DeviceRegisterRequest(BaseModel):
    device_id: str = Field(..., examples=["PULSE-OX-001"])
    device_type: MedicalDeviceType = Field(..., examples=[MedicalDeviceType.PULSE_OXIMETER])
    manufacturer: str = Field(..., examples=["MedTech Solutions"])
    firmware_version: str = Field(..., examples=["v2.1.0-secure"])
    hardware_uid: str = Field(..., examples=["HW-84920492"])
    patient_id: Optional[str] = Field(None, examples=["PAT-9912"])


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    current_settings = settings or get_settings()

    app = FastAPI(
        title="Passerelle Sécurisée IoMT & Détection d'Anomalies IA",
        description="Architecture de protection des dispositifs médicaux connectés sous MDR UE 2017/745",
        version="1.0.0",
    )

    # Initialisation des briques singletons pour l'instance
    crypto = IoMTCryptoEngine(shared_secret_hex=current_settings.GATEWAY_SECRET_KEY)
    registry = DeviceRegistry()
    gateway = IoMTEdgeGateway(crypto_engine=crypto, registry=registry)

    # Stocker sur l'état de l'application
    app.state.crypto = crypto
    app.state.registry = registry
    app.state.gateway = gateway

    @app.get("/health", tags=["Monitoring"])
    async def health() -> dict:
        return {
            "status": "healthy",
            "service": "protection-iot-medical",
            "version": "1.0.0",
            "active_devices": len([d for d in registry.list_devices() if d.status == DeviceStatus.ACTIVE]),
        }

    @app.post(
        "/api/v1/devices/register",
        status_code=status.HTTP_201_CREATED,
        tags=["Device Management"],
    )
    async def register_device(payload: DeviceRegisterRequest) -> dict:
        try:
            device = registry.register_device(
                device_id=payload.device_id,
                device_type=payload.device_type,
                manufacturer=payload.manufacturer,
                firmware_version=payload.firmware_version,
                hardware_uid=payload.hardware_uid,
                patient_id=payload.patient_id,
            )
            return {
                "message": "Dispositif médical enrôlé avec succès",
                "device_id": device.device_id,
                "status": device.status.value,
            }
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    @app.get("/api/v1/devices/", tags=["Device Management"])
    async def list_devices() -> List[dict]:
        return [
            {
                "device_id": d.device_id,
                "type": d.device_type.value,
                "manufacturer": d.manufacturer,
                "firmware": d.firmware_version,
                "status": d.status.value,
                "patient_id": d.patient_id,
            }
            for d in registry.list_devices()
        ]

    @app.post("/api/v1/devices/{device_id}/revoke", tags=["Device Management"])
    async def revoke_device(device_id: str) -> dict:
        success = registry.revoke_device(device_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositif introuvable.")
        return {"message": f"Dispositif {device_id} révoqué immédiatement."}

    @app.post("/api/v1/telemetry/ingest", tags=["Telemetry & Security Gateway"])
    async def ingest_telemetry(frame: TelemetryFrame) -> dict:
        result: GatewayProcessingResult = gateway.process_telemetry_frame(frame)
        if result.status == "REJECTED":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.message)

        return {
            "status": result.status,
            "device_id": result.device_id,
            "risk_score": result.risk_score,
            "message": result.message,
            "reasons": result.reasons,
        }

    return app


app = create_app()
