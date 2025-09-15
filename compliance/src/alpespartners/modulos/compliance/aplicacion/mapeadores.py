from datetime import datetime
from alpespartners.modulos.compliance.dominio.entidades import Payment
from alpespartners.seedwork.aplicacion.dto import Mapeador as AppMap
from alpespartners.seedwork.dominio.repositorio import Mapeador as RepMap
from .dto import PaymentDTO

class MapeadorComplianceDTOJson(AppMap):
    def externo_a_dto(self, externo: dict) -> PaymentDTO:
        partnerId = externo.get("partner_id", "")
        state = externo.get("state", "ACTIVE")
        enable_at = externo.get("enable_at")
        if enable_at:
            if isinstance(enable_at, str):
                enable_at = datetime.fromisoformat(enable_at.replace('Z', '+00:00'))

        payment_dto = PaymentDTO(
            payment_id=externo.get("payment_id", ""),
            partnerId=partnerId,
            state=state,
            enable_at=enable_at if enable_at else datetime.now()
        )
        return payment_dto

    def dto_a_externo(self, dto: dict) -> dict:
        # Aquí se puede implementar la lógica para mapear el DTO específico a un dict externo si es necesario
        return dto

class MapeadorPayment(RepMap):    
    _FORMATO_FECHA = "%Y-%m-%dT%H:%M:%SZ"

    def obtener_tipo(self) -> type:
        return Payment.__class__

    def entidad_a_dto(self, externo: dict) -> PaymentDTO:
        payment_dto = PaymentDTO(
            payment_id=externo.get("payment_id", ""),
            partnerId=externo.get("partner_id", ""),
            state=externo.get("state", ""),
            enable_at=externo.get("enable_at", "")
        )
        return payment_dto

    def dto_a_entidad(self, dto: PaymentDTO) -> Payment:
        return Payment(
            partner_id=dto.partnerId,
            state=dto.state,
            enable_at=dto.enable_at
        )