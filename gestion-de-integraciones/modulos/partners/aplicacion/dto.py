from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any

@dataclass
class CrearPartnerDTO:
    """DTO para crear un nuevo partner"""
    nombre: str
    email: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None

@dataclass
class ActualizarPartnerDTO:
    """DTO para actualizar un partner existente"""
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

@dataclass
class VerificarKYCDTO:
    """DTO para verificar KYC de un partner"""
    estado_kyc: str  # APROBADO, RECHAZADO, REQUIERE_DOCUMENTOS
    documentos: Optional[Dict[str, Any]] = None
    comentarios: Optional[str] = None

@dataclass
class CrearIntegracionDTO:
    """DTO para crear una nueva integración"""
    partner_id: str
    tipo: str  # API, WEBHOOK, BATCH, REAL_TIME
    nombre: str
    descripcion: Optional[str] = None
    configuracion: Dict[str, Any] = None

@dataclass
class PartnerResponseDTO:
    """DTO de respuesta para Partner"""
    id: str
    nombre: str
    email: str
    telefono: Optional[str]
    direccion: Optional[str]
    estado: str
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]
    estado_kyc: str
    documentos_kyc: Optional[Dict[str, Any]]
    integraciones: List['IntegracionResponseDTO']

@dataclass
class IntegracionResponseDTO:
    """DTO de respuesta para Integración"""
    id: str
    partner_id: str
    tipo: str
    nombre: str
    descripcion: Optional[str]
    activa: bool
    fecha_creacion: datetime
    fecha_revocacion: Optional[datetime]

@dataclass
class RevocarIntegracionDTO:
    """DTO para revocar una integración"""
    integracion_id: str
    motivo: Optional[str] = None
