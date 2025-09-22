
"""
Coordinador de saga coreográfico para el proceso de partners y contratos
"""
import sys
import os
import logging
import uuid
from typing import Optional

# Agregar paths para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from seedwork.aplicacion.sagas import CoordinadorCoreografia, Transaccion, Inicio, Fin
from seedwork.aplicacion.comandos import Comando
from seedwork.dominio.eventos import EventoDominio

# Importar eventos específicos de partners y contratos
from modulos.sagas.dominio.eventos import (
    CreatePartner, PartnerCreated, PartnerCreationFailed,
    ContratoCreado, ContratoCreadoFailed,
    ContratoAprobado, ContratoRechazado, RevisionContrato
)

from modulos.sagas.aplicacion.servicios.saga_log_service import SagaLogService
from modulos.sagas.infraestructura.repositorios.saga_log_repository import SagaLogRepository

logger = logging.getLogger(__name__)


class CoordinadorPartnersCoreografico(CoordinadorCoreografia):

    def __init__(self, saga_log_service=None):
        self.estado_saga = {} 
        
        if saga_log_service is None:
            try:
                repository = SagaLogRepository()
                self.saga_log_service = SagaLogService(repository)
                logger.info("✅ Saga log service initialized directly")
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize saga log service, continuing without DB logging: {e}")
                self.saga_log_service = None
        else:
            self.saga_log_service = saga_log_service
            
        self.inicializar_pasos()

    def inicializar_pasos(self):
        """
        Define las reglas de coreografía - qué eventos pueden seguir a otros
        """
        self.reglas_coreografia = {
            CreatePartner: [PartnerCreated, PartnerCreationFailed],
            PartnerCreated: [ContratoCreado, ContratoCreadoFailed],
            PartnerCreationFailed: [],  # Fin de saga en caso de error
            ContratoCreado: [ContratoAprobado, ContratoRechazado],  # Compliance después del contrato
            ContratoCreadoFailed: [],  # Fin de saga en caso de error
            ContratoAprobado: [],  # Fin exitoso de saga - contrato aprobado
            ContratoRechazado: [RevisionContrato],  # Si se rechaza, se puede revisar
            RevisionContrato: []  # Fin de saga - pendiente de revisión manual
        }
        logger.info("� Initialized choreography rules for partner-contract saga")

    def iniciar(self, partner_id: str):
        """Inicia una nueva saga para un partner"""
        saga_id = str(uuid.uuid4())
        logger.info(f"🚀 Starting choreographic saga for partner: {partner_id} (saga_id: {saga_id})")
        
        self.estado_saga[partner_id] = {
            'saga_id': saga_id,
            'estado': 'INICIADA',
            'eventos': [],
            'timestamp': None
        }
        
        # Registrar inicio de saga en el log
        if self.saga_log_service:
            try:
                self.saga_log_service.registrar_evento_recibido(
                    saga_id=saga_id,
                    tipo_evento="SAGA_INICIADA",
                    evento_data={"partner_id": partner_id, "action": "saga_start"}
                )
                logger.info(f"📝 Saga iniciada registrada en BD: {saga_id}")
            except Exception as e:
                logger.error(f"❌ Error registrando inicio de saga: {e}")

    def terminar(self, partner_id: str, exitoso: bool = True):
        """Termina la saga para un partner"""
        estado_final = 'COMPLETADA' if exitoso else 'FALLIDA'
        
        # Validar que la saga existe y no está ya finalizada
        if partner_id not in self.estado_saga:
            logger.warning(f"⚠️ Intentando terminar saga inexistente para partner: {partner_id}")
            return
        
        estado_actual = self.estado_saga[partner_id].get('estado', 'INICIADA')
        if estado_actual in ['COMPLETADA', 'FALLIDA']:
            logger.warning(f"⚠️ Saga ya finalizada para partner {partner_id} en estado: {estado_actual}")
            return
        
        logger.info(f"🏁 Partner saga {estado_final.lower()} for: {partner_id}")
        
        saga_id = self.estado_saga[partner_id].get('saga_id')
        self.estado_saga[partner_id]['estado'] = estado_final
        
        # Registrar fin de saga en el log
        if self.saga_log_service and saga_id:
            try:
                self.saga_log_service.registrar_evento_recibido(
                    saga_id=saga_id,
                    tipo_evento="SAGA_FINALIZADA",
                    evento_data={
                        "partner_id": partner_id, 
                        "estado_final": estado_final,
                        "exitoso": exitoso
                    }
                )
                logger.info(f"📝 Finalización de saga registrada en BD: {saga_id}")
            except Exception as e:
                logger.error(f"❌ Error registrando finalización de saga: {e}")

    def persistir_en_saga_log(self, mensaje):
        logger.info(f"📝 Choreography log: {mensaje}")

    def construir_comando(self, evento: EventoDominio, tipo_comando: type):
        logger.info(f"🔄 Event received in choreography: {type(evento).__name__}")
        return None

    def puede_procesar_evento(self, evento_anterior: type, evento_actual: type) -> bool:
        if evento_anterior is None:
            return isinstance(evento_actual, type) and evento_actual == CreatePartner
        
        return evento_actual in self.reglas_coreografia.get(evento_anterior, [])

    def procesar_evento(self, evento: EventoDominio):
        logger.info(f"📨 Processing choreographic event: {type(evento).__name__}")
        
        try:
            # Validar que el evento es realmente un objeto EventoDominio
            if not hasattr(evento, 'partner_id'):
                logger.error(f"💥 Error: received object without partner_id attribute. Type: {type(evento)}, Value: {evento}")
                raise ValueError(f"Event object must have partner_id attribute. Received: {type(evento)} - {evento}")
            
            partner_id = getattr(evento, 'partner_id', 'unknown')
            logger.info(f"🆔 Partner ID extracted: {partner_id}")

            if isinstance(evento, CreatePartner):
                logger.info(f"📝 CreatePartner recibido - solo logging: {partner_id}")
                self._log_evento_sin_saga(evento)
                self._procesar_evento_interno(evento)
                return
            
            if partner_id not in self.estado_saga:
                if isinstance(evento, PartnerCreated):
                    self.iniciar(partner_id)  # Usar el ID real del partner creado
                    logger.info(f"🚀 Saga iniciada por PartnerCreated para partner: {partner_id}")
            
            saga_id = self.estado_saga[partner_id].get('saga_id')
            self.estado_saga[partner_id]['eventos'].append(type(evento).__name__)
            
            # Registrar evento en el saga log si el servicio está disponible
            if self.saga_log_service and saga_id:
                try:
                    evento_data = {
                        'partner_id': partner_id, 
                        'evento_tipo': type(evento).__name__,
                        'timestamp': str(getattr(evento, 'fecha_evento', 'N/A'))
                    }
                    
                    if hasattr(evento, 'contrato_id'):
                        evento_data['contrato_id'] = getattr(evento, 'contrato_id', None)
                    if hasattr(evento, 'monto'):
                        evento_data['monto'] = getattr(evento, 'monto', None)
                    if hasattr(evento, 'error_message'):
                        evento_data['error_message'] = getattr(evento, 'error_message', None)
                    
                    self.saga_log_service.registrar_evento_recibido(
                        saga_id=saga_id,
                        tipo_evento=type(evento).__name__,
                        evento_data=evento_data
                    )
                    logger.info(f"📝 Evento {type(evento).__name__} registrado en BD para saga: {saga_id}")
                    
                except Exception as e:
                    # Warning en lugar de error para que continúe el procesamiento
                    logger.warning(f"⚠️ Base de datos no disponible para logging de saga, continuando procesamiento: {e}")
                    logger.info(f"📄 Evento {type(evento).__name__} procesado en memoria para saga: {saga_id}")
            
            # Procesar el evento normalmente
            self._procesar_evento_interno(evento)
                
        except Exception as e:
            logger.error(f"💥 Error processing choreographic event: {type(e).__name__}: {str(e)}")
            logger.error(f"📍 Event type: {type(evento).__name__} for partner: {getattr(evento, 'partner_id', 'unknown')}")
            raise

    def _procesar_evento_interno(self, evento: EventoDominio):
        """Procesamiento interno del evento sin logging"""
        try:
            if isinstance(evento, CreatePartner):
                self._procesar_create_partner(evento)
                
            elif isinstance(evento, PartnerCreated):
                self._procesar_partner_created(evento)
                
            elif isinstance(evento, PartnerCreationFailed):
                self._procesar_partner_creation_failed(evento)
                
            elif isinstance(evento, ContratoCreado):
                self._procesar_contrato_creado(evento)
                
            elif isinstance(evento, ContratoCreadoFailed):
                self._procesar_contrato_creado_failed(evento)
                
            elif isinstance(evento, ContratoAprobado):
                self._procesar_contrato_aprobado(evento)
                
            elif isinstance(evento, ContratoRechazado):
                self._procesar_contrato_rechazado(evento)
                
            elif isinstance(evento, RevisionContrato):
                self._procesar_revision_contrato(evento)
                
            else:
                logger.warning(f"⚠️  Unknown event type in choreographic saga: {type(evento).__name__}")
                
        except Exception as e:
            logger.error(f"💥 Error in _procesar_evento_interno for {type(evento).__name__}: {type(e).__name__}: {str(e)}")
            raise

    def _procesar_create_partner(self, evento: CreatePartner):
        logger.info(f"📝 [CHOREOGRAPHY] CreatePartner received: {evento.partner_id}")
        logger.info(f"📄 Partner data: {evento.partner_id}")
        logger.info(f"⏭️ Waiting for PartnerCreated to start saga")
        

    def _procesar_partner_created(self, evento: PartnerCreated):
        logger.info(f"✅ [CHOREOGRAPHY] PartnerCreated received for: {evento.partner_id}")
        logger.info(f"⏭️  Next expected: ContratoCreado or ContratoCreadoFailed")

    def _procesar_partner_creation_failed(self, evento: PartnerCreationFailed):
        logger.error(f"❌ [CHOREOGRAPHY] PartnerCreationFailed for: {evento.partner_id}")
        logger.error(f"🚫 Error: {evento.error_message}")
        logger.info("🔚 Saga terminates due to partner creation failure")
        
        self.terminar(evento.partner_id, exitoso=False)

    def _procesar_contrato_creado(self, evento: ContratoCreado):
        logger.info(f"✅ [CHOREOGRAPHY] ContratoCreado received for partner: {evento.partner_id}")
        logger.info(f"📄 Contract ID: {evento.contrato_id}, Amount: {evento.monto} {evento.moneda}")
        logger.info("⏭️  Next expected: ContratoAprobado or ContratoRechazado (from compliance)")

    def _procesar_contrato_creado_failed(self, evento: ContratoCreadoFailed):
        logger.error(f"❌ [CHOREOGRAPHY] ContratoCreadoFailed for partner: {evento.partner_id}")
        logger.error(f"📄 Contract ID: {evento.contrato_id}")
        logger.error(f"� Error: {evento.error_message}")
        logger.info("🔚 Saga terminates due to contract creation failure")
        
        self.terminar(evento.partner_id, exitoso=False)

    def _procesar_contrato_aprobado(self, evento: ContratoAprobado):
        logger.info(f"✅ [CHOREOGRAPHY] ContratoAprobado received for partner: {evento.partner_id}")
        logger.info(f"📄 Contract ID: {evento.contrato_id}")
        logger.info(f"🔍 Compliance validation passed")
        logger.info("🎉 Saga completed successfully!")
        
        self.terminar(evento.partner_id, exitoso=True)

    def _procesar_contrato_rechazado(self, evento: ContratoRechazado):
        logger.error(f"❌ [CHOREOGRAPHY] ContratoRechazado for partner: {evento.partner_id}")
        logger.error(f"📄 Contract ID: {evento.contrato_id}")
        logger.error(f"🔍 Compliance rejection reason: {evento.causa_rechazo}")
        logger.info("🔚 Saga terminates due to compliance rejection")
        
        self.terminar(evento.partner_id, exitoso=False)

    def _procesar_revision_contrato(self, evento: RevisionContrato):
        logger.warning(f"⚠️ [CHOREOGRAPHY] RevisionContrato for partner: {evento.partner_id}")
        logger.warning(f"📄 Contract ID: {evento.contrato_id}")
        logger.warning(f"🔍 Revision required due to: {evento.causa_rechazo_original}")
        logger.warning(f"⚠️ Validation failed: {evento.validacion_fallida}")
        logger.info("⏳ Saga maintains PENDING_REVISION state - awaiting manual intervention")
        logger.info("⏭️ Next expected: Manual resolution or new ContratoAprobado/ContratoRechazado")

    def obtener_estado_saga(self, partner_id: str) -> dict:
        return self.estado_saga.get(partner_id, {})
    
    def obtener_historial_saga(self, partner_id: str) -> list:
        if not self.saga_log_service:
            return []
        
        saga_data = self.estado_saga.get(partner_id, {})
        saga_id = saga_data.get('saga_id')
        
        if saga_id:
            return self.saga_log_service.obtener_historial_saga(saga_id)
        return []

    def _log_evento_sin_saga(self, evento: EventoDominio):
        """Log evento sin saga con manejo robusto de errores de conectividad"""
        if self.saga_log_service:
            try:
                # Generar un ID único para este evento sin saga
                evento_id = str(uuid.uuid4())
                
                evento_data = {
                    'partner_id': getattr(evento, 'partner_id', 'unknown'),
                    'evento_tipo': type(evento).__name__,
                    'timestamp': str(getattr(evento, 'fecha_evento', 'N/A')),
                    'sin_saga': True  # Marcar que este evento no tiene saga asociada
                }
                
                self.saga_log_service.registrar_evento_recibido(
                    saga_id=evento_id,  # Usar evento_id como saga_id para eventos sin saga
                    tipo_evento=type(evento).__name__,
                    evento_data=evento_data
                )
                logger.info(f"📝 Evento {type(evento).__name__} registrado en BD sin saga: {evento_id}")
                
            except Exception as e:
                # Log del error pero continuar el procesamiento
                logger.warning(f"⚠️ Base de datos no disponible para logging, continuando procesamiento: {e}")
                logger.info(f"📄 Evento {type(evento).__name__} procesado en memoria para partner: {getattr(evento, 'partner_id', 'unknown')}")
        else:
            # Si no hay servicio de logging, solo hacer log en console
            logger.info(f"📄 Evento {type(evento).__name__} procesado sin persistencia para partner: {getattr(evento, 'partner_id', 'unknown')}")

def oir_mensaje(mensaje, saga_log_service=None):
    logger.info(f"👂 Received choreographic message: {type(mensaje).__name__}")
    
    if isinstance(mensaje, EventoDominio):
        coordinador = CoordinadorPartnersCoreografico(saga_log_service)
        coordinador.procesar_evento(mensaje)
    else:
        error_msg = f"El mensaje no es evento de Dominio: {type(mensaje)}"
        logger.error(error_msg)
        raise NotImplementedError(error_msg)
