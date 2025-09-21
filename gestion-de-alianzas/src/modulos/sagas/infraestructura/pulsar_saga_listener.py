"""
Listener para eventos de Pulsar relacionados con la saga coreográfica de partners
"""
import pulsar
import json
import logging
from datetime import datetime
import asyncio
import os
import sys
import threading

# Agregar paths para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from modulos.sagas.dominio.eventos import (
    CreatePartner, PartnerCreated, PartnerCreationFailed,
    ContratoCreado, ContratoCreadoFailed
)
from modulos.sagas.aplicacion.coordinadores.saga_partners import CoordinadorPartnersCoreografico

# Configurar logging
logger = logging.getLogger(__name__)

class PulsarSagaChoreographyListener:
    """
    Listener que escucha múltiples eventos desde Pulsar para la saga coreográfica
    Escucha: CreatePartner, PartnerCreated, PartnerCreationFailed, ContratoCreado, ContratoCreadoFailed
    """
    
    def __init__(self, pulsar_url: str = None):
        self.pulsar_url = pulsar_url or os.getenv('BROKER_URL', 'pulsar://localhost:6650')
        
        # Mapeo de tópicos a tipos de eventos
        self.topics = {
            'PartnerCreado': CreatePartner,  # Topic que inicia la saga
            'ContratoCreado': ContratoCreado,  # Topic del compliance service
            # Puedes agregar más topics aquí para otros eventos
        }
        
        self.subscription_prefix = 'saga-choreography'
        self.client = None
        self.consumers = {}

        self.coordinador = CoordinadorPartnersCoreografico()

    def connect(self):
        """Conecta al broker de Pulsar y crea consumers para todos los tópicos"""
        try:
            logger.info(f"🔌 Connecting to Pulsar at {self.pulsar_url}")
            self.client = pulsar.Client(self.pulsar_url)
            
            for topic, event_type in self.topics.items():
                consumer = self.client.subscribe(
                    topic,
                    subscription_name=f"{self.subscription_prefix}-{topic}",
                    schema=pulsar.schema.BytesSchema()
                )
                self.consumers[topic] = consumer
                logger.info(f"✅ Subscribed to topic: {topic} for event: {event_type.__name__}")
                
            logger.info(f"✅ Pulsar choreography listener connected successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Pulsar: {e}")
            raise
    
    def process_message(self, topic: str, msg_data: bytes):
        """
        Procesa el mensaje recibido de Pulsar y lo convierte en evento de dominio
        """
        try:
            # Decodificar el mensaje
            content = msg_data.decode('utf-8')
            logger.info(f"📨 Received message from topic {topic}: {content}")
            
            evento = None
            
            if topic == 'PartnerCreado':
                evento = self._process_partner_created_message(content)
            elif topic == 'ContratoCreado':
                evento = self._process_contrato_creado_message(content)
            
            if evento:
                logger.info(f"✨ Created event: {type(evento).__name__} for partner_id: {evento.partner_id}")
                return evento
            else:
                raise ValueError(f"No se pudo crear evento para topic {topic} con contenido: {content}")
                
        except Exception as e:
            logger.error(f"❌ Error processing message from topic {topic}: {e}")
            raise
    
    def _process_partner_created_message(self, content: str) -> CreatePartner:
        """Procesa mensajes del topic PartnerCreado y crea eventos CreatePartner"""
        try:
            # Intentar parsear como JSON
            try:
                data = json.loads(content)
                partner_id = data.get("partner_id")
                if not partner_id:
                    partner_id = str(data)
            except json.JSONDecodeError:
                # Si no es JSON válido, limpiar el contenido
                clean_content = ''.join(char for char in content if char.isprintable())
                logger.info(f'📥 Cleaned content: {clean_content}')
                
                # Manejar el prefijo 'H' como en el consumer existente
                if clean_content and clean_content[0] == 'H':
                    partner_id = clean_content[1:]  # Remover el prefijo 'H'
                    logger.info(f'📥 Extracted partner_id from prefixed message: {partner_id}')
                else:
                    partner_id = clean_content
                    logger.info(f'📥 Using content as partner_id: {partner_id}')
            
            if not partner_id:
                raise ValueError(f"No se pudo extraer partner_id del mensaje: {content}")
            
            return CreatePartner(partner_id=partner_id)
            
        except Exception as e:
            logger.error(f"❌ Error processing PartnerCreado message: {e}")
            raise
    
    def _process_contrato_creado_message(self, content: str) -> ContratoCreado:
        """Procesa mensajes del topic ContratoCreado"""
        try:
            # Parsear JSON del contrato
            contrato_data = json.loads(content)
            logger.info(f"📋 Contrato data parsed: {contrato_data}")
            
            return ContratoCreado(
                partner_id=contrato_data.get('partner_id', ''),
                contrato_id=contrato_data.get('id', 'unknown'),
                monto=contrato_data.get('monto', 0.0),
                moneda=contrato_data.get('moneda', 'USD'),
                estado=contrato_data.get('estado', 'ACTIVO')
            )
            
        except Exception as e:
            logger.error(f"❌ Error processing ContratoCreado message: {e}")
            raise
    
    def listen_topic(self, topic: str):
        """
        Escucha continuamente un tópico específico
        """
        consumer = self.consumers[topic]
        logger.info(f"📡 Starting to listen for events on topic: {topic}")
        
        try:
            while True:
                logger.info(f"⏳ Waiting for messages on topic {topic}...")
                msg = consumer.receive()
                
                try:
                    # Procesar el mensaje y crear evento de dominio
                    evento = self.process_message(topic, msg.data())
                    
                    # Procesar el evento en la saga coreográfica
                    self.coordinador.procesar_evento(evento)
                    
                    # Confirmar el mensaje
                    consumer.acknowledge(msg)
                    logger.info(f"✅ Successfully processed event from topic {topic}")
                    
                except Exception as e:
                    logger.error(f'❌ Error processing message from topic {topic}: {e}')
                    consumer.negative_acknowledge(msg)
                    
        except Exception as e:
            logger.error(f'💥 Fatal error in listener for topic {topic}: {e}')
            raise
    
    def listen(self):
        """
        Escucha todos los tópicos en threads separados
        """
        if not self.consumers:
            self.connect()
        
        logger.info(f"🎭 Starting choreography listener for topics: {list(self.topics.keys())}")
        
        # Crear un thread para cada tópico
        threads = []
        for topic in self.topics.keys():
            thread = threading.Thread(target=self.listen_topic, args=(topic,), daemon=True)
            thread.start()
            threads.append(thread)
            logger.info(f"🧵 Started thread for topic: {topic}")
        
        # Mantener el proceso principal vivo
        try:
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            logger.info("🛑 Choreography listener stopped by user")
    
    def close(self):
        """Cierra las conexiones de Pulsar"""
        if self.client:
            self.client.close()
            logger.info("📡 Pulsar choreography listener closed")


def iniciar_listener():
    """Función helper para iniciar el listener coreográfico"""
    listener = PulsarSagaChoreographyListener()
    try:
        listener.listen()
    except KeyboardInterrupt:
        logger.info("🛑 Choreography saga listener stopped by user")
    finally:
        listener.close()


if __name__ == "__main__":
    iniciar_listener()