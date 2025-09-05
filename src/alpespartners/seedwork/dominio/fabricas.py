from abc import ABC, abstractmethod
from .mixins import ValidarReglasMixin


class Fabrica(ABC, ValidarReglasMixin):
    @abstractmethod
    def crear_objeto(self,obj: any, mapeador: Mapeador = None) -> any:
        ...