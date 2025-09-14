
from dataclasses import dataclass

from alpespartners.seedwork.dominio.repositorio import Repositorio
from alpespartners.seedwork.dominio.fabricas import Fabrica
from alpespartners.modulos.compliance.dominio.repositorios import RepositorioCompliance

from .excepciones import ExcepcionFabrica
from .repositorios import RepositorioCompliancePostgress

@dataclass
class FabricaRepositorio(Fabrica):
    def crear_objeto(self, obj:type, mapeador: any = None) -> Repositorio:
        if obj == RepositorioCompliance:
            return RepositorioCompliancePostgress()
        else:
            raise ExcepcionFabrica()