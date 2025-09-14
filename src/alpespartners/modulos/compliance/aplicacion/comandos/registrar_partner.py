

from dataclasses import dataclass

from alpespartners.modulos.compliance.aplicacion.mapeadores import MapeadorPayment
from alpespartners.modulos.compliance.dominio.repositorios import RepositorioCompliance
from .base import ComandoBaseHandler
from alpespartners.seedwork.aplicacion.comandos import Comando
from alpespartners.seedwork.aplicacion.comandos import ejecutar_commando as comando
from alpespartners.modulos.compliance.dominio.entidades import Payment

@dataclass
class RegistrarPartner(Comando):
    partner_id: str

class RegistrarPartnerHandler(ComandoBaseHandler):

    def handle(self, comando: RegistrarPartner):
        payment_DTO = payment_DTO(
            partnerId=comando.partner_id
        )

        payment: Payment = self._fabrica_compliance.crear_objeto(
            payment_DTO, MapeadorPayment()
        )

        repositorio = self._fabrica_repositorio.crear_objeto(RepositorioCompliance)
        repositorio.agregar(payment)
        payment.registrar_partner(payment)
    
@comando.register(RegistrarPartner)
def ejecutar_comando_registrar_partner(
    comando: RegistrarPartner,
) -> None:
    handler = RegistrarPartnerHandler()
    return handler.handle(comando)