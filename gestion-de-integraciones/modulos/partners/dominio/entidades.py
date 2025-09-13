from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid

class EstadoPartner(Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    SUSPENDIDO = "SUSPENDIDO"
    ELIMINADO = "ELIMINADO"

class EstadoKYC(Enum):
    PENDIENTE = "PENDIENTE"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    REQUIERE_DOCUMENTOS = "REQUIERE_DOCUMENTOS"

class TipoIntegracion(Enum):
    API = "API"
    WEBHOOK = "WEBHOOK"
    BATCH = "BATCH"
    REAL_TIME = "REAL_TIME"

@dataclass
class Partner:
    """Entidad Partner que representa un socio comercial"""
    id: str
    nombre: str
    email: str
    telefono: Optional[str]
    direccion: Optional[str]
    estado: EstadoPartner
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]
    estado_kyc: EstadoKYC
    documentos_kyc: Optional[dict]
    integraciones: list
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.fecha_creacion:
            self.fecha_creacion = datetime.utcnow()
        if self.integraciones is None:
            self.integraciones = []
    
    def actualizar_estado(self, nuevo_estado: EstadoPartner):
        """Actualiza el estado del partner"""
        self.estado = nuevo_estado
        self.fecha_actualizacion = datetime.utcnow()
    
    def verificar_kyc(self, estado_kyc: EstadoKYC, documentos: Optional[dict] = None):
        """Actualiza el estado KYC del partner"""
        self.estado_kyc = estado_kyc
        if documentos:
            self.documentos_kyc = documentos
        self.fecha_actualizacion = datetime.utcnow()
    
    def agregar_integracion(self, integracion: 'Integracion'):
        """Agrega una nueva integración al partner"""
        self.integraciones.append(integracion)
        self.fecha_actualizacion = datetime.utcnow()
    
    def revocar_integracion(self, integracion_id: str):
        """Revoca una integración específica"""
        for integracion in self.integraciones:
            if integracion.id == integracion_id:
                integracion.revocar()
                self.fecha_actualizacion = datetime.utcnow()
                break
    
    def eliminar(self):
        """Marca el partner como eliminado"""
        self.estado = EstadoPartner.ELIMINADO
        self.fecha_actualizacion = datetime.utcnow()
        # Revocar todas las integraciones
        for integracion in self.integraciones:
            integracion.revocar()

@dataclass
class Integracion:
    """Entidad Integración que representa una integración técnica con un partner"""
    id: str
    partner_id: str
    tipo: TipoIntegracion
    nombre: str
    descripcion: Optional[str]
    configuracion: dict
    activa: bool
    fecha_creacion: datetime
    fecha_revocacion: Optional[datetime]
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.fecha_creacion:
            self.fecha_creacion = datetime.utcnow()
        if self.configuracion is None:
            self.configuracion = {}
    
    def revocar(self):
        """Revoca la integración"""
        self.activa = False
        self.fecha_revocacion = datetime.utcnow()
    
    def activar(self):
        """Activa la integración"""
        self.activa = True
        self.fecha_revocacion = None
