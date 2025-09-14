from dataclasses import dataclass

from alpespartners.seedwork.dominio.fabricas import Fabrica
from alpespartners.seedwork.aplicacion.dto import Mapeador
from alpespartners.seedwork.dominio.entidades import Entidad

@dataclass
class FabricaCompliance(Fabrica):
    def crear_objeto(self, obj: any, mapeador: Mapeador) -> any:
        if isinstance(obj, Entidad):
            return mapeador.entidad_a_dto(obj)
        else:
            compliance: Compliance = mapeador.dto_a_entidad(obj)

            # TODO VALIDAR REGLAS DE NEGOCIO

            return compliance