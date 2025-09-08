from pulsar.schema import *
from alpespartners.seedwork.infrastructura.schema.v1.eventos import EventoIntegracion
from alpespartners.seedwork.infrastructura.utils import time_millis
import uuid

class AfiliacionPayload(Record):
    afiliado_id = String()
    
class ProgramaCreadoPayload(Record):
    programa_id = String()
    estado = String()
    afiliaciones = Array(AfiliacionPayload())


class EventoProgramaCreado(EventoIntegracion):
    # NOTE La librería Record de Pulsar no es capaz de reconocer campos heredados,
    # por lo que los mensajes al ser codificados pierden sus valores
    # Dupliqué el los cambios que ya se encuentran en la clase Mensaje
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String()
    type = String()
    datacontenttype = String()
    service_name = String()
    data = ProgramaCreadoPayload()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
