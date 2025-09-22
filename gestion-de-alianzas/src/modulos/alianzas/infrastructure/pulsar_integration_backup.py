import pulsar
impPULSAR_SERVICE_URL = os.getenv('BROKER_URL', 'pulsar://localhost:6650')
TOPIC = 'gestion-de-integraciones'
TOPIC_PARTNERCREADO = 'PartnerCreated'json
from src.modulos.alianzas.domain.models.contrato import Contrato  # BaseModel
from src.modulos.alianzas.infrastructure.models import ContratoRow  # DB row
from src.modulos.alianzas.adapters.postgres.contrato_postgres_adapter import PostgresContratoRepository
from datetime import date, datetime
from src.modulos.alianzas.domain.models.contrato import TipoContrato, EstadoContrato
from src.modulos.alianzas.domain.use_cases.create_contrato_use_case import CreateContratoUseCase
from src.assembly import build_create_contrato_use_case
import os
import asyncio
import random, uuid
import logging

# Configurar logging para este módulo
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PULSAR_SERVICE_URL = os.getenv('BROKER_URL', 'pulsar://localhost:6650')
TOPIC = 'gestion-de-integraciones'
TOPIC_PARTNERCREADO = 'PartnerCreado'
TOPIC_REVISION_CONTRATO = 'revision-contrato'

# Publisher
class PulsarContratoPublisher:
    def __init__(self):
        try:
            logger.info(f"🔌 Connecting to Pulsar at {PULSAR_SERVICE_URL}")
            self.client = pulsar.Client(PULSAR_SERVICE_URL)
            self.producer = self.client.create_producer(TOPIC)
            logger.info(f"✅ Pulsar publisher connected successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Pulsar publisher: {e}")
            raise

    def publish_contrato(self, contrato: Contrato):
        data = contrato.model_dump() if hasattr(contrato, 'model_dump') else contrato.dict()
        logger.info(f'📤 Publishing contrato: {data}')
        self.producer.send(json.dumps(data).encode('utf-8'))

    def close(self):
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("📡 Pulsar publisher closed")

