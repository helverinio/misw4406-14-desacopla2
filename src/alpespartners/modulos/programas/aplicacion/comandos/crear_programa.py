import logging
from alpespartners.seedwork.aplicacion.comandos import Comando, ComandoResultado
from .base import ComandoBaseHandler
from dataclasses import dataclass, field
from alpespartners.seedwork.aplicacion.comandos import ejecutar_commando as comando

from alpespartners.modulos.programas.dominio.entidades import Programa
from alpespartners.modulos.programas.infraestructura.repositorios import (
    RepositorioProgramas,
)
from alpespartners.modulos.programas.aplicacion.dto import (
    AfiliacionDTO,
    ProgramaDTO,
    TerminosDTO,
    VigenciaDTO,
)
from alpespartners.modulos.programas.aplicacion.mapeadores import MapeadorPrograma


@dataclass
class CrearPrograma(Comando):
    estado: str
    tipo: str
    brand_id: str

    vigencia: VigenciaDTO
    terminos: TerminosDTO
    afiliaciones: list[AfiliacionDTO]


class CrearProgramaHandler(ComandoBaseHandler):

    def handle(self, comando: CrearPrograma):
        programa_dto = ProgramaDTO(
            estado=comando.estado,
            tipo=comando.tipo,
            brand_id=comando.brand_id,
            vigencia=comando.vigencia,
            terminos=comando.terminos,
            afiliaciones=comando.afiliaciones,
        )
  
        programa: Programa = self._fabrica_programas.crear_objeto(
            programa_dto, MapeadorPrograma()
        )

        repositorio = self._fabrica_repositorio.crear_objeto(RepositorioProgramas)
        repositorio.agregar(programa)
        programa.crear_programa(programa)

        if len(programa.eventos) > 0:
            for evento in programa.eventos:
                self.despachador.publicar_evento(evento)

        programa_dto = self._fabrica_programas.crear_objeto(
            programa, MapeadorPrograma()
        )

        return ComandoResultado(resultado=programa_dto)


@comando.register(CrearPrograma)
def ejecutar_comando_crear_programa(comando: CrearPrograma):
    handler = CrearProgramaHandler()
    return handler.handle(comando)
