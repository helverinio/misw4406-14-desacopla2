"""Entidad de dominio para el log de eventos de saga."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid

from src.seedwork.dominio.entidades import Entidad

class EstadoEvento(Enum):
    """Estados posibles para el procesamiento de eventos en la saga."""
    RECIBIDO = "RECIBIDO"
    PROCESANDO = "PROCESANDO"
    PROCESADO = "PROCESADO"
    ERROR = "ERROR"


@dataclass
class SagaLog(Entidad):
    """Entidad de dominio que representa un log de evento de saga."""
    
    # Atributos de identidad
    saga_id: str = ""
    
    # Información del evento
    tipo_evento: str = ""
    evento_data: str = ""  # JSON serializado del evento

    # Información de procesamiento
    estado: EstadoEvento = EstadoEvento.RECIBIDO
    timestamp: datetime = datetime.utcnow()

    # Información adicional
    mensaje_error: Optional[str] = None
    intentos: int = 1
    procesado_en: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones post-inicialización."""
        if not self.id:
            self.id = str(uuid.uuid4())
        
        if not self.saga_id:
            raise ValueError("saga_id es requerido")
        
        if not self.tipo_evento:
            raise ValueError("tipo_evento es requerido")
        
        if not self.evento_data:
            raise ValueError("evento_data es requerido")
        
        if not isinstance(self.estado, EstadoEvento):
            raise ValueError("estado debe ser una instancia de EstadoEvento")
    
    def marcar_como_procesando(self) -> None:
        """Marca el evento como en procesamiento."""
        self.estado = EstadoEvento.PROCESANDO
    
    def marcar_como_procesado(self) -> None:
        """Marca el evento como procesado exitosamente."""
        self.estado = EstadoEvento.PROCESADO
        self.procesado_en = datetime.utcnow()
    
    def marcar_como_error(self, mensaje_error: str) -> None:
        """Marca el evento con error."""
        self.estado = EstadoEvento.ERROR
        self.mensaje_error = mensaje_error
        self.intentos += 1
    
    def es_procesable(self) -> bool:
        """Determina si el evento puede ser procesado."""
        return self.estado in [EstadoEvento.RECIBIDO, EstadoEvento.ERROR]
    
    def ha_excedido_intentos(self, max_intentos: int = 3) -> bool:
        """Verifica si ha excedido el número máximo de intentos."""
        return self.intentos > max_intentos