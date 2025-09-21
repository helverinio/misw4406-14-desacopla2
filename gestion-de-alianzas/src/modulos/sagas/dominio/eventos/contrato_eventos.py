"""
Eventos de dominio relacionados con Contratos para la saga
"""
from dataclasses import dataclass
from datetime import datetime
import uuid

# Importamos desde el seedwork del proyecto
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from seedwork.dominio.eventos import EventoDominio


# Eventos del agregado Contratos
@dataclass
class ContratoCreado(EventoDominio):
    """Evento que se dispara cuando un contrato ha sido creado exitosamente"""
    partner_id: str = ""
    contrato_id: str = ""
    monto: float = 0.0
    moneda: str = "USD"
    estado: str = "ACTIVO"
    tipo_contrato: str = ""
    fecha_inicio: str = ""
    fecha_fin: str = ""
    
    def __post_init__(self):
        self._id = self.siguiente_id()


@dataclass
class ContratoCreadoFailed(EventoDominio):
    """Evento que se dispara cuando falla la creación de un contrato"""
    partner_id: str = ""
    contrato_id: str = ""
    error_message: str = ""
    error_code: str = ""
    
    def __post_init__(self):
        self._id = self.siguiente_id()


@dataclass
class ContratoActualizado(EventoDominio):
    """Evento que se dispara cuando un contrato ha sido actualizado"""
    partner_id: str = ""
    contrato_id: str = ""
    campos_actualizados: str = ""  # JSON string con los campos actualizados
    version_anterior: str = ""
    
    def __post_init__(self):
        self._id = self.siguiente_id()


@dataclass
class ContratoTerminado(EventoDominio):
    """Evento que se dispara cuando un contrato ha sido terminado"""
    partner_id: str = ""
    contrato_id: str = ""
    motivo_terminacion: str = ""
    fecha_terminacion: str = ""
    
    def __post_init__(self):
        self._id = self.siguiente_id()


@dataclass
class ContratoSuspendido(EventoDominio):
    """Evento que se dispara cuando un contrato ha sido suspendido"""
    partner_id: str = ""
    contrato_id: str = ""
    motivo_suspension: str = ""
    fecha_suspension: str = ""
    
    def __post_init__(self):
        self._id = self.siguiente_id()


@dataclass
class ContratoReactivado(EventoDominio):
    """Evento que se dispara cuando un contrato suspendido ha sido reactivado"""
    partner_id: str = ""
    contrato_id: str = ""
    fecha_reactivacion: str = ""
    
    def __post_init__(self):
        self._id = self.siguiente_id()