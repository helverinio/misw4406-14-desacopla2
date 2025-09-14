from alpespartners.seedwork.dominio.repositorio import Mapeador
from alpespartners.modulos.compliance.dominio.entidades import Payment

class MapeadorCompliance(Mapeador):
    _FORMATO_FECHA = "%Y-%m-%dT%H:%M:%SZ"

    def entidad_a_dto(self, entidad: Payment) -> PaymentDTO:
        #TODO
        ...