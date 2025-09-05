
from dataclasses import dataclass, field
from datetime import datetime
from .reglas import IdEntidadEsInmutable
from .excepciones import IdDebeSerInmutableExcepcion
from .mixins import ValidarReglasMixin
import uuid


@dataclass
class Entidad:
    id: uuid.UUID = field(hash=True)
    _id: uuid.UUID = field(init=False, repr=False, hash=True)
    fecha_creacion: datetime = field(default=datetime.now())
    fecha_actualizacion: datetime = field(default=datetime.now())

    @classmethod
    def siguiente_id(cls) -> uuid.UUID:
        return uuid.uuid4()
    
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, valor: uuid.UUID):
        if not IdEntidadEsInmutable(self).es_valido():
            raise IdDebeSerInmutableExcepcion()
        self.id = self.siguiente_id()

@dataclass
class AgregacionRaiz(Entidad, ValidarReglasMixin):
    ...
