import pulsar, _pulsar
from pulsar.schema import *
import logging
import traceback


from alpespartners.modulos.programas.infraestructura.schema.v1.eventos import (
    EventoProgramaCreado,
)
from alpespartners.seedwork.infrastructura.utils import broker_url


def suscribirse_a_eventos(app=None):
    cliente = None
    try:
        cliente = pulsar.Client(broker_url())
        consumidor = cliente.subscribe(
            "eventos-programas",
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name="alpespartners-sub-eventos",
            schema=AvroSchema(EventoProgramaCreado),
        )

        while True:
            mensaje = consumidor.receive()
            datos = mensaje.value().data
            logging.info(f"Evento recibido: {datos}")
            consumidor.acknowledge(mensaje)

        cliente.close()
    except:
        logging.error("ERROR: Suscribiendose al tópico de eventos!")
        traceback.print_exc()
        if cliente:
            cliente.close()
