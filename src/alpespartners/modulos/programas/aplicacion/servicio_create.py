


from alpespartners.modulos.programas.dominio.entidades import Programa
from alpespartners.modulos.programas.dominio.fabricas import FabricaProgramas
from alpespartners.modulos.programas.infraestructura.fabricas import FabricaRepositorio
from alpespartners.seedwork.aplicacion.servicios import Servicio
from alpespartners.modulos.programas.infraestructura.repositorios import RepositorioProgramas

from .dto import ProgramaDTO
from .mapeadores import MapeadorPrograma

class ServicioProgramaCreate(Servicio):

    def __init__(self):
        self._fabrica_repositorios: FabricaRepositorio = FabricaRepositorio()
        self._fabrica_programas: FabricaProgramas = FabricaProgramas()

    @property 
    def fabrica_repositorio(self):
        return self._fabrica_repositorios
    
    @property
    def fabrica_programas(self):
        return self._fabrica_programas

    def crear_programa(self, programa_dto: ProgramaDTO):
        programa : Programa = self.fabrica_programas.crear_objeto(programa_dto,MapeadorPrograma())
        
        repositorio = self.fabrica_repositorio.crear_objeto(RepositorioProgramas)
        repositorio.agregar(programa)

        return self.fabrica_programas.crear_objeto(programa, MapeadorPrograma())