import logging
import threading
from typing import Dict, Any
from ..infrastructure.pulsar_client import PulsarClient, SagaEventListener
from ..application.event_handlers import SagaEventHandler


class EventListenerService:
    """Service to listen to events from other microservices"""
    
    def __init__(self, saga_event_handler: SagaEventHandler, pulsar_client: PulsarClient):
        self.saga_event_handler = saga_event_handler
        self.pulsar_client = pulsar_client
        self.logger = logging.getLogger(__name__)
        self.listener_threads = []
        self.running = False
    
    def start_listeners(self):
        """Start all event listeners in separate threads"""
        if self.running:
            self.logger.warning("Event listeners are already running")
            return
        
        self.running = True
        
        # Start partner events listener
        partner_thread = threading.Thread(
            target=self._listen_to_partner_events,
            daemon=True,
            name="PartnerEventsListener"
        )
        partner_thread.start()
        self.listener_threads.append(partner_thread)
        
        # Start alliance events listener
        alliance_thread = threading.Thread(
            target=self._listen_to_alliance_events,
            daemon=True,
            name="AllianceEventsListener"
        )
        alliance_thread.start()
        self.listener_threads.append(alliance_thread)
        
        self.logger.info("Started all event listeners")
    
    def stop_listeners(self):
        """Stop all event listeners"""
        self.running = False
        self.logger.info("Stopping event listeners...")
        
        # Note: Threads will stop naturally when the main process exits
        # since they are daemon threads
    
    def _listen_to_partner_events(self):
        """Listen to partner events from gestion-de-integraciones"""
        try:
            event_listener = SagaEventListener(self.pulsar_client)
            event_listener.listen_to_partner_events(self._handle_partner_message)
        except Exception as e:
            self.logger.error(f"Error in partner events listener: {e}")
    
    def _listen_to_alliance_events(self):
        """Listen to alliance events from gestion-de-alianzas"""
        try:
            event_listener = SagaEventListener(self.pulsar_client)
            event_listener.listen_to_alliance_events(self._handle_alliance_message)
        except Exception as e:
            self.logger.error(f"Error in alliance events listener: {e}")
    
    def _handle_partner_message(self, message_data: Dict[str, Any]):
        """Handle partner-related messages"""
        try:
            self.logger.debug(f"Received partner message: {message_data}")
            self.saga_event_handler.handle_partner_event(message_data)
        except Exception as e:
            self.logger.error(f"Error handling partner message: {e}")
    
    def _handle_alliance_message(self, message_data: Dict[str, Any]):
        """Handle alliance-related messages"""
        try:
            self.logger.debug(f"Received alliance message: {message_data}")
            self.saga_event_handler.handle_alliance_event(message_data)
        except Exception as e:
            self.logger.error(f"Error handling alliance message: {e}")
