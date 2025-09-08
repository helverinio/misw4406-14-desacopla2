
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

from alpespartners.seedwork.dominio.objetos_valor import ObjetoValor

class ModeloComision(Enum):
    CPA = "CPA"
    CPL = "CPL"
    CPC = "CPC"


class ProgramaEstado(Enum):
    BORRADOR = "BORRADOR"
    ACTIVO = "ACTIVO"
    SUSPENDIDO = "SUSPENDIDO"
    CERRADO = "CERRADO"

class ProgramaTipo(Enum):
    AFILIADOS = "AFILIADOS"
    INFLUENCERS = "INFLUENCERS"
    ADVOCACY = "ADVOCACY"
    SAAS = "SAAS"

class AfiliacionEstado(Enum):
    PENDIENTE = "PENDIENTE"
    ACTIVA = "ACTIVA"
    SUSPENDIDA = "SUSPENDIDA"
    BAJA = "BAJA"


@dataclass(frozen=True)
class Vigencia(ObjetoValor):
    inicio: date
    fin: date

@dataclass(frozen=True)
class Terminos(ObjetoValor):
    modelo : ModeloComision
    moneda : str
    tarifa_base : Decimal
    tope : Decimal