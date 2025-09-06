

from dataclasses import dataclass

from .entidades import Programa

from alpespartners.seedwork.aplicacion.dto import Mapeador
from alpespartners.seedwork.dominio.entidades import Entidad
from alpespartners.seedwork.dominio.fabricas import Fabrica

@dataclass
class FabricaProgramas(Fabrica):
    def crear_objeto(self, obj: any, mapeador: Mapeador) -> any:
        if isinstance(obj, Entidad):
            return mapeador.entidad_a_dto(obj)
        else:
            programa: Programa = mapeador.dto_a_entidad(obj)

            # TODO VALIDAR REGLAS DE NEGOCIO

            return programa
