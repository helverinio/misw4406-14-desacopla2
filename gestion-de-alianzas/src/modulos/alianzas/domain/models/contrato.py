from datetime import datetime, date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class EstadoContrato(str, Enum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    VENCIDO = "vencido"
    CANCELADO = "cancelado"

class TipoContrato(str, Enum):
    CPA = "CPA"  # Cost per action
    CPL = "CPL"  # Cost per lead
    CPC = "CPC"  # Cost per click
    REVSHARE = "revshare"
    FIJO = "fijo"

class Contrato(BaseModel):
    """Modelo de Contrato asociado a un Partner"""
    id: Optional[str] = Field(None, description="Identificador único del contrato")
    partner_id: str = Field(..., description="Referencia al socio (Partner) relacionado")
    tipo: TipoContrato = Field(..., description="Tipo de contrato")
    fecha_inicio: date = Field(..., description="Fecha de inicio del contrato")
    fecha_fin: Optional[date] = Field(None, description="Fecha de fin del contrato, si aplica")
    monto: Optional[float] = Field(None, description="Monto total o comisión asociada")
    moneda: Optional[str] = Field("USD", description="Moneda del contrato")
    condiciones: Optional[str] = Field(None, description="Términos y condiciones adicionales")
    estado: EstadoContrato = Field(default=EstadoContrato.ACTIVO, description="Estado actual del contrato")
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = None
