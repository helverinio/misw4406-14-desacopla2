"""
Listener para eventos de Pulsar relacionados con la saga de partners
"""
import pulsar
import json
import logging
from datetime import datetime
import asyncio
import os
import sys

# Agregar paths para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from modulos.sagas.dominio.eventos.partners import CreatePartner
from modulos.sagas.aplicacion.coordinadores.saga_partners import CoordinadorPartners

# Configurar logging
logger = logging.getLogger(__name__)

class PulsarSagaListener:
    
    def __init__(self, pulsar_url: str = None):
        self.pulsar_url = pulsar_url or os.getenv('BROKER_URL', 'pulsar://localhost:6650')
        self.topic = 'PartnerCreado'  # Topic específico para eventos PartnerCreado
        self.subscription_name = 'saga-partners-subscription'
        self.client = None
        self.consumer = None
        
    def connect(self):
        try:
            logger.info(f"🔌 Connecting to Pulsar at {self.pulsar_url}")
            self.client = pulsar.Client(self.pulsar_url)
            self.consumer = self.client.subscribe(
                self.topic, 
                subscription_name=self.subscription_name,
                schema=pulsar.schema.BytesSchema()
            )
            logger.info(f"✅ Pulsar saga listener connected successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Pulsar: {e}")
            raise
    
    def process_message(self, msg_data: bytes) -> CreatePartner:
        try:
            # Decodificar el mensaje
            content = msg_data.decode('utf-8')
            logger.info(f"📨 Received raw message: {content}")
            
            # Intentar parsear como JSON
            try:
                data = json.loads(content)
                partner_id = data.get("partner_id")
                if not partner_id:
                    # Si no hay partner_id en JSON, usar todo el contenido
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
            
            # Crear el evento de dominio
            evento = CreatePartner(partner_id=partner_id)
            
            logger.info(f"✨ Created CreatePartner event for partner_id: {partner_id}")
            return evento
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            raise
    
    def listen(self):
        if not self.consumer:
            self.connect()
            
        logger.info(f"📡 Starting to listen for CreatePartner events on topic: {self.topic}")
        
        try:
            while True:
                logger.info("⏳ Waiting for CreatePartner messages...")
                msg = self.consumer.receive()
                
                try:
                    # Procesar el mensaje y crear evento de dominio
                    evento = self.process_message(msg.data())
                    
                    # Iniciar la saga con el evento
                    coordinador = CoordinadorPartners()
                    coordinador.procesar_evento(evento)
                    
                    # Confirmar el mensaje
                    self.consumer.acknowledge(msg)
                    logger.info(f"✅ Successfully processed CreatePartner event for partner: {evento.partner_id}")
                    
                except Exception as e:
                    logger.error(f'❌ Error processing CreatePartner message: {e}')
                    self.consumer.negative_acknowledge(msg)
                    
        except Exception as e:
            logger.error(f'💥 Fatal error in saga listener: {e}')
            raise
    
    def close(self):
        """Cierra las conexiones de Pulsar"""
        if self.client:
            self.client.close()
            logger.info("📡 Pulsar saga listener closed")


def iniciar_listener():
    """Función helper para iniciar el listener"""
    listener = PulsarSagaListener()
    try:
        listener.listen()
    except KeyboardInterrupt:
        logger.info("🛑 Saga listener stopped by user")
    finally:
        listener.close()


if __name__ == "__main__":
    iniciar_listener()