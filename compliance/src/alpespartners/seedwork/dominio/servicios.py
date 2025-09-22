"""
Interfaces de servicios de dominio para el seedwork
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class ComplianceService(ABC):
    """
    Interfaz del servicio de dominio para validaciones de compliance
    """
    
    @abstractmethod
    def procesar_contrato(self, contrato_data: Dict[str, Any]) -> None:
        """
        Procesa las validaciones de compliance para un contrato
        
        Args:
            contrato_data: Datos del contrato a validar
            
        Raises:
            ComplianceError: Si las validaciones de compliance fallan
        """
        pass


class NotificationService(ABC):
    """
    Interfaz del servicio de dominio para notificaciones
    """
    
    @abstractmethod
    def enviar_notificacion(self, mensaje: str, destinatario: str) -> None:
        """
        Envía una notificación
        
        Args:
            mensaje: Contenido de la notificación
            destinatario: Destinatario de la notificación
        """
        pass


class AuditService(ABC):
    """
    Interfaz del servicio de dominio para auditoría
    """
    
    @abstractmethod
    def registrar_evento(self, evento: str, datos: Dict[str, Any]) -> None:
        """
        Registra un evento de auditoría
        
        Args:
            evento: Tipo de evento
            datos: Datos del evento
        """
        pass