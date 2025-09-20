
from alpespartners.modulos.compliance.dominio.repositorios import RepositorioCompliance
from alpespartners.modulos.compliance.dominio.fabricas  import FabricaCompliance
from alpespartners.modulos.compliance.dominio.entidades import Payment
from alpespartners.config.db import db
from .mapeadores import MapeadorCompliance
from .dto import Payment as PaymentDTO
import logging

logger = logging.getLogger(__name__)

class RepositorioPaymentPostgress(RepositorioCompliance):
    def __init__(self):
        self._fabrica_compliance: FabricaCompliance = FabricaCompliance()
    
    @property
    def fabrica_payment(self):
        return self._fabrica_compliance

    def agregar(self, payment: Payment):
        logger.info(f"Agregando payment: {payment}")
        payment_dto = self._fabrica_compliance.crear_objeto(payment, MapeadorCompliance())
        logger.info(f"Payment DTO creado: {payment_dto}")
        db.session.add(payment_dto)
        db.session.commit()
    
    def obtener_por_id(self, id: str) -> Payment:
        payment_dto = db.session.query(PaymentDTO).filter_by(partner_id=id).one()
        return self._fabrica_compliance.crear_objeto(payment_dto, MapeadorCompliance())
    
    def obtener_por_partner_id(self, partner_id: str) -> Payment:
        payment_dto = db.session.query(PaymentDTO).filter_by(partner_id=partner_id).one()
        return self._fabrica_compliance.crear_objeto(payment_dto, MapeadorCompliance())
    
    def actualizar(self, payment: Payment):
        logger.info(f"Actualizando payment: {payment}")
        
        # Convertir entidad a DTO
        payment_dto_data = self._fabrica_compliance.crear_objeto(payment, MapeadorCompliance())
        
        # Buscar el registro existente en la BD
        payment_existente = db.session.query(PaymentDTO).filter_by(partner_id=payment.partner_id).first()
        
        if payment_existente:
            # Actualizar campos
            payment_existente.state = payment_dto_data.state
            payment_existente.enable_at = payment_dto_data.enable_at
            payment_existente.money = payment_dto_data.money
            payment_existente.payment_method = payment_dto_data.payment_method
            payment_existente.taxes = payment_dto_data.taxes
            
            db.session.commit()
            logger.info(f"Payment {payment.partner_id} actualizado exitosamente")
        else:
            logger.error(f"Payment {payment.partner_id} no encontrado para actualizar")
            raise ValueError(f"Payment con partner_id {payment.partner_id} no encontrado")