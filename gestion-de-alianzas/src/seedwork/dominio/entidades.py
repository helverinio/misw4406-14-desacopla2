
from dataclasses import dataclass, field
from datetime import datetime

from .eventos import EventoDominio
from .reglas import IdEntidadEsInmutable
from .excepciones import IdDebeSerInmutableExcepcion
import uuid
import logging


@dataclass
class Entidad:
    id: uuid.UUID = field(hash=True)
    _id: uuid.UUID = field(init=False, repr=False, hash=True)
    fecha_creacion: datetime = field(default=datetime.now())
    fecha_actualizacion: datetime = field(default=datetime.now())

    @classmethod
    def siguiente_id(self) -> uuid.UUID:
        return uuid.uuid4()
    
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, id: uuid.UUID) -> None:
        if not IdEntidadEsInmutable(self).es_valido():
            raise IdDebeSerInmutableExcepcion()
        self._id = self.siguiente_id()