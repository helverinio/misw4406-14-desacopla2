import logging
from typing import Dict, Any
from .saga_orchestrator import SagaOrchestrator


class SagaEventHandler:
    """Event handler for saga-related events"""
    
    def __init__(self, saga_orchestrator: SagaOrchestrator):
        self.saga_orchestrator = saga_orchestrator
        self.logger = logging.getLogger(__name__)
    
    def handle_partner_event(self, message_data: Dict[str, Any]):
        """Handle partner-related events"""
        try:
            event_type = message_data.get('event_type', 'partner_created')
            
            if event_type == 'partner_created':
                self._handle_partner_created_event(message_data)
            elif event_type == 'partner_creation_failed':
                self._handle_partner_creation_failed_event(message_data)
            else:
                self.logger.warning(f"Unknown partner event type: {event_type}")
                
        except Exception as e:
            self.logger.error(f"Error handling partner event: {e}")
    
    def handle_alliance_event(self, message_data: Dict[str, Any]):
        """Handle alliance-related events"""
        try:
            # Check if this is a contract creation event from gestion-de-alianzas
            if 'partner_id' in message_data and ('id' in message_data or 'contrato_id' in message_data):
                # This looks like a contract/alliance creation event
                self._handle_alliance_created_event(message_data)
            else:
                self.logger.debug(f"Received alliance event but not a creation event: {message_data}")
                
        except Exception as e:
            self.logger.error(f"Error handling alliance event: {e}")
    
    def _handle_partner_created_event(self, message_data: Dict[str, Any]):
        """Handle partner created event"""
        try:
            partner_id = message_data.get('partner_id')
            saga_id = message_data.get('saga_id')
            
            if not partner_id:
                self.logger.warning("Partner created event missing partner_id")
                return
            
            if saga_id:
                # This is part of a saga, let the orchestrator handle it
                saga_state = self.saga_orchestrator.saga_repository.get_saga_state(saga_id)
                if saga_state:
                    self.saga_orchestrator._handle_partner_created(saga_state, partner_id, message_data)
                else:
                    self.logger.warning(f"Saga state not found for saga_id: {saga_id}")
            else:
                self.logger.info(f"Partner created outside of saga: {partner_id}")
                
        except Exception as e:
            self.logger.error(f"Error handling partner created event: {e}")
    
    def _handle_partner_creation_failed_event(self, message_data: Dict[str, Any]):
        """Handle partner creation failed event"""
        try:
            saga_id = message_data.get('saga_id')
            error = message_data.get('error', 'Unknown error')
            
            if saga_id:
                saga_state = self.saga_orchestrator.saga_repository.get_saga_state(saga_id)
                if saga_state:
                    self.saga_orchestrator._handle_partner_creation_failed(saga_state, error)
                else:
                    self.logger.warning(f"Saga state not found for saga_id: {saga_id}")
            else:
                self.logger.info(f"Partner creation failed outside of saga: {error}")
                
        except Exception as e:
            self.logger.error(f"Error handling partner creation failed event: {e}")
    
    def _handle_alliance_created_event(self, message_data: Dict[str, Any]):
        """Handle alliance/contract created event"""
        try:
            # Extract relevant information from the contract creation event
            partner_id = message_data.get('partner_id')
            alliance_id = message_data.get('id') or message_data.get('contrato_id')
            saga_id = message_data.get('saga_id')
            
            if not partner_id or not alliance_id:
                self.logger.warning(f"Alliance created event missing required fields: {message_data}")
                return
            
            # If saga_id is not in the message, try to find active saga for this partner
            if not saga_id:
                active_sagas = self.saga_orchestrator.saga_repository.get_active_sagas()
                for saga in active_sagas:
                    if saga.partner_id == partner_id and saga.status.value in ['alliance_creation_in_progress', 'partner_created']:
                        saga_id = saga.saga_id
                        break
            
            if saga_id:
                # Add saga_id to the event data for the orchestrator
                message_data['saga_id'] = saga_id
                message_data['alliance_id'] = alliance_id
                
                self.saga_orchestrator.handle_alliance_created_event(message_data)
            else:
                self.logger.info(f"Alliance created outside of saga: partner_id={partner_id}, alliance_id={alliance_id}")
                
        except Exception as e:
            self.logger.error(f"Error handling alliance created event: {e}")


class PartnerCreationRequestHandler:
    """Handler for external partner creation requests"""
    
    def __init__(self, saga_orchestrator: SagaOrchestrator):
        self.saga_orchestrator = saga_orchestrator
        self.logger = logging.getLogger(__name__)
    
    def handle_partner_creation_request(self, partner_data: Dict[str, Any], correlation_id: str = None) -> str:
        """Handle external partner creation request by starting a saga"""
        try:
            # Validate required fields
            if not partner_data.get('nombre') or not partner_data.get('email'):
                raise ValueError("Partner data must include 'nombre' and 'email'")
            
            # Start the saga
            saga_id = self.saga_orchestrator.start_partner_creation_saga(partner_data, correlation_id)
            
            self.logger.info(f"Started partner creation saga {saga_id} for partner: {partner_data.get('email')}")
            return saga_id
            
        except Exception as e:
            self.logger.error(f"Error handling partner creation request: {e}")
            raise
