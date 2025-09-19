from flask import Blueprint, request, jsonify
import logging
from typing import Dict, Any
from ..application.saga_orchestrator import SagaOrchestrator
from ..application.event_handlers import PartnerCreationRequestHandler


class SagaAPI:
    """REST API for saga orchestrator"""
    
    def __init__(self, saga_orchestrator: SagaOrchestrator):
        self.saga_orchestrator = saga_orchestrator
        self.partner_creation_handler = PartnerCreationRequestHandler(saga_orchestrator)
        self.logger = logging.getLogger(__name__)
        
        # Create Flask blueprint
        self.bp = Blueprint('saga_api', __name__, url_prefix='/api/v1/saga')
        self._register_routes()
    
    def _register_routes(self):
        """Register API routes"""
        
        @self.bp.route('/partner-creation', methods=['POST'])
        def create_partner_saga():
            """Start a new partner creation saga"""
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({
                        'error': 'Request body is required',
                        'codigo': 'DATOS_INVALIDOS'
                    }), 400
                
                # Validate required fields
                if not data.get('nombre') or not data.get('email'):
                    return jsonify({
                        'error': 'nombre and email are required',
                        'codigo': 'DATOS_INVALIDOS'
                    }), 400
                
                # Extract correlation ID if provided
                correlation_id = data.get('correlation_id')
                
                # Start the saga
                saga_id = self.partner_creation_handler.handle_partner_creation_request(
                    partner_data=data,
                    correlation_id=correlation_id
                )
                
                return jsonify({
                    'mensaje': 'Partner creation saga started successfully',
                    'saga_id': saga_id,
                    'correlation_id': correlation_id,
                    'status': 'started'
                }), 202
                
            except ValueError as e:
                return jsonify({
                    'error': str(e),
                    'codigo': 'DATOS_INVALIDOS'
                }), 400
            except Exception as e:
                self.logger.error(f"Error starting partner creation saga: {e}")
                return jsonify({
                    'error': 'Internal server error',
                    'codigo': 'ERROR_INTERNO'
                }), 500
        
        @self.bp.route('/status/<saga_id>', methods=['GET'])
        def get_saga_status(saga_id: str):
            """Get status of a specific saga"""
            try:
                saga_status = self.saga_orchestrator.get_saga_status(saga_id)
                
                if not saga_status:
                    return jsonify({
                        'error': f'Saga not found: {saga_id}',
                        'codigo': 'SAGA_NO_ENCONTRADA'
                    }), 404
                
                return jsonify({
                    'saga': saga_status
                }), 200
                
            except Exception as e:
                self.logger.error(f"Error getting saga status {saga_id}: {e}")
                return jsonify({
                    'error': 'Internal server error',
                    'codigo': 'ERROR_INTERNO'
                }), 500
        
        @self.bp.route('/active', methods=['GET'])
        def list_active_sagas():
            """List all active sagas"""
            try:
                active_sagas = self.saga_orchestrator.list_active_sagas()
                
                return jsonify({
                    'active_sagas': active_sagas,
                    'total': len(active_sagas)
                }), 200
                
            except Exception as e:
                self.logger.error(f"Error listing active sagas: {e}")
                return jsonify({
                    'error': 'Internal server error',
                    'codigo': 'ERROR_INTERNO'
                }), 500
        
        @self.bp.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'service': 'saga-orchestrator',
                'timestamp': '2025-09-19T11:53:47-05:00'
            }), 200
    
    def get_blueprint(self):
        """Get the Flask blueprint"""
        return self.bp
