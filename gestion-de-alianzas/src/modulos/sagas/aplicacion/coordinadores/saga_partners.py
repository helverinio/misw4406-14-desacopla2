
import sys
import os
import logging

# Agregar paths para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from seedwork.aplicacion.sagas import CoordinadorOrquestacion, Transaccion, Inicio, Fin
from seedwork.aplicacion.comandos import Comando
from seedwork.dominio.eventos import EventoDominio

# Importar eventos específicos de partners
from modulos.sagas.dominio.eventos.partners import CreatePartner, PartnerCreated, PartnerCreationFailed

logger = logging.getLogger(__name__)


class CoordinadorPartners(CoordinadorOrquestacion):

    def inicializar_pasos(self):
        self.pasos = [
            Inicio(index=0),
            # Paso 1: Crear el partner básico
            Transaccion(
                index=1, 
                comando=None,  # Por ahora None, luego implementaremos comandos específicos
                evento=PartnerCreated, 
                error=PartnerCreationFailed, 
                compensacion=None
            ),
            Fin(index=2)
        ]
        logger.info(f"🎯 Initialized saga steps for partner coordination")

    def iniciar(self):
        logger.info("🚀 Starting partner saga")
        self.persistir_en_saga_log(self.pasos[0])
        # La saga se iniciará cuando reciba el evento CreatePartner
    
    def terminar(self):
        logger.info("🏁 Partner saga completed")
        self.persistir_en_saga_log(self.pasos[-1])

    def persistir_en_saga_log(self, mensaje):
        logger.info(f"📝 Saga log: {type(mensaje).__name__} - {mensaje}")

    def construir_comando(self, evento: EventoDominio, tipo_comando: type):
        # Por ahora implementación básica
        logger.info(f"🔄 Building command {tipo_comando} from event {type(evento).__name__}")
        # TODO: Implementar lógica específica de transformación
        return None
    
    def procesar_evento(self, evento: EventoDominio):
        logger.info(f"📨 Processing event: {type(evento).__name__}")
        
        try:
            if isinstance(evento, CreatePartner):
                logger.info(f"🎯 Starting partner creation saga for partner_id: {evento.partner_id}")
                self.iniciar()

                logger.info(f"✨ Partner creation initiated for: {evento.partner_id}")
                
                # TODO Simular éxito (en una implementación real, esto vendría del handler)
                evento_exitoso = PartnerCreated(
                    partner_id=evento.partner_id
                )
                logger.info(f"✅ Partner created successfully: {evento.partner_id}")
                self.terminar()
                
            elif isinstance(evento, PartnerCreated):
                logger.info(f"✅ Partner creation confirmed: {evento.partner_id}")
                self.terminar()
                
            elif isinstance(evento, PartnerCreationFailed):
                logger.error(f"❌ Partner creation failed: {evento.partner_id} - {evento.error_message}")
                self.terminar()
                
            else:
                logger.warning(f"⚠️  Unknown event type in partner saga: {type(evento).__name__}")
                
        except Exception as e:
            logger.error(f"💥 Error processing event in partner saga: {e}")
            raise


# Listener function para redireccionar eventos de dominio
def oir_mensaje(mensaje):
    logger.info(f"👂 Received message: {type(mensaje).__name__}")
    
    if isinstance(mensaje, EventoDominio):
        coordinador = CoordinadorPartners()
        coordinador.procesar_evento(mensaje)
    else:
        error_msg = f"El mensaje no es evento de Dominio: {type(mensaje)}"
        logger.error(error_msg)
        raise NotImplementedError(error_msg)
