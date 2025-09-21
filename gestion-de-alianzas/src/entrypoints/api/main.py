
from fastapi import FastAPI
from contextlib import asynccontextmanager
import threading
import logging
from src.exceptions import setup_exception_handlers
from src.config import Settings
from src.entrypoints.api.routers.contrato_router import router as contrato_router
from src.modulos.alianzas.infrastructure.pulsar_integration import PulsarContratoConsumer, PulsarContratoPublisher
from src.modulos.alianzas.adapters.postgres.contrato_postgres_adapter import PostgresContratoRepository
from src.modulos.sagas.infraestructura.saga_integration import iniciar_saga_integration, detener_saga_integration

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

publisher = None
consumer_thread = None

def run_consumer():
    try:
        consumer = PulsarContratoConsumer()
        consumer.listen()
    except Exception as e:
        logger.error(f"❌ Error in consumer: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🔥 INICIANDO APLICACIÓN DE GESTIÓN DE ALIANZAS")
    
    # Inicializar Pulsar publisher
    global publisher
    logger.info("📡 Inicializando Pulsar publisher...")
    publisher = PulsarContratoPublisher()
    
    # Iniciar consumer en thread separado
    global consumer_thread
    consumer_thread = threading.Thread(target=run_consumer, daemon=True)
    consumer_thread.start()
    logger.info("✅ Consumer de Pulsar iniciado correctamente")
    
    # Iniciar saga listener
    try:
        iniciar_saga_integration()
        logger.info("🎭 Saga integration iniciada correctamente")
    except Exception as e:
        logger.error(f"❌ Error iniciando saga integration: {e}")
    
    yield 
    
    # ✅ SHUTDOWN
    if publisher:
        publisher.close()
    
    # Detener saga integration
    try:
        detener_saga_integration()
    except Exception as e:
        logger.error(f"❌ Error deteniendo saga integration: {e}")
        
    logger.info("✅ Aplicación cerrada correctamente")

app = FastAPI(
    title=Settings.app_name,
    lifespan=lifespan
)

app.include_router(contrato_router)
setup_exception_handlers(app)