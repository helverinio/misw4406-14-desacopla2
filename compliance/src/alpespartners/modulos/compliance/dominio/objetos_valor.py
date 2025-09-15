

from dataclasses import dataclass
from enum import Enum

from alpespartners.seedwork.dominio.objetos_valor import ObjetoValor

class PartnerState(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"

class PaymentType(Enum):
    CREDIT_CARD = "CREDIT_CARD"
    BANK_TRANSFER = "BANK_TRANSFER"
    PAYPAL = "PAYPAL"

@dataclass(frozen=True)
class Money(ObjetoValor):
    amount: float
    currency: str

@dataclass(frozen=True)
class PaymentMethod(ObjetoValor):
    type: str

@dataclass(frozen=True)
class Tax(ObjetoValor):
    rate: str
    amount: Money