from dataclasses import dataclass, field
from datetime import datetime
from alpespartners.modulos.programas.dominio.eventos import ProgramaCreado
from alpespartners.seedwork.dominio.entidades import AgregacionRaiz, Entidad
import alpespartners.modulos.programas.dominio.objetos_valor as ov


@dataclass
class Afiliacion(Entidad):
    afiliado_id: str = field(default="")
    estado: ov.AfiliacionEstado = field(default=ov.AfiliacionEstado.PENDIENTE)
    fecha_alta: datetime = field(default_factory=datetime.now)
    fecha_baja: datetime = field(default_factory=datetime.now)


@dataclass
class Programa(AgregacionRaiz):
    estado: ov.ProgramaEstado = field(default=ov.ProgramaEstado.BORRADOR)
    tipo: ov.ProgramaTipo = field(default=ov.ProgramaTipo.AFILIADOS)
    brand_id: str = field(default="")
    vigencia: ov.Vigencia = field(default=None)
    terminos: ov.Terminos = field(default=None)
    afiliaciones: list[Afiliacion] = field(default_factory=list)

    def crear_programa(self, programa):
        self.estado = programa.estado
        self.tipo = programa.tipo
        self.brand_id = programa.brand_id
        self.vigencia = programa.vigencia
        self.terminos = programa.terminos

        self.agregar_evento(ProgramaCreado(id=self.id, estado=self.estado))
