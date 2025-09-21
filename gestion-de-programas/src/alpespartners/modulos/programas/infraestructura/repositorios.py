
from alpespartners.config.db import db
from alpespartners.modulos.programas.dominio.entidades import Programa
from alpespartners.modulos.programas.dominio.fabricas import FabricaProgramas
from alpespartners.modulos.programas.dominio.repositorios import RepositorioProgramas
from .mapeadores import MapeadorPrograma
from .dto import Programa as ProgramaDTO
from uuid import UUID

class RepositorioProgramasPostgress(RepositorioProgramas):

    def __init__(self):
        self._fabrica_programas: FabricaProgramas = FabricaProgramas()
    
    @property
    def fabrica_programas(self):
        return self._fabrica_programas

    def agregar(self, programa: Programa):
        programa_dto = self.fabrica_programas.crear_objeto(programa, MapeadorPrograma())
        db.session.add(programa_dto)
        db.session.commit()
    
    def obtener_por_id(self, id: UUID) -> Programa:
        programa_dto = db.session.query(ProgramaDTO).filter_by(programa_id=str(id)).one()
        return self.fabrica_programas.crear_objeto(programa_dto, MapeadorPrograma())