# Consumer
class PulsarContratoConsumer:
    def __init__(self):
        try:
            logger.info(f"🔌 Connecting Pulsar consumer to {PULSAR_SERVICE_URL}")
            self.client = pulsar.Client(PULSAR_SERVICE_URL)
            self.consumer = self.client.subscribe(TOPIC_PARTNERCREADO, subscription_name='contrato-sub')
            self.use_case = build_create_contrato_use_case()
            logger.info(f"✅ Pulsar consumer initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Pulsar consumer: {e}")
            raise

    def listen(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            logger.info(f"📡 Subscribed to topic: {TOPIC_PARTNERCREADO}")

            while True:
                logger.info("⏳ Waiting for messages...")
                msg = self.consumer.receive()
                try:
                    logger.info(f"📨 Message received, processing...")
                    content = msg.data().decode('utf-8')
                    
                    # Try to parse as JSON first, if fails assume it's just the partner_id
                    try:
                        data = json.loads(content)
                        partner_id = data.get("partner_id")
                    except json.JSONDecodeError:
                        raw_content = content.strip()
                        
                        clean_content = ''.join(char for char in raw_content if char.isprintable())
                        logger.info(f'📥 Cleaned content: {clean_content}')
                        
                        if clean_content and clean_content[0] == 'H':
                            partner_id = clean_content[1:]  # Remove the 'H' prefix
                            logger.info(f'📥 Extracted partner_id from prefixed message: {partner_id}')
                        else:
                            partner_id = clean_content
                            logger.info(f'📥 Plain text partner_id: {partner_id}')
                    
                    if not partner_id:
                        error_msg = f"❌ No partner_id found in message: {content}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    
                    tipos = list(TipoContrato)
                    estados = list(EstadoContrato)
                    monedas = ["USD", "EUR", "COP", "MXN"]
                    condiciones_list = ["Condición A", "Condición B", "Condición C", "Condición D"]
                    contrato = Contrato(
                        partner_id=partner_id,
                        tipo=random.choice(tipos),
                        fecha_inicio=date.today(),
                        fecha_fin=None if random.random() < 0.5 else date.today(),
                        monto=round(random.uniform(100, 10000), 2),
                        moneda=random.choice(monedas),
                        condiciones=random.choice(condiciones_list),
                        estado=random.choice(estados),
                        fecha_creacion=datetime.utcnow(),
                        fecha_actualizacion=None
                    )
                    # Use persistent event loop for async DB operation
                    result = loop.run_until_complete(self.use_case.execute(contrato))
                    logger.info(f'✅ Contrato created: {result}')

                    # Publish to ContratoCreado topic
                    compliance_producer = self.client.create_producer('ContratoCreado')
                    contrato_json = contrato.model_dump_json() if hasattr(contrato, 'model_dump_json') else json.dumps(contrato.dict(), default=str)
                    compliance_producer.send(contrato_json.encode('utf-8'))
                    logger.info(f'📤 Contrato published to ContratoCreado: {contrato_json}')

                    self.consumer.acknowledge(msg)
                except Exception as e:
                    logger.error(f'❌ Error processing message: {e}')
                    self.consumer.negative_acknowledge(msg)
                    
        except Exception as e:
            logger.error(f'💥 Fatal error in consumer loop: {e}')
            raise

    def close(self):
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("🎧 Pulsar consumer closed")

# Consumer for revision-contrato events
class PulsarRevisionContratoConsumer:
    def __init__(self):
        try:
            logger.info(f"🔌 Connecting Pulsar revision consumer to {PULSAR_SERVICE_URL}")
            self.client = pulsar.Client(PULSAR_SERVICE_URL)
            self.consumer = self.client.subscribe(
                TOPIC_REVISION_CONTRATO, 
                subscription_name='revision-contrato-sub',
                schema=pulsar.schema.BytesSchema()
            )
            logger.info(f"✅ Pulsar revision consumer initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Pulsar revision consumer: {e}")
            raise

    def listen(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            logger.info(f"📡 Subscribed to topic: {TOPIC_REVISION_CONTRATO}")

            while True:
                logger.info("⏳ Waiting for revision-contrato messages...")
                msg = self.consumer.receive()
                try:
                    logger.info(f"📨 Revision message received, processing...")
                    content = msg.data().decode('utf-8')
                    
                    # Parse the revision event
                    try:
                        data = json.loads(content)
                        partner_id = data.get("partner_id")
                        comentarios_revision = data.get("comentarios_revision", "Contrato requires revision")
                        
                        logger.info(f"🔄 Processing revision for partner: {partner_id}")
                        logger.info(f"📝 Revision comments: {comentarios_revision}")
                        
                    except json.JSONDecodeError:
                        logger.error(f"❌ Invalid JSON in revision message: {content}")
                        self.consumer.negative_acknowledge(msg)
                        continue
                    
                    if not partner_id:
                        logger.error(f"❌ No partner_id found in revision message: {content}")
                        self.consumer.negative_acknowledge(msg)
                        continue
                    
                    # Process the revision using the use case
                    from src.modulos.alianzas.domain.use_cases.process_revision_contrato_use_case import ProcessRevisionContratoUseCase
                    from src.modulos.alianzas.infrastructure.contrato_repository import ContratoRepository
                    from src.modulos.alianzas.infrastructure.db import get_session
                    
                    # Get database session and repository
                    session = await get_session()
                    repository = ContratoRepository(session)
                    use_case = ProcessRevisionContratoUseCase(repository)
                    
                    # Execute the use case
                    result = await use_case.execute(partner_id, comentarios_revision)
                    
                    if result:
                        logger.info(f'✅ Contract revision processed successfully for partner: {partner_id}')
                        logger.info(f'📄 Contract {result.id} updated to estado: {result.estado}')
                    else:
                        logger.warning(f'⚠️ No contract found for partner: {partner_id}')

                    self.consumer.acknowledge(msg)
                    await session.close()
                    
                except Exception as e:
                    logger.error(f'❌ Error processing revision message: {e}')
                    self.consumer.negative_acknowledge(msg)
                    if 'session' in locals():
                        await session.close()
                    
        except Exception as e:
            logger.error(f'💥 Fatal error in revision consumer loop: {e}')
            raise

    def close(self):
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("🎧 Pulsar revision consumer closed")


# Example usage (uncomment to run)
# db_adapter = ContratoPostgresAdapter()
# consumer = PulsarContratoConsumer(db_adapter)
# consumer.listen()

# revision_consumer = PulsarRevisionContratoConsumer()
# revision_consumer.listen()

# publisher = PulsarContratoPublisher()
# contrato = Contrato(...)
# publisher.publish_contrato(contrato)
# publisher.close()
