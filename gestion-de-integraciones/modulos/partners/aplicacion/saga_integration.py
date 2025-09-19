import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime
import os


class SagaIntegration:
    """Integration with Saga Orchestrator for partner creation workflow"""
    
    def __init__(self):
        self.saga_orchestrator_url = os.getenv('SAGA_ORCHESTRATOR_URL', 'http://localhost:5003')
        self.logger = logging.getLogger(__name__)
    
    def start_partner_creation_saga(self, partner_data: Dict[str, Any], correlation_id: Optional[str] = None) -> Optional[str]:
        """Start a partner creation saga through the orchestrator"""
        try:
            # Prepare saga request
            saga_request = {
                **partner_data,
                'correlation_id': correlation_id
            }
            
            # Call saga orchestrator
            response = requests.post(
                f"{self.saga_orchestrator_url}/api/v1/saga/partner-creation",
                json=saga_request,
                timeout=30
            )
            
            if response.status_code == 202:
                saga_response = response.json()
                saga_id = saga_response.get('saga_id')
                
                self.logger.info(f"Started partner creation saga: {saga_id}")
                return saga_id
            else:
                self.logger.error(f"Failed to start saga: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error starting partner creation saga: {e}")
            return None
    
    def get_saga_status(self, saga_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a saga"""
        try:
            response = requests.get(
                f"{self.saga_orchestrator_url}/api/v1/saga/status/{saga_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('saga')
            else:
                self.logger.error(f"Failed to get saga status: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting saga status: {e}")
            return None
    
    def is_saga_orchestrator_available(self) -> bool:
        """Check if saga orchestrator is available"""
        try:
            response = requests.get(
                f"{self.saga_orchestrator_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
