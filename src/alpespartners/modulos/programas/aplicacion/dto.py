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
class ProgramaDTO(DTO):
    programa_id: str = field(default_factory=str)
    estado: str = field(default_factory=str)
    tipo: str = field(default_factory=str)
    brand_id: str = field(default_factory=str)
    vigencia_inicio: str = field(default_factory=str)
    vigencia_fin: str = field(default_factory=str)
    term_modelo: str = field(default_factory=str)
    term_moneda: str = field(default_factory=str)
    term_tarifa_base: float = field(default_factory=float)
    term_tope: float = field(default_factory=float)
    creado_en: str = field(default_factory=str)
    modificado_en: str = field(default_factory=str)
    afiliaciones: list[AfiliacionDTO] = field(default_factory=list)



