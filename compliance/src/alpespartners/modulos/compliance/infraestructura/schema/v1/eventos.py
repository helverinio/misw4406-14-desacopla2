from alpespartners.seedwork.infrastructura.schema.v1.eventos import EventoIntegracion
from alpespartners.seedwork.infrastructura.utils import time_millis
import uuid
from pulsar.schema import Record, String, Long

class ContratoCreadoPayload(Record):
    contrato_id = String()
    partner_id = String()
    estado = String() 

class EventoContratoCreado(EventoIntegracion):
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String()
    type = String()
    datacontenttype = String()
    service_name = String()
    data = ContratoCreadoPayload()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)