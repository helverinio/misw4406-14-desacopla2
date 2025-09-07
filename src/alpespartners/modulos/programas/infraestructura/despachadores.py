import pulsar
from pulsar.schema import AvroSchema

from alpespartners.seedwork.infrastructura.utils import broker_host
from alpespartners.modulos.programas.infraestructura.mapeadores import MapeadorEventoDominioPrograma

class Despachador:
    def __init__(self):
        self.mapper = MapeadorEventoDominioPrograma()

    def _publicar_mensaje(self, mensaje, topico, schema):
        cliente = pulsar.Client(f'pulsar://{broker_host()}:6650')
        publicador = cliente.create_producer(topico, schema)
        publicador.send(mensaje)
        cliente.close()

    def publicar_evento(self, evento, topico='eventos-programas'):
        evento = self.mapper.entidad_a_dto(evento)
        self._publicar_mensaje(evento, topico, AvroSchema(evento.__class__))