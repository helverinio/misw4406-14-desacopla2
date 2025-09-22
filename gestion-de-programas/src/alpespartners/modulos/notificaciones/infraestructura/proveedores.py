from abc import ABC, abstractmethod
from typing import Optional
import logging


class EmailProvider(ABC):
    """Interfaz abstracta para proveedores de email"""
    
    @abstractmethod
    def enviar_email(self, destinatario: str, asunto: str, contenido: str, 
                    remitente: Optional[str] = None) -> bool:
        """
        Envía un email
        
        Args:
            destinatario: Email del destinatario
            asunto: Asunto del email
            contenido: Contenido del email (HTML o texto plano)
            remitente: Email del remitente (opcional)
            
        Returns:
            bool: True si el email se envió correctamente, False en caso contrario
        """
        pass
    
    @abstractmethod
    def validar_configuracion(self) -> bool:
        """
        Valida la configuración del proveedor de email
        
        Returns:
            bool: True si la configuración es válida, False en caso contrario
        """
        pass


class MockEmailProvider(EmailProvider):
    """Proveedor de email mock para testing"""
    
    def __init__(self):
        self.emails_enviados = []
        self.logger = logging.getLogger(__name__)
    
    def enviar_email(self, destinatario: str, asunto: str, contenido: str, 
                    remitente: Optional[str] = None) -> bool:
        email_data = {
            'destinatario': destinatario,
            'asunto': asunto,
            'contenido': contenido,
            'remitente': remitente
        }
        self.emails_enviados.append(email_data)
        self.logger.info(f"Email mock enviado a {destinatario}: {asunto}")
        return True
    
    def validar_configuracion(self) -> bool:
        return True
    
    def obtener_emails_enviados(self) -> list:
        """Obtiene la lista de emails enviados (solo para testing)"""
        return self.emails_enviados.copy()
    
    def limpiar_emails_enviados(self):
        """Limpia la lista de emails enviados (solo para testing)"""
        self.emails_enviados.clear()
