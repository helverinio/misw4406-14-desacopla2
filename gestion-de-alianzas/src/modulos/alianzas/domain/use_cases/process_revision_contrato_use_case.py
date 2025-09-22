# process_revision_contrato_use_case.py

import logging
from typing import Optional
from src.modulos.alianzas.domain.use_cases.base_use_case import BaseUseCase
from src.modulos.alianzas.domain.ports.contrato_repository_port import ContratoRepositoryPort
from src.modulos.alianzas.domain.models.contrato import Contrato, EstadoContrato

logger = logging.getLogger(__name__)


class ProcessRevisionContratoUseCase(BaseUseCase):
    """Use case para procesar evento revision-contrato."""

    def __init__(self, contrato_repository: ContratoRepositoryPort):
        self.contrato_repository = contrato_repository

    async def execute(self, partner_id: str, comentarios_revision: str = None) -> Optional[Contrato]:
        """
        Procesa el evento revision-contrato:
        1. Busca el contrato por partner_id
        2. Actualiza el estado a RECHAZADO
        3. Guarda los comentarios de revisión si están disponibles
        """
        try:
            logger.info(f"🔄 Processing revision-contrato for partner: {partner_id}")
            
            # Buscar el contrato por partner_id
            contrato = await self.contrato_repository.get_by_partner_id(partner_id)
            
            if not contrato:
                logger.warning(f"⚠️ No contrato found for partner_id: {partner_id}")
                return None
            
            logger.info(f"📄 Found contrato: {contrato.id} for partner: {partner_id}")
            logger.info(f"📊 Current estado: {contrato.estado}")
            
            # Actualizar el estado a RECHAZADO
            contrato.estado = EstadoContrato.RECHAZADO
            
            # Si hay comentarios de revisión, agregarlos a las condiciones
            if comentarios_revision:
                revision_note = f"REVISION: {comentarios_revision}"
                if contrato.condiciones:
                    contrato.condiciones = f"{contrato.condiciones}. {revision_note}"
                else:
                    contrato.condiciones = revision_note
            
            # Guardar el contrato actualizado
            contrato_actualizado = await self.contrato_repository.update(contrato)
            
            logger.info(f"✅ Contrato {contrato_actualizado.id} updated to estado: {contrato_actualizado.estado}")
            logger.info(f"🔄 Revision processing completed for partner: {partner_id}")
            
            return contrato_actualizado
            
        except Exception as e:
            logger.error(f"❌ Error processing revision-contrato for partner {partner_id}: {e}")
            raise