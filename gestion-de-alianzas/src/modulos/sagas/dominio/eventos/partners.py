"""
Eventos de dominio relacionados con partners para la saga
"""
from dataclasses import dataclass
from datetime import datetime
import uuid

# Importamos desde el seedwork del proyecto
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from seedwork.dominio.eventos import EventoDominio


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