
from abc import ABC, abstractmethod
from alpespartners.seedwork.dominio.repositorio import Repositorio


class RepositorioCompliance(Repositorio, ABC):
    
    @abstractmethod
    def obtener_por_partner_id(self, partner_id: str):
        pass
    
    @abstractmethod
    def actualizar(self, payment) -> None:
        pass