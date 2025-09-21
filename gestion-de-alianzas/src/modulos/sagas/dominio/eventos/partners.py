"""
Eventos de dominio relacionados con partners y contratos para la saga
"""
from dataclasses import dataclass
from datetime import datetime
import uuid

# Importamos desde el seedwork del proyecto
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from seedwork.dominio.eventos import EventoDominio


# Eventos de Partners
@dataclass
class CreatePartner(EventoDominio):
    partner_id: str = ""

    def __post_init__(self):
        # Inicializar el ID del evento padre
        self._id = self.siguiente_id()


@dataclass 
class PartnerCreated(EventoDominio):
    partner_id: str = ""

    def __post_init__(self):
        self._id = self.siguiente_id()


@dataclass
class PartnerCreationFailed(EventoDominio):
    partner_id: str = ""
    error_message: str = ""
    
    def __post_init__(self):
        self._id = self.siguiente_id()


# Eventos de Contratos
@dataclass
class ContratoCreado(EventoDominio):
    """Evento que se dispara cuando un contrato ha sido creado"""
    partner_id: str = ""
    contrato_id: str = ""
    monto: float = 0.0
    moneda: str = "USD"
    estado: str = "ACTIVO"
    
    def __post_init__(self):
        self._id = self.siguiente_id()


@dataclass
class ContratoCreadoFailed(EventoDominio):
    """Evento que se dispara cuando falla la creación de un contrato"""
    partner_id: str = ""
    contrato_id: str = ""
    error_message: str = ""
    
    def __post_init__(self):
        self._id = self.siguiente_id()