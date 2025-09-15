from dataclasses import dataclass, field
from alpespartners.seedwork.aplicacion.dto import DTO



@dataclass(frozen=True)
class Money(DTO):
    amount: float = field(default_factory=float)
    currency: str = field(default_factory=str)

@dataclass(frozen=True)
class PaymentMethod(DTO):
    type: str = field(default_factory=str)

@dataclass(frozen=True)
class Tax(DTO):
    rate: str = field(default_factory=str)
    amount: Money = field(default_factory=Money)

@dataclass(frozen=True)
class PaymentDTO(DTO):
    payment_id: str = field(default_factory=str)
    partnerId: str = field(default_factory=str)
    state: str = field(default_factory=str)
    enable_at: str = field(default_factory=str)
    money: Money = field(default_factory=Money)
    payment_Method: PaymentMethod = field(default_factory=PaymentMethod)
    taxes: list[Tax] = field(default_factory=list)
