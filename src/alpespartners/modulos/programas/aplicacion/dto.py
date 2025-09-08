from dataclasses import dataclass, field
from alpespartners.seedwork.aplicacion.dto import DTO

@dataclass(frozen=True)
class AfiliacionDTO(DTO):
    afiliacion_id: str = field(default_factory=str)
    programa_id: str = field(default_factory=str)
    afiliado_id: str = field(default_factory=str)
    estado: str = field(default_factory=str)
    fecha_alta: str = field(default_factory=str)
    fecha_baja: str = field(default_factory=str)
    creado_en: str = field(default_factory=str)
    actualizado_en: str = field(default_factory=str)

@dataclass(frozen=True)
class VigenciaDTO(DTO):
    inicio: str = field(default_factory=str)
    fin: str = field(default_factory=str)

@dataclass(frozen=True)
class TerminosDTO(DTO):
    modelo: str = field(default_factory=str)
    moneda: str = field(default_factory=str)
    tarifa_base: float = field(default_factory=float)
    tope: float = field(default_factory=float)

@dataclass(frozen=True)
class ProgramaDTO(DTO):
    programa_id: str = field(default_factory=str)
    estado: str = field(default_factory=str)
    tipo: str = field(default_factory=str)
    brand_id: str = field(default_factory=str)
    vigencia: VigenciaDTO = field(default_factory=VigenciaDTO)
    terminos: TerminosDTO = field(default_factory=TerminosDTO)
    creado_en: str = field(default_factory=str)
    modificado_en: str = field(default_factory=str)
    afiliaciones: list[AfiliacionDTO] = field(default_factory=list)



