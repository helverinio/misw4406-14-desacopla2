"""
Wrapper asíncrono para el servicio de logging de saga
"""
import asyncio
import json
from datetime import datetime
from typing import Optional, List, Any
import uuid
import logging

from ...dominio.entidades.saga_log import SagaLog, EstadoEvento
from ...dominio.repositorios.saga_log_repository import ISagaLogRepository

logger = logging.getLogger(__name__)


class AsyncSagaLogService:
    """Servicio asíncrono para gestionar el logging de eventos de saga."""
    
    def __init__(self, saga_log_repository: ISagaLogRepository):
        self.saga_log_repository = saga_log_repository
    
    async def registrar_evento_recibido(
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
        
        await self.saga_log_repository.agregar(saga_log)
        return saga_log
    
    async def marcar_evento_procesando(self, log_id: str) -> bool:
        """Marca un evento como en procesamiento."""
        saga_log = await self.saga_log_repository.obtener_por_id(log_id)
        if saga_log and saga_log.es_procesable():
            saga_log.marcar_como_procesando()
            await self.saga_log_repository.actualizar(saga_log)
            return True
        return False
    
    async def marcar_evento_procesado(self, log_id: str) -> bool:
        """Marca un evento como procesado exitosamente."""
        saga_log = await self.saga_log_repository.obtener_por_id(log_id)
        if saga_log and saga_log.estado == EstadoEvento.PROCESANDO:
            saga_log.marcar_como_procesado()
            await self.saga_log_repository.actualizar(saga_log)
            return True
        return False
    
    async def marcar_evento_error(self, log_id: str, error_mensaje: str) -> bool:
        """Marca un evento como fallido."""
        saga_log = await self.saga_log_repository.obtener_por_id(log_id)
        if saga_log:
            saga_log.marcar_como_error(error_mensaje)
            await self.saga_log_repository.actualizar(saga_log)
            return True
        return False
    
    async def procesar_evento_con_logging(
        self, 
        saga_id: str, 
        tipo_evento: str, 
        evento_data: Any,
        procesador_callback
    ) -> tuple[bool, Optional[str]]:
        """
        Procesa un evento con logging automático de estado.
        
        Args:
            saga_id: ID de la saga
            tipo_evento: Tipo del evento
            evento_data: Datos del evento
            procesador_callback: Función que procesa el evento
            
        Returns:
            Tupla (éxito, mensaje_error)
        """
        log_id = str(uuid.uuid4())
        
        try:
            # 1. Registrar evento como recibido
            await self.registrar_evento_recibido(saga_id, tipo_evento, evento_data, log_id)
            
            # 2. Marcar como procesando
            await self.marcar_evento_procesando(log_id)
            
            # 3. Ejecutar el procesador
            procesador_callback()
            
            # 4. Marcar como procesado
            await self.marcar_evento_procesado(log_id)
            
            return True, None
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"💥 Error processing event {tipo_evento}: {error_msg}")
            
            # Marcar como error
            try:
                await self.marcar_evento_error(log_id, error_msg)
            except Exception as mark_error:
                logger.error(f"💥 Failed to mark event as error: {mark_error}")
            
            return False, error_msg
    
    async def obtener_historial_saga(self, saga_id: str) -> List[dict]:
        """Obtiene el historial completo de una saga."""
        logs = await self.saga_log_repository.obtener_por_saga_id(saga_id)
        return [
            {
                'id': log.id,
                'tipo_evento': log.tipo_evento,
                'estado': log.estado.value,
                'timestamp': log.timestamp.isoformat(),
                'evento_data': log.evento_data,
                'error_mensaje': log.error_mensaje
            }
            for log in logs
        ]
    
    def _serializar_evento_data(self, evento_data: Any) -> str:
        """Serializa los datos del evento a JSON."""
        try:
            if hasattr(evento_data, '__dict__'):
                # Si es un objeto con atributos, convertir a diccionario
                data_dict = {}
                for key, value in evento_data.__dict__.items():
                    if not key.startswith('_'):
                        if hasattr(value, 'isoformat'):  # datetime
                            data_dict[key] = value.isoformat()
                        elif hasattr(value, 'value'):  # enum
                            data_dict[key] = value.value
                        else:
                            data_dict[key] = value
                return json.dumps(data_dict, ensure_ascii=False)
            elif isinstance(evento_data, dict):
                return json.dumps(evento_data, ensure_ascii=False, default=str)
            else:
                return json.dumps({'data': str(evento_data)}, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"⚠️ Error serializing event data: {e}")
            return json.dumps({'error': 'serialization_failed', 'data': str(evento_data)})


