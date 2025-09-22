from pulsar.schema import *

def time_millis():
    """Utility function to get current time in milliseconds"""
    import time
    return int(time.time() * 1000)

class EventoIntegracion(Record):
    """Clase base para eventos de integración siguiendo CloudEvents spec"""
    id = String()
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String()
    type = String()
    datacontenttype = String()
    service_name = String()

class CrearPartnerPayload(Record):
    """Payload para eventos de creación de partner"""	
    nombre = String()
    email = String()
    telefono = String(required=False)
    direccion = String(required=False)

# Eventos de integración específicos
class ComandoCrearPartner(EventoIntegracion):
    data = CrearPartnerPayload()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

