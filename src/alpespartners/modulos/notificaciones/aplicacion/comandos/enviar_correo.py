from dataclasses import dataclass, field
from typing import Optional
import logging
import uuid
from datetime import datetime

from alpespartners.seedwork.aplicacion.dto import DTO
from alpespartners.modulos.notificaciones.infraestructura.fabricas import FabricaEmailProviders
from alpespartners.modulos.notificaciones.infraestructura.proveedores import EmailProvider


@dataclass(frozen=True)
class EnviarCorreoCommand(DTO):
    """Command para enviar un correo electrónico"""
    
    # Identificadores
    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fecha_creacion: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Datos del email
    destinatario: str = field(default_factory=str)
    asunto: str = field(default_factory=str)
    contenido: str = field(default_factory=str)
    remitente: Optional[str] = field(default=None)
    
    # Configuración del proveedor
    tipo_proveedor: str = field(default="mock")
    
    # Metadatos
    prioridad: str = field(default="normal")  # normal, alta, baja
    intentos_maximos: int = field(default=3)
    timeout_segundos: int = field(default=30)


class EnviarCorreoCommandHandler:
    """Handler para procesar el comando EnviarCorreoCommand"""
    
    def __init__(self):
        self._fabrica_proveedores = FabricaEmailProviders()
        self.logger = logging.getLogger(__name__)
    
    @property
    def fabrica_proveedores(self) -> FabricaEmailProviders:
        return self._fabrica_proveedores
    
    def ejecutar(self, command: EnviarCorreoCommand) -> dict:
        """
        Ejecuta el comando para enviar un correo electrónico
        
        Args:
            command: Comando con los datos del email a enviar
            
        Returns:
            dict: Resultado de la ejecución del comando
        """
        try:
            self.logger.info(f"Iniciando envío de email - Command ID: {command.command_id}")
            
            # Validar el comando
            self._validar_comando(command)
            
            # Crear el proveedor de email
            proveedor = self._crear_proveedor(command)
            
            # Validar configuración del proveedor
            if not proveedor.validar_configuracion():
                raise Exception("Configuración del proveedor de email inválida")
            
            # Enviar el email
            resultado_envio = self._enviar_email(proveedor, command)
            
            # Preparar respuesta
            resultado = {
                "command_id": command.command_id,
                "exitoso": resultado_envio,
                "fecha_ejecucion": datetime.now().isoformat(),
                "destinatario": command.destinatario,
                "asunto": command.asunto,
                "tipo_proveedor": command.tipo_proveedor,
                "mensaje": "Email enviado exitosamente" if resultado_envio else "Error al enviar email"
            }
            
            if resultado_envio:
                self.logger.info(f"Email enviado exitosamente - Command ID: {command.command_id}")
            else:
                self.logger.error(f"Error al enviar email - Command ID: {command.command_id}")
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error ejecutando comando EnviarCorreo - Command ID: {command.command_id}, Error: {str(e)}")
            return {
                "command_id": command.command_id,
                "exitoso": False,
                "fecha_ejecucion": datetime.now().isoformat(),
                "destinatario": command.destinatario,
                "asunto": command.asunto,
                "tipo_proveedor": command.tipo_proveedor,
                "mensaje": f"Error: {str(e)}"
            }
    
    def _validar_comando(self, command: EnviarCorreoCommand) -> None:
        """Valida que el comando tenga todos los datos necesarios"""
        if not command.destinatario or not command.destinatario.strip():
            raise ValueError("El destinatario es requerido")
        
        if not command.asunto or not command.asunto.strip():
            raise ValueError("El asunto es requerido")
        
        if not command.contenido or not command.contenido.strip():
            raise ValueError("El contenido es requerido")
        
        # Validar formato de email básico
        if "@" not in command.destinatario:
            raise ValueError("El destinatario debe ser un email válido")
        
        if command.remitente and "@" not in command.remitente:
            raise ValueError("El remitente debe ser un email válido")
    
    def _crear_proveedor(self, command: EnviarCorreoCommand) -> EmailProvider:
        """Crea el proveedor de email según la configuración del comando"""
        try:
            return self.fabrica_proveedores.crear_objeto(command.tipo_proveedor)
        except Exception as e:
            self.logger.error(f"Error creando proveedor {command.tipo_proveedor}: {str(e)}")
            # Fallback a mock si hay error
            self.logger.info("Usando proveedor mock como fallback")
            return self.fabrica_proveedores.crear_objeto("mock")
    
    def _enviar_email(self, proveedor: EmailProvider, command: EnviarCorreoCommand) -> bool:
        """Envía el email usando el proveedor especificado"""
        intentos = 0
        max_intentos = command.intentos_maximos
        
        while intentos < max_intentos:
            try:
                intentos += 1
                self.logger.info(f"Intento {intentos}/{max_intentos} de envío de email")
                
                resultado = proveedor.enviar_email(
                    destinatario=command.destinatario,
                    asunto=command.asunto,
                    contenido=command.contenido,
                    remitente=command.remitente
                )
                
                if resultado:
                    return True
                else:
                    self.logger.warning(f"Intento {intentos} falló, reintentando...")
                    
            except Exception as e:
                self.logger.error(f"Error en intento {intentos}: {str(e)}")
                if intentos >= max_intentos:
                    raise e
        
        return False


# Función de conveniencia para crear y ejecutar el comando
def enviar_correo(destinatario: str, asunto: str, contenido: str, 
                 remitente: Optional[str] = None, 
                 tipo_proveedor: str = "mock") -> dict:
    """
    Función de conveniencia para enviar un correo electrónico
    
    Args:
        destinatario: Email del destinatario
        asunto: Asunto del email
        contenido: Contenido del email
        remitente: Email del remitente (opcional)
        tipo_proveedor: Tipo de proveedor a usar (default: "mock")
        
    Returns:
        dict: Resultado de la ejecución
    """
    command = EnviarCorreoCommand(
        destinatario=destinatario,
        asunto=asunto,
        contenido=contenido,
        remitente=remitente,
        tipo_proveedor=tipo_proveedor
    )
    
    handler = EnviarCorreoCommandHandler()
    return handler.ejecutar(command)
