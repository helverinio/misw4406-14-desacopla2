import pulsar
from pulsar.schema import AvroSchema

from alpespartners.seedwork.infrastructura.utils import broker_url
from alpespartners.modulos.programas.infraestructura.mapeadores import MapeadorEventoDominioPrograma

class Despachador:
    def __init__(self):
        self.mapper = MapeadorEventoDominioPrograma()

    def _publicar_mensaje(self, mensaje, topico, schema):
        cliente = pulsar.Client(broker_url())
        publicador = cliente.create_producer(topic=topico, schema=schema)
        publicador.send(mensaje)
        cliente.close()

    def publicar_evento(self, evento, topico='eventos-programas'):
        evento = self.mapper.entidad_a_dto(evento)
        self._publicar_mensaje(evento, topico, AvroSchema(evento.__class__))