

from dataclasses import dataclass

from alpespartners.modulos.compliance.aplicacion.dto import PaymentDTO
from alpespartners.modulos.compliance.aplicacion.mapeadores import MapeadorPayment
from alpespartners.modulos.compliance.infraestructura.repositorios import RepositorioPaymentPostgress
from .base import ComandoBaseHandler
from alpespartners.seedwork.aplicacion.comandos import Comando
from alpespartners.seedwork.aplicacion.comandos import ejecutar_commando as comando
from alpespartners.modulos.compliance.dominio.entidades import Payment

import logging

logging = logging.getLogger(__name__)

@dataclass
class RegistrarPartner(Comando):
    partner_id: str
    state: str
    enable_at: str = None

class RegistrarPartnerHandler(ComandoBaseHandler):

    def handle(self, comando: RegistrarPartner):
        payment_DTO = PaymentDTO(
            partnerId=comando.partner_id,
            state= comando.state,
            enable_at= comando.enable_at
        )

        payment: Payment = self._fabrica_compliance.crear_objeto(
            payment_DTO, MapeadorPayment()
        )

        repositorio = self._fabrica_repositorio.crear_objeto(RepositorioPaymentPostgress.__class__)
        repositorio.agregar(payment)
    
@comando.register(RegistrarPartner)
def ejecutar_comando_registrar_partner(
    comando: RegistrarPartner,
) -> None:
    handler = RegistrarPartnerHandler()
    return handler.handle(comando)