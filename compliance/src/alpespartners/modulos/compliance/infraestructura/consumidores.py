import logging
import traceback
import json
from alpespartners.modulos.compliance.infraestructura.schema.v1.eventos import EventoContratoCreado
from alpespartners.modulos.compliance.aplicacion.comandos.procesar_compliance import ProcesarComplianceContrato
from alpespartners.seedwork.aplicacion.comandos import ejecutar_commando as comando
import pulsar, _pulsar
from pulsar.schema import *
from alpespartners.seedwork.infrastructura.utils import broker_url

logger = logging.getLogger(__name__)


# Consumidor de eventos de Pulsar
class PulsarComplianceConsumer:
    def __init__(self):
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
                    
                    # Crear comando de compliance
                    comando_compliance = self._crear_comando_compliance(contrato_data)
                    
                    # Ejecutar comando usando CQRS
                    comando(comando_compliance)
                    
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

    def _crear_comando_compliance(self, contrato_data: dict) -> ProcesarComplianceContrato:
        return ProcesarComplianceContrato(
            partner_id=contrato_data.get('partner_id'),
            contrato_id=contrato_data.get('id', 'unknown'),
            monto=contrato_data.get('monto', 0),
            moneda=contrato_data.get('moneda', 'USD'),
            estado=contrato_data.get('estado', 'PENDIENTE'),
            tipo=contrato_data.get('tipo'),
            fecha_inicio=contrato_data.get('fecha_inicio'),
            fecha_fin=contrato_data.get('fecha_fin')
        )


def suscribirse_a_eventos():
    consumer = PulsarComplianceConsumer()
    
    # Iniciar consumo
    consumer.iniciar_consumo()