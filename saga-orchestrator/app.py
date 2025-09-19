import os
import logging
from flask import Flask
from dotenv import load_dotenv
from src.infrastructure.pulsar_client import PulsarClient, SagaEventPublisher
from src.infrastructure.database import SagaRepository
from src.application.saga_orchestrator import SagaOrchestrator
from src.application.event_handlers import SagaEventHandler
from src.application.event_listener_service import EventListenerService
from src.api.saga_api import SagaAPI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['BROKER_URL'] = os.getenv('BROKER_URL', 'pulsar://localhost:6650')
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/saga_db')
    app.config['INTEGRACIONES_API_URL'] = os.getenv('INTEGRACIONES_API_URL', 'http://localhost:5001')
    app.config['ALIANZAS_API_URL'] = os.getenv('ALIANZAS_API_URL', 'http://localhost:5002')
    
    # Initialize infrastructure
    pulsar_client = PulsarClient(app.config['BROKER_URL'])
    saga_repository = SagaRepository(app.config['DATABASE_URL'])
    
    # Initialize application services
    event_publisher = SagaEventPublisher(pulsar_client)
    saga_orchestrator = SagaOrchestrator(event_publisher, saga_repository)
    
    # Update orchestrator with service URLs
    saga_orchestrator.integraciones_api_url = app.config['INTEGRACIONES_API_URL']
    saga_orchestrator.alianzas_api_url = app.config['ALIANZAS_API_URL']
    
    # Initialize event handling
    saga_event_handler = SagaEventHandler(saga_orchestrator)
    event_listener_service = EventListenerService(saga_event_handler, pulsar_client)
    
    # Initialize API
    saga_api = SagaAPI(saga_orchestrator)
    app.register_blueprint(saga_api.get_blueprint())
    
    # Store services in app context for cleanup
    app.pulsar_client = pulsar_client
    app.event_listener_service = event_listener_service
    
    # Initialize services at startup
    def initialize_services():
        """Initialize services at startup"""
        try:
            logger.info("Starting Saga Orchestrator services...")
            
            # Connect to Pulsar
            pulsar_client.connect()
            
            # Start event listeners
            event_listener_service.start_listeners()
            
            logger.info("Saga Orchestrator started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Saga Orchestrator: {e}")
            raise
    
    # Store initialization function for later use
    app.initialize_services = initialize_services
    
    @app.teardown_appcontext
    def cleanup(error):
        """Cleanup resources"""
        if error:
            logger.error(f"Application error: {error}")
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {
            'status': 'healthy',
            'service': 'saga-orchestrator',
            'version': '1.0.0'
        }
    
    return app

def main():
    """Main entry point"""
    try:
        app = create_app()
        
        # Initialize services
        app.initialize_services()
        
        # Get configuration
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 5003))
        debug = os.getenv('DEBUG', 'False').lower() == 'true'
        
        logger.info(f"Starting Saga Orchestrator on {host}:{port}")
        
        # Run the application
        app.run(host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        logger.info("Saga Orchestrator stopped by user")
    except Exception as e:
        logger.error(f"Failed to start Saga Orchestrator: {e}")
        raise
    finally:
        # Cleanup
        if 'app' in locals():
            if hasattr(app, 'event_listener_service'):
                app.event_listener_service.stop_listeners()
            if hasattr(app, 'pulsar_client'):
                app.pulsar_client.disconnect()

if __name__ == '__main__':
    main()
