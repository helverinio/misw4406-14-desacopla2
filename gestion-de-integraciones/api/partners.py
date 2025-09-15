from flask import Blueprint, request, jsonify
import logging
from modulos.partners.aplicacion.servicios import ServicioPartners
from modulos.partners.aplicacion.dto import (
    CrearPartnerDTO, ActualizarPartnerDTO, VerificarKYCDTO, 
    CrearIntegracionDTO, RevocarIntegracionDTO
)
from modulos.partners.infraestructura.repositorios import (
    RepositorioPartnersSQLAlchemy, RepositorioIntegracionesSQLAlchemy
)
from modulos.partners.dominio.excepciones import (
    PartnerNoEncontrado, EmailYaExiste, IntegracionNoEncontrada,
    KYCNoValido, PartnerEliminado, IntegracionYaRevocada
)

# Configurar logging
logger = logging.getLogger(__name__)

# Crear blueprint
bp = Blueprint('partners', __name__, url_prefix='/api/v1/partners')

# Inicializar servicios
repositorio_partners = RepositorioPartnersSQLAlchemy()
repositorio_integraciones = RepositorioIntegracionesSQLAlchemy()
servicio_partners = ServicioPartners(repositorio_partners, repositorio_integraciones)

@bp.route('', methods=['POST'])
def crear_partner():
    """Endpoint para crear un nuevo partner"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data or not data.get('nombre') or not data.get('email'):
            return jsonify({
                'error': 'Nombre y email son requeridos',
                'codigo': 'DATOS_INVALIDOS'
            }), 400
        
        # Crear DTO
        dto = CrearPartnerDTO(
            nombre=data['nombre'],
            email=data['email'],
            telefono=data.get('telefono'),
            direccion=data.get('direccion')
        )
        
        # Crear partner
        partner_creado = servicio_partners.crear_partner(dto)
        
        return jsonify({
            'mensaje': 'Partner creado exitosamente',
            'partner': {
                'id': partner_creado.id,
                'nombre': partner_creado.nombre,
                'email': partner_creado.email,
                'telefono': partner_creado.telefono,
                'direccion': partner_creado.direccion,
                'estado': partner_creado.estado,
                'estado_kyc': partner_creado.estado_kyc,
                'fecha_creacion': partner_creado.fecha_creacion.isoformat()
            }
        }), 201
        
    except EmailYaExiste as e:
        return jsonify({
            'error': str(e),
            'codigo': 'EMAIL_EXISTENTE'
        }), 409
        
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'codigo': 'ERROR_INTERNO'
        }), 500

@bp.route('/<partner_id>', methods=['PUT'])
def actualizar_partner(partner_id):
    """Endpoint para actualizar un partner existente"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Datos requeridos para actualización',
                'codigo': 'DATOS_INVALIDOS'
            }), 400
        
        # Crear DTO
        dto = ActualizarPartnerDTO(
            nombre=data.get('nombre'),
            telefono=data.get('telefono'),
            direccion=data.get('direccion')
        )
        
        # Actualizar partner
        partner_actualizado = servicio_partners.actualizar_partner(partner_id, dto)
        
        return jsonify({
            'mensaje': 'Partner actualizado exitosamente',
            'partner': {
                'id': partner_actualizado.id,
                'nombre': partner_actualizado.nombre,
                'email': partner_actualizado.email,
                'telefono': partner_actualizado.telefono,
                'direccion': partner_actualizado.direccion,
                'estado': partner_actualizado.estado,
                'estado_kyc': partner_actualizado.estado_kyc,
                'fecha_actualizacion': partner_actualizado.fecha_actualizacion.isoformat() if partner_actualizado.fecha_actualizacion else None
            }
        }), 200
        
    except PartnerNoEncontrado as e:
        return jsonify({
            'error': str(e),
            'codigo': 'PARTNER_NO_ENCONTRADO'
        }), 404
        
    except PartnerEliminado as e:
        return jsonify({
            'error': str(e),
            'codigo': 'PARTNER_ELIMINADO'
        }), 410
        
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'codigo': 'ERROR_INTERNO'
        }), 500

@bp.route('/<partner_id>', methods=['DELETE'])
def eliminar_partner(partner_id):
    """Endpoint para eliminar un partner"""
    try:
        resultado = servicio_partners.eliminar_partner(partner_id)
        
        if resultado:
            return jsonify({
                'mensaje': 'Partner eliminado exitosamente',
                'partner_id': partner_id
            }), 200
        else:
            return jsonify({
                'error': 'No se pudo eliminar el partner',
                'codigo': 'ERROR_ELIMINACION'
            }), 500
            
    except PartnerNoEncontrado as e:
        return jsonify({
            'error': str(e),
            'codigo': 'PARTNER_NO_ENCONTRADO'
        }), 404
        
    except PartnerEliminado as e:
        return jsonify({
            'error': str(e),
            'codigo': 'PARTNER_YA_ELIMINADO'
        }), 410
        
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'codigo': 'ERROR_INTERNO'
        }), 500

