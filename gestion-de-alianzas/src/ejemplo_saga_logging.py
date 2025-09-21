"""
Ejemplo de uso del sistema de logging de saga.
Este archivo demuestra cómo se integra el logging en la saga coreográfica.
"""
import sys
import os
import logging
import asyncio
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Simular los eventos y dependencias para el ejemplo
class MockEvent:
    def __init__(self, partner_id: str, event_type: str):
        self.partner_id = partner_id
        self.event_type = event_type
        self.timestamp = datetime.utcnow()

class MockSagaLogService:
    """Mock del servicio de logging para demostración."""
    def __init__(self):
        self.logs = []
    
    def registrar_evento_recibido(self, saga_id: str, tipo_evento: str, evento_data):
        log_entry = {
            'saga_id': saga_id,
            'tipo_evento': tipo_evento,
            'evento_data': str(evento_data),
            'timestamp': datetime.utcnow(),
            'estado': 'RECIBIDO'
        }
        self.logs.append(log_entry)
        logger.info(f"📝 [SAGA_LOG] Evento registrado: {tipo_evento} para saga: {saga_id}")
        return log_entry
    
    def procesar_evento_con_logging(self, saga_id: str, tipo_evento: str, evento_data, procesador_callback):
        """Simula el procesamiento con logging automático."""
        logger.info(f"🔄 [SAGA_LOG] Iniciando procesamiento de {tipo_evento}")
        
        # Registrar como procesando
        log_entry = self.registrar_evento_recibido(saga_id, tipo_evento, evento_data)
        log_entry['estado'] = 'PROCESANDO'
        
        try:
            # Ejecutar el procesador
            procesador_callback()
            
            # Marcar como procesado
            log_entry['estado'] = 'PROCESADO'
            log_entry['procesado_en'] = datetime.utcnow()
            logger.info(f"✅ [SAGA_LOG] Evento procesado exitosamente: {tipo_evento}")
            return True, None
            
        except Exception as e:
            # Marcar como error
            log_entry['estado'] = 'ERROR'
            log_entry['mensaje_error'] = str(e)
            logger.error(f"❌ [SAGA_LOG] Error procesando evento: {e}")
            return False, str(e)
    
    def obtener_historial_saga(self, saga_id: str):
        """Obtiene el historial de logs para una saga."""
        return [log for log in self.logs if log['saga_id'] == saga_id]


def ejemplo_saga_con_logging():
    """Ejemplo de uso del sistema de logging en la saga."""
    
    logger.info("🚀 === EJEMPLO DE SAGA CON LOGGING ===")
    
    # Crear el servicio de logging mock
    saga_log_service = MockSagaLogService()
    
    # Simular eventos de la saga
    partner_id = "partner-123"
    saga_id = f"saga-{partner_id}"
    
    # Evento 1: CreatePartner
    def procesar_create_partner():
        logger.info(f"🎯 Procesando CreatePartner para partner: {partner_id}")
        # Aquí iría la lógica de procesamiento real
        pass
    
    evento1 = MockEvent(partner_id, "CreatePartner")
    exito1, error1 = saga_log_service.procesar_evento_con_logging(
        saga_id=saga_id,
        tipo_evento="CreatePartner",
        evento_data=evento1,
        procesador_callback=procesar_create_partner
    )
    
    # Evento 2: PartnerCreated
    def procesar_partner_created():
        logger.info(f"✅ Procesando PartnerCreated para partner: {partner_id}")
        # Aquí iría la lógica de procesamiento real
        pass
    
    evento2 = MockEvent(partner_id, "PartnerCreated")
    exito2, error2 = saga_log_service.procesar_evento_con_logging(
        saga_id=saga_id,
        tipo_evento="PartnerCreated",
        evento_data=evento2,
        procesador_callback=procesar_partner_created
    )
    
    # Evento 3: ContratoCreado
    def procesar_contrato_creado():
        logger.info(f"📄 Procesando ContratoCreado para partner: {partner_id}")
        # Aquí iría la lógica de procesamiento real
        pass
    
    evento3 = MockEvent(partner_id, "ContratoCreado")
    exito3, error3 = saga_log_service.procesar_evento_con_logging(
        saga_id=saga_id,
        tipo_evento="ContratoCreado",
        evento_data=evento3,
        procesador_callback=procesar_contrato_creado
    )
    
    # Mostrar historial de la saga
    logger.info("📚 === HISTORIAL DE LA SAGA ===")
    historial = saga_log_service.obtener_historial_saga(saga_id)
    for i, log in enumerate(historial, 1):
        logger.info(f"  {i}. {log['tipo_evento']} - {log['estado']} - {log['timestamp']}")
    
    logger.info("🎉 === EJEMPLO COMPLETADO ===")


