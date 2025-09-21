
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from src.exceptions import setup_exception_handlers
from src.config import Settings
from src.presentation.api.routers.v1.partners_router import router as partners_router
#from src.infrastructure.pulsar_integration import PulsarContratoConsumer, PulsarContratoPublisher

import threading

app = FastAPI(title=Settings.app_name)

@app.get("/ping", response_class=PlainTextResponse)
def health_check():
    """Healthcheck endpoint."""
    return "pong"

app.include_router(partners_router, prefix="/api")
setup_exception_handlers(app)

# Pulsar integration
# publisher = PulsarContratoPublisher()

# def run_consumer():
#	consumer = PulsarContratoConsumer()
#	consumer.listen()
"""
 
	
@app.on_event("startup")
def startup_event():
	thread = threading.Thread(target=run_consumer, daemon=True)
	thread.start()

@app.on_event("shutdown")
def shutdown_event():
	publisher.close()
"""