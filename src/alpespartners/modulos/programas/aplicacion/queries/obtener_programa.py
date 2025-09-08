from alpespartners.seedwork.aplicacion.queries import Query, QueryResultado
from alpespartners.seedwork.aplicacion.queries import ejecutar_query as query
from alpespartners.modulos.programas.infraestructura.repositorios import (
    RepositorioProgramas,
)
from dataclasses import dataclass
from .base import ProgramaQueryBaseHandler
from alpespartners.modulos.programas.aplicacion.mapeadores import MapeadorPrograma


@dataclass
class ObtenerPrograma(Query):
    id: str


class ObtenerProgramaHandler(ProgramaQueryBaseHandler):

    def handle(self, query: ObtenerPrograma) -> QueryResultado:
        repositorio = self.fabrica_repositorio.crear_objeto(RepositorioProgramas)
        programa = self.fabrica_programas.crear_objeto(
            repositorio.obtener_por_id(query.id), MapeadorPrograma()
        )
        return QueryResultado(resultado=programa)


@query.register(ObtenerPrograma)
def ejecutar_query_obtener_reserva(query: ObtenerPrograma):
    handler = ObtenerProgramaHandler()
    return handler.handle(query)
