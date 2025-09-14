
from alpespartners.modulos.compliance.dominio.repositorios import RepositorioCompliance
from alpespartners.modulos.compliance.dominio.fabricas  import FabricaCompliance
from alpespartners.modulos.compliance.dominio.fabricas  import FabricaCompliance
from alpespartners.modulos.programas.dominio.repositorios import RepositorioProgramas
from alpespartners.modulos.compliance.dominio.entidades import Payment
from alpespartners.config.db import db

class RepositorioPaymentPostgress(RepositorioCompliance):
    def __init__(self):
        self._fabrica_compliance: FabricaCompliance = FabricaCompliance()
    
    @property
    def fabrica_payment(self):
        return self._fabrica_compliance

    def registerPartner(self, payment: Payment):
        payment_dto = self._fabrica_compliance.crear_objeto(payment, MapeadorPayment())
        db.session.add(payment_dto)
        db.session.commit()