from pulsar.schema import *
import uuid
from typing import Optional

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

class PartnerPayload(Record):
    """Payload para eventos de Partner"""
    partner_id = String()
    nombre = String()
    email = String()
    telefono = String(required=False)
    direccion = String(required=False)
    estado = String()
    estado_kyc = String()

class PartnerCreadoPayload(Record):
    """Payload simplificado para eventos de Partner creado"""
    partner_id = String()

class PartnerActualizadoPayload(Record):
    """Payload para eventos de Partner actualizado"""
    partner_id = String()
    nombre = String()
    email = String()
    telefono = String(required=False)
    direccion = String(required=False)
    estado = String()
    estado_anterior = String()

class KYCPayload(Record):
    """Payload para eventos de KYC"""
    partner_id = String()
    estado_kyc_anterior = String()
    estado_kyc_nuevo = String()
    observaciones = String(required=False)

class IntegracionPayload(Record):
    """Payload para eventos de Integración"""
    integracion_id = String()
    partner_id = String()
    tipo = String()
    nombre = String()
    descripcion = String(required=False)

class IntegracionRevocadaPayload(Record):
    """Payload para eventos de Integración revocada"""
    integracion_id = String()
    partner_id = String()
    nombre = String()
    motivo = String(required=False)

# Eventos de integración específicos
class EventoPartnerCreado(EventoIntegracion):
    data = PartnerCreadoPayload()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class EventoPartnerActualizado(EventoIntegracion):
    data = PartnerActualizadoPayload()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class EventoPartnerEliminado(EventoIntegracion):
    data = PartnerPayload()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class EventoKYCVerificado(EventoIntegracion):
    data = KYCPayload()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class EventoIntegracionCreada(EventoIntegracion):
    data = IntegracionPayload()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class EventoIntegracionRevocada(EventoIntegracion):
    data = IntegracionRevocadaPayload()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
