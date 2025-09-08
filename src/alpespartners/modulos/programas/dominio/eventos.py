from __future__ import annotations
from dataclasses import dataclass
import uuid
from alpespartners.seedwork.dominio.eventos import (EventoDominio)

class EventoPrograma(EventoDominio):
    ...

@dataclass
class ProgramaCreado(EventoPrograma):
    programa_id: uuid.UUID = None
    estado: str = None
    afiliaciones: list[dict] = None