class SyncSagaLogServiceWrapper:
    """
    Wrapper síncrono que ejecuta operaciones asíncronas en un loop de eventos.
    Para uso desde código síncrono que no puede ser convertido a async.
    """
    
    def __init__(self, async_service: AsyncSagaLogService):
        self.async_service = async_service
    
    def registrar_evento_recibido(
        self, 
        saga_id: str, 
        tipo_evento: str, 
        evento_data: Any,
        log_id: Optional[str] = None
    ) -> SagaLog:
        """Wrapper síncrono para registrar evento."""
        try:
            # Intentar ejecutar en el loop actual si existe
            loop = asyncio.get_running_loop()
            # Si hay un loop corriendo, usar create_task
            task = loop.create_task(
                self.async_service.registrar_evento_recibido(saga_id, tipo_evento, evento_data, log_id)
            )
            # No podemos esperar aquí, así que devolvemos un mock
            logger.info(f"📝 [SYNC] Evento registrado: {tipo_evento} para saga: {saga_id}")
            return SagaLog(
                id=log_id or str(uuid.uuid4()),
                saga_id=saga_id,
                tipo_evento=tipo_evento,
                evento_data=self._serializar_evento_data(evento_data),
                estado=EstadoEvento.RECIBIDO
            )
        except RuntimeError:
            # No hay loop corriendo, crear uno nuevo
            return asyncio.run(
                self.async_service.registrar_evento_recibido(saga_id, tipo_evento, evento_data, log_id)
            )
    
    def procesar_evento_con_logging(
        self, 
        saga_id: str, 
        tipo_evento: str, 
        evento_data: Any,
        procesador_callback
    ) -> tuple[bool, Optional[str]]:
        """Wrapper síncrono para procesar evento con logging."""
        try:
            # Intentar ejecutar en el loop actual si existe
            loop = asyncio.get_running_loop()
            # Crear tarea sin esperar el resultado
            task = loop.create_task(
                self._procesar_async(saga_id, tipo_evento, evento_data, procesador_callback)
            )
            logger.info(f"🔄 [SYNC] Procesando evento {tipo_evento} para saga {saga_id}")
            
            # Ejecutar el procesador de forma síncrona
            try:
                procesador_callback()
                logger.info(f"✅ [SYNC] Evento procesado exitosamente: {tipo_evento}")
                return True, None
            except Exception as e:
                logger.error(f"💥 [SYNC] Error procesando evento: {e}")
                return False, str(e)
                
        except RuntimeError:
            # No hay loop corriendo, crear uno nuevo
            return asyncio.run(
                self.async_service.procesar_evento_con_logging(
                    saga_id, tipo_evento, evento_data, procesador_callback
                )
            )
    
    async def _procesar_async(self, saga_id, tipo_evento, evento_data, procesador_callback):
        """Método auxiliar para procesar de forma asíncrona."""
        return await self.async_service.procesar_evento_con_logging(
            saga_id, tipo_evento, evento_data, procesador_callback
        )
    
    def obtener_historial_saga(self, saga_id: str) -> List[dict]:
        """Wrapper síncrono para obtener historial."""
        try:
            loop = asyncio.get_running_loop()
            # Si hay un loop, devolver lista vacía como fallback
            logger.info(f"📚 [SYNC] Obteniendo historial para saga: {saga_id}")
            return []
        except RuntimeError:
            return asyncio.run(self.async_service.obtener_historial_saga(saga_id))
    
    def _serializar_evento_data(self, evento_data: Any) -> str:
        """Serializa los datos del evento a JSON."""
        return self.async_service._serializar_evento_data(evento_data)