from flask import Blueprint, request, jsonify
import logging
from modulos.partners.aplicacion.saga_integration import SagaIntegration

# Configurar logging
logger = logging.getLogger(__name__)

# Crear blueprint
bp = Blueprint('saga_partners', __name__, url_prefix='/api/v1/saga/partners')

# Inicializar integración con saga
saga_integration = SagaIntegration()

@bp.route('', methods=['POST'])
def create_partner_with_saga():
    """Endpoint para crear un partner usando el patrón Saga"""
    logger.info("🔄 Iniciando creación de partner con Saga")
    try:
        data = request.get_json()
        logger.debug(f"Datos recibidos: {data}")
        
        # Validar datos requeridos
        if not data or not data.get('nombre') or not data.get('email'):
            return jsonify({
                'error': 'Nombre y email son requeridos',
                'codigo': 'DATOS_INVALIDOS'
            }), 400
        
        # Verificar si el saga orchestrator está disponible
        if not saga_integration.is_saga_orchestrator_available():
            return jsonify({
                'error': 'Saga Orchestrator no está disponible',
                'codigo': 'SAGA_NO_DISPONIBLE'
            }), 503
        
        # Extraer correlation_id si se proporciona
        correlation_id = data.get('correlation_id')
        
        # Iniciar saga de creación de partner
        saga_id = saga_integration.start_partner_creation_saga(data, correlation_id)
        
        if saga_id:
            logger.info(f"✅ Saga de creación de partner iniciada: {saga_id}")
            return jsonify({
                'mensaje': 'Saga de creación de partner iniciada exitosamente',
                'saga_id': saga_id,
                'correlation_id': correlation_id,
                'status': 'started',
                'partner_data': {
                    'nombre': data['nombre'],
                    'email': data['email'],
                    'telefono': data.get('telefono'),
                    'direccion': data.get('direccion')
                }
            }), 202
        else:
            return jsonify({
                'error': 'No se pudo iniciar la saga de creación de partner',
                'codigo': 'ERROR_SAGA'
            }), 500
        
    except Exception as e:
        logger.error(f"Error en create_partner_with_saga: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error interno del servidor',
            'codigo': 'ERROR_INTERNO'
        }), 500

@bp.route('/saga-status/<saga_id>', methods=['GET'])
def get_partner_saga_status(saga_id):
    """Endpoint para obtener el estado de una saga de creación de partner"""
    try:
        saga_status = saga_integration.get_saga_status(saga_id)
        
        if saga_status:
            return jsonify({
                'saga_status': saga_status
            }), 200
        else:
            return jsonify({
                'error': f'Saga no encontrada: {saga_id}',
                'codigo': 'SAGA_NO_ENCONTRADA'
            }), 404
        
    except Exception as e:
        logger.error(f"Error obteniendo estado de saga {saga_id}: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor',
            'codigo': 'ERROR_INTERNO'
        }), 500
