
from abc import ABC, abstractmethod
from uuid import UUID
from .entidades import Entidad


class Repositorio(ABC):
    @abstractmethod
    def obtener_por_id(self, id: UUID) -> Entidad:
        ...