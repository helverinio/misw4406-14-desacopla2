import logging
import traceback
import json
from alpespartners.modulos.compliance.infraestructura.schema.v1.eventos import EventoContratoCreado
from alpespartners.seedwork.dominio.servicios import ComplianceService
from alpespartners.modulos.compliance.aplicacion.servicios import ComplianceApplicationService
import pulsar, _pulsar
from pulsar.schema import *
from alpespartners.seedwork.infrastructura.utils import broker_url

logger = logging.getLogger(__name__)


# Consumidor de eventos de Pulsar
class PulsarComplianceConsumer:
    def __init__(self, compliance_service: ComplianceService):
        self.compliance_service = compliance_service
        self.cliente = None
    
    def iniciar_consumo(self):
        """
        Inicia el consumo de eventos desde Pulsar
        """
        logger.info("🚀 Iniciando consumidor de eventos de compliance...")
        try:
            self.cliente = pulsar.Client(broker_url())
            
            # Usar BytesSchema para compatibilidad con JSON
            consumidor = self.cliente.subscribe(
                "administracion-financiera-compliance",
                consumer_type=_pulsar.ConsumerType.Shared,
                subscription_name="administracion-financiera-compliance",
                schema=BytesSchema()  # Compatible con JSON de gestion-de-alianzas
            )
            
            logger.info("🎧 Suscrito a eventos de administracion-financiera-compliance")
            
            while True:
                mensaje = consumidor.receive()
                try:
                    # Decodificar mensaje JSON
                    content = mensaje.data().decode('utf-8')
                    logger.info(f"📨 Mensaje recibido: {content}")
                    
                    # Parsear JSON del contrato
                    contrato_data = json.loads(content)
                    logger.info(f"📋 Contrato parseado: {contrato_data}")
                    
                    # Delegar al servicio de dominio
                    self.compliance_service.procesar_contrato(contrato_data)
                    
                    consumidor.acknowledge(mensaje)
                    logger.info("✅ Mensaje procesado exitosamente")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Error parseando JSON: {e}, contenido: {content}")
                    consumidor.negative_acknowledge(mensaje)
                except Exception as e:
                    logger.error(f"❌ Error procesando mensaje: {e}")
                    consumidor.negative_acknowledge(mensaje)
        
        except Exception as e:
            logger.error(f"❌ Error al conectar con el broker: {e}")
            traceback.print_exc()
        finally:
            if self.cliente:
                self.cliente.close()


def suscribirse_a_eventos():
    """
    Función de fábrica que ensambla las dependencias e inicia el consumidor
    """
    # Inyección de dependencias - crear instancias concretas
    compliance_service = ComplianceApplicationService()
    consumer = PulsarComplianceConsumer(compliance_service)
    
    # Iniciar consumo
    consumer.iniciar_consumo()