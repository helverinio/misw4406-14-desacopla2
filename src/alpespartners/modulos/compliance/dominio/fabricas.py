from dataclasses import dataclass

from alpespartners.modulos.compliance.infraestructura.dto import Payment
from alpespartners.seedwork.dominio.fabricas import Fabrica
from alpespartners.seedwork.dominio.repositorio import Mapeador
from alpespartners.seedwork.dominio.entidades import Entidad

import logging

logging = logging.getLogger(__name__)

@dataclass
class FabricaCompliance(Fabrica):
    def crear_objeto(self, obj: any, mapeador: Mapeador) -> any:
        #print instance of obj
        logging.info(f"Tipo de obj: {type(obj)}")
        if isinstance(obj, Entidad):
            logging.info(f"Convirtiendo entidad a DTO: {obj}")
            return mapeador.entidad_a_dto(obj)
        else:
            logging.info(f"Convirtiendo DTO a entidad: {obj}")
            payment: Payment = mapeador.dto_a_entidad(obj)

            # TODO VALIDAR REGLAS DE NEGOCIO

            return payment