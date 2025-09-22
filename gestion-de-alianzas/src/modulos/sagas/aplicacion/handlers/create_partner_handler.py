"""
Handler para eventos CreatePartner en la saga
"""
import logging
from datetime import datetime
import sys
import os

# Agregar paths para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from src.seedwork.aplicacion.handlers import Handler
from src.modulos.sagas.dominio.eventos import CreatePartner, PartnerCreated, PartnerCreationFailed

logger = logging.getLogger(__name__)


class CreatePartnerHandler(Handler):
    
    def handle(self, evento: CreatePartner):
        logger.info(f"🎯 Processing CreatePartner event for partner_id: {evento.partner_id}")
        
        try:
            # Validar que el partner_id sea válido
            if not evento.partner_id or len(evento.partner_id) < 3:
                raise ValueError("partner_id debe tener al menos 3 caracteres")
            
            logger.info(f"✨ Creating partner with ID: {evento.partner_id}")
            logger.info(f"✅ Partner {evento.partner_id} created successfully")
            
            # Generar evento de éxito
            return PartnerCreated(
                partner_id=evento.partner_id,
                fecha_evento=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to create partner {evento.partner_id}: {e}")
            
            # Generar evento de fallo
            return PartnerCreationFailed(
                partner_id=evento.partner_id,
                error_message=str(e),
                fecha_evento=datetime.now()
            )


def crear_partner_handler():
    return CreatePartnerHandler()