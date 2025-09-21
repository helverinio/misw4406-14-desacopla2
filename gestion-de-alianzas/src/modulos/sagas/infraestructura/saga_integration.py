"""
Integración del listener de saga con la aplicación FastAPI
"""
import threading
import logging
import sys
import os

# Agregar paths para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from modulos.sagas.infraestructura.pulsar_saga_listener import PulsarSagaListener

logger = logging.getLogger(__name__)


class SagaIntegration:
    """
    Clase para integrar el listener de saga con la aplicación
    """
    
    def __init__(self):
        self.saga_listener = None
        self.saga_thread = None
    
    def start_saga_listener(self):
        """
        Inicia el listener de saga en un thread separado
        """
        try:
            logger.info("🎭 Iniciando saga listener...")
            
            def run_saga_listener():
                try:
                    self.saga_listener = PulsarSagaListener()
                    self.saga_listener.listen()
                except Exception as e:
                    logger.error(f"❌ Error in saga listener: {e}")
            
            # Iniciar en thread separado
            self.saga_thread = threading.Thread(target=run_saga_listener, daemon=True)
            self.saga_thread.start()
            
            logger.info("✅ Saga listener iniciado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Failed to start saga listener: {e}")
            raise
    
    def stop_saga_listener(self):
        """
        Detiene el listener de saga
        """
        if self.saga_listener:
            self.saga_listener.close()
            logger.info("🎭 Saga listener cerrado")


# Instancia global
saga_integration = SagaIntegration()


def iniciar_saga_integration():
    """
    Función helper para iniciar la integración de saga
    """
    saga_integration.start_saga_listener()


def detener_saga_integration():
    """
    Función helper para detener la integración de saga
    """
    saga_integration.stop_saga_listener()