"""
Eventos de dominio relacionados con Partners para la saga
"""
from dataclasses import dataclass
from datetime import datetime
import uuid

# Importamos desde el seedwork del proyecto
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from seedwork.dominio.eventos import EventoDominio


# Eventos del agregado Partners
@dataclass
class CreatePartner(EventoDominio):
    """Evento que se dispara cuando se necesita crear un partner"""
    partner_id: str = ""

    def __post_init__(self):
        # Inicializar el ID del evento padre
        self._id = self.siguiente_id()


@dataclass 
class PartnerCreated(EventoDominio):
    """Evento que se dispara cuando un partner ha sido creado exitosamente"""
    partner_id: str = ""

    def __post_init__(self):
        self._id = self.siguiente_id()


@dataclass
class PartnerCreationFailed(EventoDominio):
    """Evento que se dispara cuando falla la creación de un partner"""
    partner_id: str = ""
    error_message: str = ""
    
    def __post_init__(self):
        self._id = self.siguiente_id()


@dataclass
class PartnerUpdated(EventoDominio):
    """Evento que se dispara cuando un partner ha sido actualizado"""
    partner_id: str = ""
    updated_fields: str = ""  # JSON string con los campos actualizados
    
    def __post_init__(self):
        self._id = self.siguiente_id()


@dataclass
class PartnerDeleted(EventoDominio):
    """Evento que se dispara cuando un partner ha sido eliminado"""
    partner_id: str = ""
    deletion_reason: str = ""
    
    def __post_init__(self):
        self._id = self.siguiente_id()