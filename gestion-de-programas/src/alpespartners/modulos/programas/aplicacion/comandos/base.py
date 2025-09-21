from alpespartners.modulos.programas.infraestructura.despachadores import Despachador
from alpespartners.seedwork.aplicacion.comandos import ComandoHandler
from alpespartners.modulos.programas.infraestructura.fabricas import FabricaRepositorio
from alpespartners.modulos.programas.dominio.fabricas import FabricaProgramas

class ComandoBaseHandler(ComandoHandler):
    def __init__(self):
        self._fabrica_repositorio: FabricaRepositorio = FabricaRepositorio()
        self._fabrica_programas: FabricaProgramas = FabricaProgramas()
        self._despachador: Despachador = Despachador()
        
    @property
    def fabrica_repositorio(self):
        return self._fabrica_repositorio
    
    @property
    def fabrica_vuelos(self):
        return self._fabrica_programas    
    
    @property
    def despachador(self):
        return self._despachador