@bp.route('/<partner_id>/kyc', methods=['PUT'])
def verificar_kyc_partner(partner_id):
    """Endpoint para verificar KYC de un partner"""
    try:
        data = request.get_json()
        
        if not data or not data.get('estado_kyc'):
            return jsonify({
                'error': 'Estado KYC es requerido',
                'codigo': 'DATOS_INVALIDOS'
            }), 400
        
        # Validar estado KYC válido
        estados_validos = ['APROBADO', 'RECHAZADO', 'REQUIERE_DOCUMENTOS', 'PENDIENTE']
        if data['estado_kyc'] not in estados_validos:
            return jsonify({
                'error': f'Estado KYC debe ser uno de: {", ".join(estados_validos)}',
                'codigo': 'ESTADO_KYC_INVALIDO'
            }), 400
        
        # Crear DTO
        dto = VerificarKYCDTO(
            estado_kyc=data['estado_kyc'],
            documentos=data.get('documentos'),
            comentarios=data.get('comentarios')
        )
        
        # Verificar KYC
        partner_actualizado = servicio_partners.verificar_kyc_partner(partner_id, dto)
        
        return jsonify({
            'mensaje': 'KYC verificado exitosamente',
            'partner': {
                'id': partner_actualizado.id,
                'nombre': partner_actualizado.nombre,
                'email': partner_actualizado.email,
                'estado_kyc': partner_actualizado.estado_kyc,
                'documentos_kyc': partner_actualizado.documentos_kyc,
                'fecha_actualizacion': partner_actualizado.fecha_actualizacion.isoformat() if partner_actualizado.fecha_actualizacion else None
            }
        }), 200
        
    except PartnerNoEncontrado as e:
        return jsonify({
            'error': str(e),
            'codigo': 'PARTNER_NO_ENCONTRADO'
        }), 404
        
    except PartnerEliminado as e:
        return jsonify({
            'error': str(e),
            'codigo': 'PARTNER_ELIMINADO'
        }), 410
        
    except KYCNoValido as e:
        return jsonify({
            'error': str(e),
            'codigo': 'KYC_INVALIDO'
        }), 400
        
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'codigo': 'ERROR_INTERNO'
        }), 500

@bp.route('/integraciones/<integracion_id>/revocar', methods=['PUT'])
def revocar_integracion(integracion_id):
    """Endpoint para revocar una integración"""
    logger.info(f"Iniciando revocación de integración con ID: {integracion_id}")
    
    try:
        # Log del request recibido
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request headers: {dict(request.headers)}")
        
        data = request.get_json() or {}
        logger.info(f"Datos recibidos: {data}")
        
        # Validar integracion_id
        if not integracion_id:
            logger.error("ID de integración no proporcionado")
            return jsonify({
                'error': 'ID de integración es requerido',
                'codigo': 'DATOS_INVALIDOS'
            }), 400
        
        logger.info(f"Creando DTO para integración {integracion_id}")
        
        # Crear DTO
        dto = RevocarIntegracionDTO(
            integracion_id=integracion_id,
            motivo=data.get('motivo')
        )
        
        logger.info(f"DTO creado exitosamente: {dto}")
        logger.info("Llamando al servicio para revocar integración")
        
        # Revocar integración
        resultado = servicio_partners.revocar_integracion(dto)
        
        logger.info(f"Resultado del servicio: {resultado}")
        
        if resultado:
            logger.info(f"Integración {integracion_id} revocada exitosamente")
            return jsonify({
                'mensaje': 'Integración revocada exitosamente',
                'integracion_id': integracion_id,
                'motivo': data.get('motivo')
            }), 200
        else:
            logger.error(f"El servicio retornó False para integración {integracion_id}")
            return jsonify({
                'error': 'No se pudo revocar la integración',
                'codigo': 'ERROR_REVOCACION'
            }), 500
            
    except IntegracionNoEncontrada as e:
        logger.error(f"Integración no encontrada: {str(e)}")
        return jsonify({
            'error': str(e),
            'codigo': 'INTEGRACION_NO_ENCONTRADA'
        }), 404
        
    except IntegracionYaRevocada as e:
        logger.error(f"Integración ya revocada: {str(e)}")
        return jsonify({
            'error': str(e),
            'codigo': 'INTEGRACION_YA_REVOCADA'
        }), 410
        
    except Exception as e:
        logger.error(f"Error inesperado en revocar_integracion: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'Error interno del servidor: {str(e)}',
            'codigo': 'ERROR_INTERNO'
        }), 500

