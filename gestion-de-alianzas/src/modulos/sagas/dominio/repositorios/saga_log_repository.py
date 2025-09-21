"""Repositorio abstracto para el manejo de logs de saga."""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entidades.saga_log import SagaLog, EstadoEvento


class ISagaLogRepository(ABC):
    """Contrato para el repositorio de logs de saga."""
    
    @abstractmethod
    async def agregar(self, saga_log: SagaLog) -> None:
        """Agrega un nuevo log de saga."""
        pass
    
    @abstractmethod
    async def obtener_por_id(self, log_id: str) -> Optional[SagaLog]:
        """Obtiene un log por su ID."""
        pass
    
    @abstractmethod
    async def obtener_por_saga_id(self, saga_id: str) -> List[SagaLog]:
        """Obtiene todos los logs de una saga específica."""
        pass
    
    @abstractmethod
    async def obtener_por_estado(self, estado: EstadoEvento) -> List[SagaLog]:
        """Obtiene logs por estado específico."""
        pass
    
    @abstractmethod
    async def actualizar(self, saga_log: SagaLog) -> None:
        """Actualiza un log existente."""
        pass
    
    @abstractmethod
    async def obtener_eventos_pendientes(self, max_intentos: int = 3) -> List[SagaLog]:
        """Obtiene eventos que pueden ser reprocesados."""
        pass
    
    @abstractmethod
    async def obtener_historial_saga(self, saga_id: str, limit: int = 100) -> List[SagaLog]:
        """Obtiene el historial completo de una saga ordenado por timestamp."""
        pass


# Versión sincronizada para compatibilidad hacia atrás
class ISagaLogRepositorySync(ABC):
    """Contrato sincronizado para el repositorio de logs de saga."""
    
    @abstractmethod
    def agregar(self, saga_log: SagaLog) -> None:
        """Agrega un nuevo log de saga."""
        pass
    
    @abstractmethod
    def obtener_por_id(self, log_id: str) -> Optional[SagaLog]:
        """Obtiene un log por su ID."""
        pass
    
    @abstractmethod
    def obtener_por_saga_id(self, saga_id: str) -> List[SagaLog]:
        """Obtiene todos los logs de una saga específica."""
        pass
    
    @abstractmethod
    def obtener_por_estado(self, estado: EstadoEvento) -> List[SagaLog]:
        """Obtiene logs por estado específico."""
        pass
    
    @abstractmethod
    def actualizar(self, saga_log: SagaLog) -> None:
        """Actualiza un log existente."""
        pass
    
    @abstractmethod
    def obtener_eventos_pendientes(self, max_intentos: int = 3) -> List[SagaLog]:
        """Obtiene eventos que pueden ser reprocesados."""
        pass
    
    @abstractmethod
    def obtener_historial_saga(self, saga_id: str, limit: int = 100) -> List[SagaLog]:
        """Obtiene el historial completo de una saga ordenado por timestamp."""
        pass