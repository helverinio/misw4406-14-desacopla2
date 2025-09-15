
from fastapi import FastAPI
from src.exceptions import setup_exception_handlers
from src.config import Settings
from src.entrypoints.api.routers.contrato_router import router as contrato_router
from src.infrastructure.pulsar_integration import PulsarContratoConsumer, PulsarContratoPublisher
from src.adapters.postgres.contrato_postgres_adapter import PostgresContratoRepository

import threading

app = FastAPI(title=Settings.app_name)
app.include_router(contrato_router)
setup_exception_handlers(app)

# Pulsar integration
publisher = PulsarContratoPublisher()

def run_consumer():
	consumer = PulsarContratoConsumer()
	consumer.listen()

@app.on_event("startup")
def startup_event():
	thread = threading.Thread(target=run_consumer, daemon=True)
	thread.start()

@app.on_event("shutdown")
def shutdown_event():
	publisher.close()