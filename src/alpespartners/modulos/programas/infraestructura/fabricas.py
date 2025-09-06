

from dataclasses import dataclass

from alpespartners.modulos.programas.dominio.repositorios import RepositorioProgramas
from alpespartners.seedwork.dominio.fabricas import Fabrica
from alpespartners.seedwork.dominio.repositorio import Repositorio

from .repositorios import RepositorioProgramasPostgress
from .excepciones import ExcepcionFabrica

@dataclass
class FabricaRepositorio(Fabrica):
    def crear_objeto(self, obj:type, mapeador: any = None) -> Repositorio:
        if obj == RepositorioProgramas:
            return RepositorioProgramasPostgress()
        else:
            raise ExcepcionFabrica()