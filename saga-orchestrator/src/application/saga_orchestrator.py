import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
import requests
from ..domain.saga_state import SagaState, SagaStatus, SagaStep
from ..domain.events import (
    PartnerCreationStarted, PartnerCreated, AllianceCreationStarted, 
    AllianceCreated, PartnerCreationFailed, AllianceCreationFailed,
    SagaCompleted, SagaFailed, CompensationStarted, CompensationCompleted
)
from ..infrastructure.pulsar_client import SagaEventPublisher, SagaEventListener
from ..infrastructure.database import SagaRepository


class SagaOrchestrator:
    """Central saga orchestrator for partner creation workflow"""
    
    def __init__(self, event_publisher: SagaEventPublisher, saga_repository: SagaRepository):
        self.event_publisher = event_publisher
        self.saga_repository = saga_repository
        self.logger = logging.getLogger(__name__)
        
        # Service URLs (should be configurable)
        self.integraciones_api_url = "http://localhost:5001"  # gestion-de-integraciones
        self.alianzas_api_url = "http://localhost:5002"       # gestion-de-alianzas
    
    def start_partner_creation_saga(self, partner_data: Dict[str, Any], correlation_id: Optional[str] = None) -> str:
        """Start a new partner creation saga"""
        try:
            # Create new saga state
            saga_state = SagaState.create_new(partner_data, correlation_id)
            
            # Save initial state
            self.saga_repository.save_saga_state(saga_state)
            
            # Publish saga started event
            event = PartnerCreationStarted(
                saga_id=saga_state.saga_id,
                event_id=str(uuid.uuid4()),
                partner_data=partner_data,
                correlation_id=correlation_id
            )
            self.event_publisher.publish_saga_event(event)
            
            # Start first step: create partner
            self._execute_create_partner_step(saga_state)
            
            self.logger.info(f"Started partner creation saga: {saga_state.saga_id}")
            return saga_state.saga_id
            
        except Exception as e:
            self.logger.error(f"Failed to start partner creation saga: {e}")
            raise
    
    def _execute_create_partner_step(self, saga_state: SagaState):
        """Execute partner creation step"""
        try:
            # Update saga state
            saga_state.status = SagaStatus.PARTNER_CREATION_IN_PROGRESS
            saga_state.start_step(SagaStep.CREATE_PARTNER)
            self.saga_repository.save_saga_state(saga_state)
            
            # Call gestion-de-integraciones API to create partner
            response = requests.post(
                f"{self.integraciones_api_url}/api/v1/partners",
                json=saga_state.partner_data,
                timeout=30
            )
            
            if response.status_code == 201:
                # Partner created successfully
                partner_response = response.json()
                partner_id = partner_response.get('partner', {}).get('id')
                
                if partner_id:
                    self._handle_partner_created(saga_state, partner_id, partner_response.get('partner', {}))
                else:
                    self._handle_partner_creation_failed(saga_state, "Partner ID not returned from service")
            else:
                # Partner creation failed
                error_msg = f"Partner creation failed with status {response.status_code}: {response.text}"
                self._handle_partner_creation_failed(saga_state, error_msg)
                
        except Exception as e:
            error_msg = f"Exception during partner creation: {str(e)}"
            self._handle_partner_creation_failed(saga_state, error_msg)
    
    def _handle_partner_created(self, saga_state: SagaState, partner_id: str, partner_data: Dict[str, Any]):
        """Handle successful partner creation"""
        try:
            # Update saga state
            saga_state.set_partner_created(partner_id)
            self.saga_repository.save_saga_state(saga_state)
            
            # Publish partner created event
            event = PartnerCreated(
                saga_id=saga_state.saga_id,
                event_id=str(uuid.uuid4()),
                partner_id=partner_id,
                partner_data=partner_data,
                correlation_id=saga_state.correlation_id
            )
            self.event_publisher.publish_saga_event(event)
            
            # Start next step: create alliance
            self._execute_create_alliance_step(saga_state)
            
            self.logger.info(f"Partner created successfully in saga {saga_state.saga_id}: {partner_id}")
            
        except Exception as e:
            self.logger.error(f"Error handling partner created in saga {saga_state.saga_id}: {e}")
            self._handle_partner_creation_failed(saga_state, str(e))
    
    def _handle_partner_creation_failed(self, saga_state: SagaState, error: str):
        """Handle failed partner creation"""
        try:
            # Update saga state
            saga_state.fail_saga(error, SagaStep.CREATE_PARTNER)
            self.saga_repository.save_saga_state(saga_state)
            
            # Publish partner creation failed event
            event = PartnerCreationFailed(
                saga_id=saga_state.saga_id,
                event_id=str(uuid.uuid4()),
                error=error,
                partner_data=saga_state.partner_data,
                correlation_id=saga_state.correlation_id
            )
            self.event_publisher.publish_saga_event(event)
            
            # Publish saga failed event
            saga_failed_event = SagaFailed(
                saga_id=saga_state.saga_id,
                event_id=str(uuid.uuid4()),
                error=error,
                step_failed="create_partner",
                correlation_id=saga_state.correlation_id
            )
            self.event_publisher.publish_saga_event(saga_failed_event)
            
            self.logger.error(f"Partner creation failed in saga {saga_state.saga_id}: {error}")
            
        except Exception as e:
            self.logger.error(f"Error handling partner creation failure in saga {saga_state.saga_id}: {e}")
    
    def _execute_create_alliance_step(self, saga_state: SagaState):
        """Execute alliance creation step"""
        try:
            # Update saga state
            saga_state.status = SagaStatus.ALLIANCE_CREATION_IN_PROGRESS
            saga_state.start_step(SagaStep.CREATE_ALLIANCE)
            self.saga_repository.save_saga_state(saga_state)
            
            # Publish alliance creation started event
            event = AllianceCreationStarted(
                saga_id=saga_state.saga_id,
                event_id=str(uuid.uuid4()),
                partner_id=saga_state.partner_id,
                correlation_id=saga_state.correlation_id
            )
            self.event_publisher.publish_saga_event(event)
            
            # Send event to gestion-de-alianzas via Pulsar
            alliance_data = {
                "partner_id": saga_state.partner_id,
                "partner_data": saga_state.partner_data,
                "saga_id": saga_state.saga_id,
                "correlation_id": saga_state.correlation_id,
                "command": "create_alliance"
            }
            
            success = self.event_publisher.publish_alliance_creation_command(
                saga_state.partner_id, 
                saga_state.partner_data
            )
            
            if not success:
                self._handle_alliance_creation_failed(saga_state, "Failed to publish alliance creation command")
            else:
                self.logger.info(f"Alliance creation command sent for saga {saga_state.saga_id}")
                
        except Exception as e:
            error_msg = f"Exception during alliance creation: {str(e)}"
            self._handle_alliance_creation_failed(saga_state, error_msg)
    
    def handle_alliance_created_event(self, event_data: Dict[str, Any]):
        """Handle alliance created event from gestion-de-alianzas"""
        try:
            saga_id = event_data.get('saga_id')
            alliance_id = event_data.get('alliance_id') or event_data.get('contrato_id')
            partner_id = event_data.get('partner_id')
            
            if not saga_id:
                self.logger.warning("Received alliance created event without saga_id")
                return
            
            # Get saga state
            saga_state = self.saga_repository.get_saga_state(saga_id)
            if not saga_state:
                self.logger.warning(f"Saga state not found for saga_id: {saga_id}")
                return
            
            if alliance_id:
                self._handle_alliance_created(saga_state, alliance_id)
            else:
                self._handle_alliance_creation_failed(saga_state, "Alliance ID not provided in event")
                
        except Exception as e:
            self.logger.error(f"Error handling alliance created event: {e}")
    
    def _handle_alliance_created(self, saga_state: SagaState, alliance_id: str):
        """Handle successful alliance creation"""
        try:
            # Update saga state
            saga_state.set_alliance_created(alliance_id)
            self.saga_repository.save_saga_state(saga_state)
            
            # Publish alliance created event
            event = AllianceCreated(
                saga_id=saga_state.saga_id,
                event_id=str(uuid.uuid4()),
                partner_id=saga_state.partner_id,
                alliance_id=alliance_id,
                correlation_id=saga_state.correlation_id
            )
            self.event_publisher.publish_saga_event(event)
            
            # Complete the saga
            self._complete_saga(saga_state)
            
            self.logger.info(f"Alliance created successfully in saga {saga_state.saga_id}: {alliance_id}")
            
        except Exception as e:
            self.logger.error(f"Error handling alliance created in saga {saga_state.saga_id}: {e}")
            self._handle_alliance_creation_failed(saga_state, str(e))
    
    def _handle_alliance_creation_failed(self, saga_state: SagaState, error: str):
        """Handle failed alliance creation"""
        try:
            # Update saga state
            saga_state.fail_saga(error, SagaStep.CREATE_ALLIANCE)
            self.saga_repository.save_saga_state(saga_state)
            
            # Publish alliance creation failed event
            event = AllianceCreationFailed(
                saga_id=saga_state.saga_id,
                event_id=str(uuid.uuid4()),
                partner_id=saga_state.partner_id,
                error=error,
                correlation_id=saga_state.correlation_id
            )
            self.event_publisher.publish_saga_event(event)
            
            # Start compensation (rollback partner creation)
            self._start_compensation(saga_state)
            
            self.logger.error(f"Alliance creation failed in saga {saga_state.saga_id}: {error}")
            
        except Exception as e:
            self.logger.error(f"Error handling alliance creation failure in saga {saga_state.saga_id}: {e}")
    
    def _complete_saga(self, saga_state: SagaState):
        """Complete the saga successfully"""
        try:
            # Update saga state
            saga_state.complete_saga()
            self.saga_repository.save_saga_state(saga_state)
            
            # Publish saga completed event
            event = SagaCompleted(
                saga_id=saga_state.saga_id,
                event_id=str(uuid.uuid4()),
                partner_id=saga_state.partner_id,
                alliance_id=saga_state.alliance_id,
                correlation_id=saga_state.correlation_id
            )
            self.event_publisher.publish_saga_event(event)
            
            self.logger.info(f"Saga completed successfully: {saga_state.saga_id}")
            
        except Exception as e:
            self.logger.error(f"Error completing saga {saga_state.saga_id}: {e}")
    
    def _start_compensation(self, saga_state: SagaState):
        """Start compensation process"""
        try:
            compensation_actions = []
            
            # If partner was created, we need to delete it
            if saga_state.partner_id and saga_state.steps[SagaStep.CREATE_PARTNER].status == "completed":
                compensation_actions.append(f"delete_partner:{saga_state.partner_id}")
            
            # Update saga state
            saga_state.start_compensation(compensation_actions)
            self.saga_repository.save_saga_state(saga_state)
            
            # Publish compensation started event
            event = CompensationStarted(
                saga_id=saga_state.saga_id,
                event_id=str(uuid.uuid4()),
                compensation_actions=compensation_actions,
                correlation_id=saga_state.correlation_id
            )
            self.event_publisher.publish_saga_event(event)
            
            # Execute compensation actions
            self._execute_compensation(saga_state, compensation_actions)
            
            self.logger.info(f"Started compensation for saga {saga_state.saga_id}")
            
        except Exception as e:
            self.logger.error(f"Error starting compensation for saga {saga_state.saga_id}: {e}")
    
    def _execute_compensation(self, saga_state: SagaState, actions: list):
        """Execute compensation actions"""
        try:
            compensation_results = {}
            
            for action in actions:
                if action.startswith("delete_partner:"):
                    partner_id = action.split(":")[1]
                    success = self._compensate_partner_creation(partner_id)
                    compensation_results[action] = "success" if success else "failed"
            
            # Update saga state
            saga_state.complete_compensation()
            self.saga_repository.save_saga_state(saga_state)
            
            # Publish compensation completed event
            event = CompensationCompleted(
                saga_id=saga_state.saga_id,
                event_id=str(uuid.uuid4()),
                compensation_results=compensation_results,
                correlation_id=saga_state.correlation_id
            )
            self.event_publisher.publish_saga_event(event)
            
            self.logger.info(f"Compensation completed for saga {saga_state.saga_id}")
            
        except Exception as e:
            self.logger.error(f"Error executing compensation for saga {saga_state.saga_id}: {e}")
    
    def _compensate_partner_creation(self, partner_id: str) -> bool:
        """Compensate partner creation by deleting the partner"""
        try:
            response = requests.delete(
                f"{self.integraciones_api_url}/api/v1/partners/{partner_id}",
                timeout=30
            )
            
            if response.status_code in [200, 404]:  # 404 is OK, partner might already be deleted
                self.logger.info(f"Successfully compensated partner creation: {partner_id}")
                return True
            else:
                self.logger.error(f"Failed to compensate partner creation {partner_id}: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception during partner compensation {partner_id}: {e}")
            return False
    
    def get_saga_status(self, saga_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a saga"""
        saga_state = self.saga_repository.get_saga_state(saga_id)
        if saga_state:
            return saga_state.to_dict()
        return None
    
    def list_active_sagas(self) -> list:
        """List all active sagas"""
        active_sagas = self.saga_repository.get_active_sagas()
        return [saga.to_dict() for saga in active_sagas]
