
from dataclasses import dataclass, field

from alpespartners.seedwork.dominio.entidades import AgregacionRaiz
import alpespartners.modulos.compliance.dominio.objetos_valor as ov

@dataclass
class Payment(AgregacionRaiz):
    partner_id: str = field(default="")
    state: ov.PartnerState = field(default=ov.PartnerState.INACTIVE)
    enable_at: str = field(default="")
    money: ov.Money = field(default=None)
    payment_method: ov.PaymentMethod = field(default=None)
    taxes: list[ov.Tax] = field(default_factory=list)  

    def registrar_partner(self, payment: "Payment"):
        self.partner_id = payment.partner_id
        self.state = payment.state
        self.enable_at = payment.enable_at
        self.money = payment.money
        self.payment_method = payment.payment_method
        self.taxes = payment.taxes