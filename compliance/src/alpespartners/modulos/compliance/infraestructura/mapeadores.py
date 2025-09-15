from alpespartners.seedwork.dominio.repositorio import Mapeador
from alpespartners.modulos.compliance.dominio.entidades import Payment
from .dto import Payment as PaymentDTO
import logging 

logging = logging.getLogger(__name__)

class MapeadorCompliance(Mapeador):
    _FORMATO_FECHA = "%Y-%m-%dT%H:%M:%SZ"

    def entidad_a_dto(self, entidad: Payment) -> PaymentDTO:
        logging.debug(f"Convirtiendo entidad a DTO: {entidad}")
        payment_dto = PaymentDTO()
        payment_dto.payment_id = entidad.id
        payment_dto.partner_id = entidad.partner_id
        payment_dto.state = entidad.state
        payment_dto.enable_at = entidad.enable_at
        return payment_dto
        

    def dto_a_entidad(self, dto: PaymentDTO) -> Payment:
        logging.debug(f"Convirtiendo DTO a entidad: {dto}")
        payment = Payment()
        payment.id = dto.payment_id
        payment.partner_id = dto.partner_id
        payment.state = dto.state
        payment.enable_at = dto.enable_at
        return payment

    def obtener_tipo(self) -> type:
        return Payment.__class__

    