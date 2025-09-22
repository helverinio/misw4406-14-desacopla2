"""Servicio de aplicación para gestionar el logging de eventos de saga."""
import json
from datetime import datetime
from typing import Optional, List, Any
import uuid

from ...dominio.entidades.saga_log import SagaLog, EstadoEvento
from ...dominio.repositorios.saga_log_repository import ISagaLogRepository


class SagaLogService:
    """Servicio para gestionar el logging de eventos de saga."""
    
    def __init__(self, saga_log_repository: ISagaLogRepository):
        self.saga_log_repository = saga_log_repository
    
    def registrar_evento_recibido(
        self, 
        saga_id: str, 
        tipo_evento: str, 
        evento_data: Any,
        log_id: Optional[str] = None
    ) -> SagaLog:
        """Registra un nuevo evento recibido por la saga."""
        if not log_id:
            log_id = str(uuid.uuid4())
        
        # Serializar los datos del evento a JSON
        evento_data_json = self._serializar_evento_data(evento_data)
        
        saga_log = SagaLog(
            id=log_id,
            saga_id=saga_id,
            tipo_evento=tipo_evento,
            evento_data=evento_data_json,
            estado=EstadoEvento.RECIBIDO,
            timestamp=datetime.utcnow()
        )
        
        self.saga_log_repository.agregar(saga_log)
        return saga_log
    
    def marcar_evento_procesando(self, log_id: str) -> bool:
        """Marca un evento como en procesamiento."""
        saga_log = self.saga_log_repository.obtener_por_id(log_id)
        if saga_log and saga_log.es_procesable():
            saga_log.marcar_como_procesando()
            self.saga_log_repository.actualizar(saga_log)
            return True
        return False
    
    def marcar_evento_procesado(self, log_id: str) -> bool:
        """Marca un evento como procesado exitosamente."""
        saga_log = self.saga_log_repository.obtener_por_id(log_id)
        if saga_log:
            saga_log.marcar_como_procesado()
            self.saga_log_repository.actualizar(saga_log)
            return True
        return False
    
    def marcar_evento_error(self, log_id: str, mensaje_error: str) -> bool:
        """Marca un evento con error."""
        saga_log = self.saga_log_repository.obtener_por_id(log_id)
        if saga_log:
            saga_log.marcar_como_error(mensaje_error)
            self.saga_log_repository.actualizar(saga_log)
            return True
        return False
    
    def obtener_historial_saga(self, saga_id: str, limit: int = 100) -> List[SagaLog]:
        """Obtiene el historial completo de una saga."""
        return self.saga_log_repository.obtener_historial_saga(saga_id, limit)
    
    def obtener_eventos_pendientes(self, max_intentos: int = 3) -> List[SagaLog]:
        """Obtiene eventos que pueden ser reprocesados."""
        return self.saga_log_repository.obtener_eventos_pendientes(max_intentos)
    
    def obtener_eventos_por_estado(self, estado: EstadoEvento) -> List[SagaLog]:
        """Obtiene eventos por estado específico."""
        return self.saga_log_repository.obtener_por_estado(estado)
    
    def procesar_evento_con_logging(
        saga_id: str, 
        tipo_evento: str, 
        evento_data: Any,
        procesador_callback
    ) -> tuple[bool, Optional[str]]:
        # Registrar evento recibido
        saga_log = self.registrar_evento_recibido(saga_id, tipo_evento, evento_data)
        
        try:
            # Marcar como procesando
            self.marcar_evento_procesando(saga_log.id)
            
            # Ejecutar el procesamiento
            procesador_callback(evento_data)
            
            # Marcar como procesado
            self.marcar_evento_procesado(saga_log.id)
            return True, None
            
        except Exception as e:
            error_msg = f"Error procesando evento {tipo_evento}: {str(e)}"
            self.marcar_evento_error(saga_log.id, error_msg)
            return False, error_msg
    
    def _serializar_evento_data(self, evento_data: Any) -> str:
        """Serializa los datos del evento a JSON."""
        try:
            if hasattr(evento_data, '__dict__'):
                # Si es un objeto, convertir a diccionario
                data_dict = evento_data.__dict__.copy()
                # Convertir datetime a string para serialización
                for key, value in data_dict.items():
                    if isinstance(value, datetime):
                        data_dict[key] = value.isoformat()
                return json.dumps(data_dict, default=str, ensure_ascii=False)
            else:
                return json.dumps(evento_data, default=str, ensure_ascii=False)
        except Exception as e:
            # Si falla la serialización, al menos guardar la representación string
            return str(evento_data)
    
    def deserializar_evento_data(self, evento_data_json: str) -> dict:
        """Deserializa los datos del evento desde JSON."""
        try:
            return json.loads(evento_data_json)
        except json.JSONDecodeError:
            return {"raw_data": evento_data_json}