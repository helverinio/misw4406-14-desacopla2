import logging
import traceback
from alpespartners.modulos.compliance.infraestructura.schema.v1.eventos import EventoContratoCreado
import pulsar, _pulsar
from pulsar.schema import *
from alpespartners.seedwork.infrastructura.utils import broker_url

logging = logging.getLogger(__name__)


def suscribirse_a_eventos():
    cliente = None
    try:
        cliente = pulsar.Client(broker_url())
        consumidor = cliente.subscribe(
            "comandos-compliance",
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name="administracion-financiera-compliance",
            schema=AvroSchema(EventoContratoCreado),
        )

        while True:
            mensaje = consumidor.receive()
            datos = mensaje.value().data
            logging.info(f"Comando recibido: {datos}")
            consumidor.acknowledge(mensaje)
    
    except:
        logging.error("Error al conectar con el broker de mensajes para comandos.")
        traceback.print_exc()
        if cliente:
            cliente.close()