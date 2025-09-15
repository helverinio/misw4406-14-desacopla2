from __future__ import annotations
from dataclasses import dataclass
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from .entidades import EstadoPartner, EstadoKYC, TipoIntegracion

class EventoDominio:
    """Clase base para eventos de dominio"""
    def __init__(self):
        self.id: uuid.UUID = uuid.uuid4()
        self.fecha_evento: datetime = datetime.utcnow()

class EventoPartner(EventoDominio):
    """Clase base para eventos relacionados con Partners"""
    pass

@dataclass
class PartnerCreado(EventoPartner):
    """Evento disparado cuando se crea un nuevo partner"""
    partner_id: str
    
    def __post_init__(self):
        super().__init__()

@dataclass
class PartnerActualizado(EventoPartner):
    """Evento disparado cuando se actualiza un partner"""
    partner_id: str
    nombre: str
    email: str
    telefono: Optional[str]
    direccion: Optional[str]
    estado: EstadoPartner
    estado_anterior: EstadoPartner
    
    def __post_init__(self):
        super().__init__()

@dataclass
class PartnerEliminado(EventoPartner):
    """Evento disparado cuando se elimina un partner"""
    partner_id: str
    nombre: str
    email: str
    fecha_eliminacion: datetime
    
    def __post_init__(self):
        super().__init__()

@dataclass
class KYCVerificado(EventoPartner):
    """Evento disparado cuando se verifica el KYC de un partner"""
    partner_id: str
    estado_kyc_anterior: EstadoKYC
    estado_kyc_nuevo: EstadoKYC
    documentos: Optional[Dict[str, Any]]
    observaciones: Optional[str]
    
    def __post_init__(self):
        super().__init__()

@dataclass
class IntegracionCreada(EventoPartner):
    """Evento disparado cuando se crea una nueva integración"""
    integracion_id: str
    partner_id: str
    tipo: TipoIntegracion
    nombre: str
    descripcion: Optional[str]
    configuracion: Dict[str, Any]
    
    def __post_init__(self):
        super().__init__()

@dataclass
class IntegracionRevocada(EventoPartner):
    """Evento disparado cuando se revoca una integración"""
    integracion_id: str
    partner_id: str
    nombre: str
    fecha_revocacion: datetime
    motivo: Optional[str]
    
    def __post_init__(self):
        super().__init__()
