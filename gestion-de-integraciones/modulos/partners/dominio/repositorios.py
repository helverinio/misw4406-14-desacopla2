from abc import ABC, abstractmethod
from typing import List, Optional
from .entidades import Partner, Integracion

class RepositorioPartners(ABC):
    """Interfaz del repositorio de Partners"""
    
    @abstractmethod
    def obtener_por_id(self, partner_id: str) -> Optional[Partner]:
        """Obtiene un partner por su ID"""
        pass
    
    @abstractmethod
    def obtener_por_email(self, email: str) -> Optional[Partner]:
        """Obtiene un partner por su email"""
        pass
    
    @abstractmethod
    def guardar(self, partner: Partner) -> Partner:
        """Guarda un partner"""
        pass
    
    @abstractmethod
    def eliminar(self, partner_id: str) -> bool:
        """Elimina un partner"""
        pass
    
    @abstractmethod
    def listar_todos(self) -> List[Partner]:
        """Lista todos los partners"""
        pass

class RepositorioIntegraciones(ABC):
    """Interfaz del repositorio de Integraciones"""
    
    @abstractmethod
    def obtener_por_id(self, integracion_id: str) -> Optional[Integracion]:
        """Obtiene una integración por su ID"""
        pass
    
    @abstractmethod
    def obtener_por_partner(self, partner_id: str) -> List[Integracion]:
        """Obtiene todas las integraciones de un partner"""
        pass
    
    @abstractmethod
    def guardar(self, integracion: Integracion) -> Integracion:
        """Guarda una integración"""
        pass
    
    @abstractmethod
    def eliminar(self, integracion_id: str) -> bool:
        """Elimina una integración"""
        pass
