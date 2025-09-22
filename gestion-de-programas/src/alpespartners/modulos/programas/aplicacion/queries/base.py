from alpespartners.seedwork.aplicacion.queries import QueryHandler
from alpespartners.modulos.programas.infraestructura.fabricas import FabricaRepositorio
from alpespartners.modulos.programas.dominio.fabricas import FabricaProgramas

class ProgramaQueryBaseHandler(QueryHandler):
    def __init__(self):
        self._fabrica_repositorio: FabricaRepositorio = FabricaRepositorio()
        self._fabrica_programas: FabricaProgramas = FabricaProgramas()

    @property
    def fabrica_repositorio(self):
        return self._fabrica_repositorio
    
    @property
    def fabrica_programas(self):
        return self._fabrica_programas    