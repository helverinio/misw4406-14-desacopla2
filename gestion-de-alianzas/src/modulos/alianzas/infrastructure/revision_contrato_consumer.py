# revision_contrato_consumer.py

import pulsar
import json
import logging
import asyncio
import os
from typing import Optional

from src.modulos.alianzas.adapters.postgres.contrato_postgres_adapter import PostgresContratoRepository
from src.modulos.alianzas.domain.use_cases.process_revision_contrato_use_case import ProcessRevisionContratoUseCase
from src.modulos.alianzas.infrastructure.db import SessionFactory

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PULSAR_SERVICE_URL = os.getenv('BROKER_URL', 'pulsar://localhost:6650')
TOPIC_REVISION_CONTRATO = 'revision-contrato'


class RevisionContratoConsumer:
    """Consumer de Pulsar para eventos revision-contrato."""

    def __init__(self):
        try:
            logger.info(f"🔌 Connecting RevisionContrato consumer to {PULSAR_SERVICE_URL}")
            self.client = pulsar.Client(PULSAR_SERVICE_URL)
            self.consumer = self.client.subscribe(
                TOPIC_REVISION_CONTRATO, 
                subscription_name='alianzas-revision-contrato-sub',
                schema=pulsar.schema.BytesSchema()
            )
            
            # Inicializar repositorio y caso de uso
            self.contrato_repository = PostgresContratoRepository(SessionFactory)
            self.use_case = ProcessRevisionContratoUseCase(self.contrato_repository)
            
            logger.info(f"✅ RevisionContrato consumer initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize RevisionContrato consumer: {e}")
            raise

    def listen_sync(self):
        """Escucha eventos revision-contrato de forma síncrona."""
        try:
            logger.info(f"📡 Subscribed to topic: {TOPIC_REVISION_CONTRATO}")
            
            # Crear un loop persistente para reutilizar
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                while True:
                    logger.info("⏳ Waiting for revision-contrato messages...")
                    
                    try:
                        # Usar receive sin timeout para bloqueo hasta que llegue un mensaje
                        msg = self.consumer.receive()
                            
                        logger.info(f"📨 Revision-contrato message received, processing...")
                        content = msg.data().decode('utf-8')
                        
                        # Parsear el mensaje JSON
                        try:
                            data = json.loads(content)
                            partner_id = data.get("partner_id")
                            comentarios_revision = data.get("comentarios_revision", "")
                            
                            logger.info(f"📋 Parsed revision data - Partner ID: {partner_id}")
                            logger.info(f"💬 Comments: {comentarios_revision}")
                            
                        except json.JSONDecodeError:
                            logger.error(f"❌ Invalid JSON in revision-contrato message: {content}")
                            self.consumer.negative_acknowledge(msg)
                            continue
                        
                        if not partner_id:
                            logger.error(f"❌ No partner_id found in revision-contrato message: {content}")
                            self.consumer.negative_acknowledge(msg)
                            continue
                        
                        # Procesar la revisión usando el loop persistente
                        resultado = loop.run_until_complete(
                            self.use_case.execute(partner_id, comentarios_revision)
                        )
                        
                        if resultado:
                            logger.info(f"✅ Revision processed successfully for partner: {partner_id}")
                            logger.info(f"📄 Contrato {resultado.id} updated to estado: {resultado.estado}")
                        else:
                            logger.warning(f"⚠️ No contrato found for partner: {partner_id}")
                        
                        # Acknowledge the message
                        self.consumer.acknowledge(msg)
                        
                    except Exception as e:
                        logger.error(f"❌ Error processing revision-contrato message: {e}")
                        if 'msg' in locals():
                            self.consumer.negative_acknowledge(msg)
            finally:
                # Cerrar el loop al finalizar
                loop.close()
                    
        except Exception as e:
            logger.error(f"💥 Fatal error in RevisionContrato consumer loop: {e}")
            raise

    def start_listening(self):
        """Inicia el consumer de forma síncrona."""
        try:
            logger.info("🚀 Starting RevisionContrato consumer...")
            
            # Ejecutar el listener síncrono directamente
            self.listen_sync()
            
        except KeyboardInterrupt:
            logger.info("🛑 RevisionContrato consumer interrupted by user")
        except Exception as e:
            logger.error(f"💥 Unexpected error in RevisionContrato consumer: {e}")
        finally:
            self.close()

    def close(self):
        """Cierra las conexiones del consumer."""
        try:
            if hasattr(self, 'consumer'):
                self.consumer.close()
            if hasattr(self, 'client'):
                self.client.close()
            logger.info("🎧 RevisionContrato consumer closed")
        except Exception as e:
            logger.error(f"❌ Error closing RevisionContrato consumer: {e}")


# Función para ejecutar el consumer
def run_revision_contrato_consumer():
    """Función de utilidad para ejecutar el consumer."""
    consumer = RevisionContratoConsumer()
    consumer.start_listening()


if __name__ == "__main__":
    run_revision_contrato_consumer()