@bp.route('/<partner_id>', methods=['GET'])
def obtener_partner(partner_id):
    """Endpoint para obtener un partner por ID"""
    try:
        partner = servicio_partners.obtener_partner(partner_id)
        
        return jsonify({
            'partner': {
                'id': partner.id,
                'nombre': partner.nombre,
                'email': partner.email,
                'telefono': partner.telefono,
                'direccion': partner.direccion,
                'estado': partner.estado,
                'estado_kyc': partner.estado_kyc,
                'documentos_kyc': partner.documentos_kyc,
                'fecha_creacion': partner.fecha_creacion.isoformat(),
                'fecha_actualizacion': partner.fecha_actualizacion.isoformat() if partner.fecha_actualizacion else None,
                'integraciones': [
                    {
                        'id': integracion.id,
                        'tipo': integracion.tipo,
                        'nombre': integracion.nombre,
                        'descripcion': integracion.descripcion,
                        'activa': integracion.activa,
                        'fecha_creacion': integracion.fecha_creacion.isoformat(),
                        'fecha_revocacion': integracion.fecha_revocacion.isoformat() if integracion.fecha_revocacion else None
                    }
                    for integracion in partner.integraciones
                ]
            }
        }), 200
        
    except PartnerNoEncontrado as e:
        return jsonify({
            'error': str(e),
            'codigo': 'PARTNER_NO_ENCONTRADO'
        }), 404
        
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'codigo': 'ERROR_INTERNO'
        }), 500

@bp.route('', methods=['GET'])
def listar_partners():
    """Endpoint para listar todos los partners"""
    try:
        partners = servicio_partners.listar_partners()
        
        return jsonify({
            'partners': [
                {
                    'id': partner.id,
                    'nombre': partner.nombre,
                    'email': partner.email,
                    'telefono': partner.telefono,
                    'estado': partner.estado,
                    'estado_kyc': partner.estado_kyc,
                    'fecha_creacion': partner.fecha_creacion.isoformat(),
                    'integraciones_count': len(partner.integraciones)
                }
                for partner in partners
            ],
            'total': len(partners)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'codigo': 'ERROR_INTERNO'
        }), 500

@bp.route('/<partner_id>/integraciones', methods=['POST'])
def crear_integracion(partner_id):
    """Endpoint para crear una nueva integración para un partner"""
    try:
        data = request.get_json()
        
        if not data or not data.get('tipo') or not data.get('nombre'):
            return jsonify({
                'error': 'Tipo y nombre de integración son requeridos',
                'codigo': 'DATOS_INVALIDOS'
            }), 400
        
        # Validar tipo de integración
        tipos_validos = ['API', 'WEBHOOK', 'BATCH', 'REAL_TIME']
        if data['tipo'] not in tipos_validos:
            return jsonify({
                'error': f'Tipo de integración debe ser uno de: {", ".join(tipos_validos)}',
                'codigo': 'TIPO_INTEGRACION_INVALIDO'
            }), 400
        
        # Crear DTO
        dto = CrearIntegracionDTO(
            partner_id=partner_id,
            tipo=data['tipo'],
            nombre=data['nombre'],
            descripcion=data.get('descripcion'),
            configuracion=data.get('configuracion', {})
        )
        
        # Crear integración
        integracion_creada = servicio_partners.crear_integracion(dto)
        
        return jsonify({
            'mensaje': 'Integración creada exitosamente',
            'integracion': {
                'id': integracion_creada.id,
                'partner_id': integracion_creada.partner_id,
                'tipo': integracion_creada.tipo,
                'nombre': integracion_creada.nombre,
                'descripcion': integracion_creada.descripcion,
                'activa': integracion_creada.activa,
                'fecha_creacion': integracion_creada.fecha_creacion.isoformat()
            }
        }), 201
        
    except PartnerNoEncontrado as e:
        return jsonify({
            'error': str(e),
            'codigo': 'PARTNER_NO_ENCONTRADO'
        }), 404
        
    except PartnerEliminado as e:
        return jsonify({
            'error': str(e),
            'codigo': 'PARTNER_ELIMINADO'
        }), 410
        
    except ValueError as e:
        return jsonify({
            'error': str(e),
            'codigo': 'DATOS_INVALIDOS'
        }), 400
        
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'codigo': 'ERROR_INTERNO'
        }), 500
