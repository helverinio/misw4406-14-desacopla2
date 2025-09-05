

from dataclasses import dataclass


@dataclass
class FabricaRepositorio(Fabrica):
    def crear_objeto(self, obj:type, mapeador: any = None) -> Repositorio:
