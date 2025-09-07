import pulsar,_pulsar  
from pulsar.schema import *
import uuid
import time
import logging
import traceback
import datetime

from alpespartners.modulos.programas.infraestructura.schema.v1.eventos import EventoProgramaCreado
from alpespartners.seedwork.infrastructura.utils import broket_url

def suscribirse_a_eventos(app=None):
    cliente = None
    try:
        cliente = pulsar.Client(broket_url())
        consumidor = cliente.subscribe('eventos-programa', consumer_type=_pulsar.ConsumerType.Shared,subscription_name='aeroalpes-sub-eventos', schema=AvroSchema(EventoProgramaCreado))

        while True:
            mensaje = consumidor.receive()
            datos = mensaje.value().data
            print(f'Evento recibido: {datos}')
            
            consumidor.acknowledge(mensaje)     

        cliente.close()
    except:
        logging.error('ERROR: Suscribiendose al tópico de eventos!')
        traceback.print_exc()
        if cliente:
            cliente.close()