def ejemplo_coordinador_con_logging():
    """Ejemplo de cómo el coordinador usa el servicio de logging."""
    
    logger.info("🎭 === COORDINADOR CON LOGGING ===")
    
    class MockCoordinador:
        def __init__(self, saga_log_service):
            self.saga_log_service = saga_log_service
            self.estado_saga = {}
        
        def iniciar(self, partner_id: str):
            saga_id = f"saga-{partner_id}"
            logger.info(f"🚀 Iniciando saga para partner: {partner_id}")
            
            self.estado_saga[partner_id] = {
                'saga_id': saga_id,
                'estado': 'INICIADA'
            }
            
            # Registrar inicio de saga
            if self.saga_log_service:
                self.saga_log_service.registrar_evento_recibido(
                    saga_id=saga_id,
                    tipo_evento="SAGA_INICIADA",
                    evento_data={"partner_id": partner_id, "action": "saga_start"}
                )
        
        def procesar_evento(self, evento):
            partner_id = evento.partner_id
            saga_id = self.estado_saga[partner_id]['saga_id']
            
            def procesador():
                logger.info(f"🎯 Procesando evento {evento.event_type}")
                # Lógica de procesamiento específica del evento
                if evento.event_type == "CreatePartner":
                    logger.info("  → Iniciando creación de partner")
                elif evento.event_type == "PartnerCreated":
                    logger.info("  → Partner creado exitosamente")
                elif evento.event_type == "ContratoCreado":
                    logger.info("  → Contrato creado exitosamente")
            
            # Usar el servicio de logging
            exito, error = self.saga_log_service.procesar_evento_con_logging(
                saga_id=saga_id,
                tipo_evento=evento.event_type,
                evento_data=evento,
                procesador_callback=procesador
            )
            
            if not exito:
                logger.error(f"💥 Error en coordinador: {error}")
            
            return exito
    
    # Ejemplo de uso
    saga_log_service = MockSagaLogService()
    coordinador = MockCoordinador(saga_log_service)
    
    partner_id = "partner-456"
    coordinador.iniciar(partner_id)
    
    # Procesar eventos
    eventos = [
        MockEvent(partner_id, "CreatePartner"),
        MockEvent(partner_id, "PartnerCreated"),
        MockEvent(partner_id, "ContratoCreado")
    ]
    
    for evento in eventos:
        coordinador.procesar_evento(evento)
    
    # Mostrar logs
    historial = saga_log_service.obtener_historial_saga(f"saga-{partner_id}")
    logger.info(f"📊 Total de eventos logueados: {len(historial)}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("DEMOSTRACIÓN DEL SISTEMA DE LOGGING DE SAGA")
    print("="*60)
    
    ejemplo_saga_con_logging()
    print("\n" + "-"*60)
    ejemplo_coordinador_con_logging()
    
    print("\n" + "="*60)
    print("CARACTERÍSTICAS IMPLEMENTADAS:")
    print("✅ Entidad de dominio SagaLog")
    print("✅ Repositorio abstracto ISagaLogRepository")
    print("✅ Implementación concreta con SQLAlchemy async")
    print("✅ Modelo de base de datos con índices optimizados")
    print("✅ Servicio de aplicación SagaLogService")
    print("✅ Integración en coordinador de saga coreográfico")
    print("✅ Logging automático con manejo de errores")
    print("✅ Seguimiento completo del estado de eventos")
    print("✅ Separación por capas siguiendo DDD")
    print("="*60)