
"""
Coordinador de saga coreográfico para el proceso de partners y contratos
"""
import sys
import os
import logging

# Agregar paths para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from seedwork.aplicacion.sagas import CoordinadorCoreografia, Transaccion, Inicio, Fin
from seedwork.aplicacion.comandos import Comando
from seedwork.dominio.eventos import EventoDominio

# Importar eventos específicos de partners y contratos
from modulos.sagas.dominio.eventos import (
    CreatePartner, PartnerCreated, PartnerCreationFailed,
    ContratoCreado, ContratoCreadoFailed
)

logger = logging.getLogger(__name__)


class CoordinadorPartnersCoreografico(CoordinadorCoreografia):
    """
    Coordinador de saga coreográfico para el proceso de partners y contratos.
    En coreografía, cada servicio sabe qué hacer cuando recibe un evento específico,
    sin un coordinador central que dirija el flujo.
    """

    def __init__(self):
        self.estado_saga = {}  # Para trackear el estado de cada saga por partner_id
        self.inicializar_pasos()

    def inicializar_pasos(self):
        """
        Define las reglas de coreografía - qué eventos pueden seguir a otros
        """
        self.reglas_coreografia = {
            CreatePartner: [PartnerCreated, PartnerCreationFailed],
            PartnerCreated: [ContratoCreado, ContratoCreadoFailed],
            PartnerCreationFailed: [],  # Fin de saga en caso de error
            ContratoCreado: [],  # Fin exitoso de saga
            ContratoCreadoFailed: []  # Fin de saga en caso de error
        }
        logger.info("� Initialized choreography rules for partner-contract saga")

    def iniciar(self, partner_id: str):
        """Inicia una nueva saga para un partner"""
        logger.info(f"🚀 Starting choreographic saga for partner: {partner_id}")
        self.estado_saga[partner_id] = {
            'estado': 'INICIADA',
            'eventos': [],
            'timestamp': None
        }

    def terminar(self, partner_id: str, exitoso: bool = True):
        """Termina la saga para un partner"""
        estado_final = 'COMPLETADA' if exitoso else 'FALLIDA'
        logger.info(f"🏁 Partner saga {estado_final.lower()} for: {partner_id}")
        
        if partner_id in self.estado_saga:
            self.estado_saga[partner_id]['estado'] = estado_final
            self.persistir_en_saga_log(f"Saga {estado_final} para partner: {partner_id}")

    def persistir_en_saga_log(self, mensaje):
        """
        Persiste el estado de la saga en logs
        TODO: Implementar persistencia en base de datos
        """
        logger.info(f"📝 Choreography log: {mensaje}")

    def construir_comando(self, evento: EventoDominio, tipo_comando: type):
        """
        En coreografía, cada servicio maneja sus propios comandos
        """
        logger.info(f"🔄 Event received in choreography: {type(evento).__name__}")
        return None

    def puede_procesar_evento(self, evento_anterior: type, evento_actual: type) -> bool:
        """
        Verifica si un evento puede seguir a otro según las reglas de coreografía
        """
        if evento_anterior is None:
            return isinstance(evento_actual, type) and evento_actual == CreatePartner
        
        return evento_actual in self.reglas_coreografia.get(evento_anterior, [])

    def procesar_evento(self, evento: EventoDominio):
        """
        Procesa eventos en la saga coreográfica
        Cada evento desencadena acciones específicas sin coordinación central
        """
        logger.info(f"📨 Processing choreographic event: {type(evento).__name__}")
        
        try:
            partner_id = getattr(evento, 'partner_id', 'unknown')
            
            # Registrar evento en el estado de la saga
            if partner_id not in self.estado_saga:
                self.iniciar(partner_id)
            
            self.estado_saga[partner_id]['eventos'].append(type(evento).__name__)
            
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
                
            else:
                logger.warning(f"⚠️  Unknown event type in choreographic saga: {type(evento).__name__}")
                
        except Exception as e:
            logger.error(f"💥 Error processing choreographic event: {e}")
            raise

    def _procesar_create_partner(self, evento: CreatePartner):
        """
        Procesa evento CreatePartner - punto de inicio de la saga
        """
        logger.info(f"🎯 [CHOREOGRAPHY] CreatePartner received for: {evento.partner_id}")
        logger.info(f"⏭️  Next expected: PartnerCreated or PartnerCreationFailed")
        
        # En coreografía, este evento desencadenaría la creación del partner
        # en el servicio correspondiente, pero aquí solo lo registramos

    def _procesar_partner_created(self, evento: PartnerCreated):
        """
        Procesa evento PartnerCreated - partner creado exitosamente
        """
        logger.info(f"✅ [CHOREOGRAPHY] PartnerCreated received for: {evento.partner_id}")
        logger.info(f"⏭️  Next expected: ContratoCreado or ContratoCreadoFailed")
        
        # En coreografía, este evento desencadenaría la creación del contrato
        # en el servicio de contratos

    def _procesar_partner_creation_failed(self, evento: PartnerCreationFailed):
        """
        Procesa evento PartnerCreationFailed - falló la creación del partner
        """
        logger.error(f"❌ [CHOREOGRAPHY] PartnerCreationFailed for: {evento.partner_id}")
        logger.error(f"🚫 Error: {evento.error_message}")
        logger.info("🔚 Saga terminates due to partner creation failure")
        
        self.terminar(evento.partner_id, exitoso=False)

    def _procesar_contrato_creado(self, evento: ContratoCreado):
        """
        Procesa evento ContratoCreado - contrato creado exitosamente
        """
        logger.info(f"✅ [CHOREOGRAPHY] ContratoCreado received for partner: {evento.partner_id}")
        logger.info(f"📄 Contract ID: {evento.contrato_id}, Amount: {evento.monto} {evento.moneda}")
        logger.info("🎉 Saga completed successfully!")
        
        self.terminar(evento.partner_id, exitoso=True)

    def _procesar_contrato_creado_failed(self, evento: ContratoCreadoFailed):
        """
        Procesa evento ContratoCreadoFailed - falló la creación del contrato
        """
        logger.error(f"❌ [CHOREOGRAPHY] ContratoCreadoFailed for partner: {evento.partner_id}")
        logger.error(f"📄 Contract ID: {evento.contrato_id}")
        logger.error(f"� Error: {evento.error_message}")
        logger.info("🔚 Saga terminates due to contract creation failure")
        
        self.terminar(evento.partner_id, exitoso=False)

    def obtener_estado_saga(self, partner_id: str) -> dict:
        """
        Obtiene el estado actual de la saga para un partner
        """
        return self.estado_saga.get(partner_id, {})


# Listener function para redireccionar eventos de dominio
def oir_mensaje(mensaje):
    """
    Función listener que redirige eventos de dominio a la saga coreográfica
    """
    logger.info(f"👂 Received choreographic message: {type(mensaje).__name__}")
    
    if isinstance(mensaje, EventoDominio):
        coordinador = CoordinadorPartnersCoreografico()
        coordinador.procesar_evento(mensaje)
    else:
        error_msg = f"El mensaje no es evento de Dominio: {type(mensaje)}"
        logger.error(error_msg)
        raise NotImplementedError(error_msg)
