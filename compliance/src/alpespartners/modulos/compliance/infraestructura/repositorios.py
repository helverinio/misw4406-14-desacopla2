
from alpespartners.modulos.compliance.dominio.repositorios import RepositorioCompliance
from alpespartners.modulos.compliance.dominio.fabricas  import FabricaCompliance
from alpespartners.modulos.compliance.dominio.fabricas  import FabricaCompliance
from alpespartners.modulos.compliance.dominio.entidades import Payment
from alpespartners.config.db import db
from .mapeadores import MapeadorCompliance
from .dto import Payment as PaymentDTO
import logging

logging = logging.getLogger(__name__)

class RepositorioPaymentPostgress(RepositorioCompliance):
    def __init__(self):
        self._fabrica_compliance: FabricaCompliance = FabricaCompliance()
    
    @property
    def fabrica_payment(self):
        return self._fabrica_compliance

    def agregar(self, payment: Payment):
        logging.info(f"Agregando payment: {payment}")
        payment_dto = self._fabrica_compliance.crear_objeto(payment, MapeadorCompliance())
        logging.info(f"Payment DTO creado: {payment_dto}")
        db.session.add(payment_dto)
        db.session.commit()
    
    def obtener_por_id(self, id: str) -> Payment:
        payment_dto = db.session.query(PaymentDTO).filter_by(partner_id=id).one()
        return self._fabrica_compliance.crear_objeto(payment_dto, MapeadorCompliance())
    
    def obtener_por_partner_id(self, partner_id: str) -> Payment:
        payment_dto = db.session.query(PaymentDTO).filter_by(partner_id=partner_id).one()
        return self._fabrica_compliance.crear_objeto(payment_dto, MapeadorCompliance())