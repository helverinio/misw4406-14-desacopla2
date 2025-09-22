import pulsar
import _pulsar
from pulsar.schema import AvroSchema
import logging
import traceback
import os
import json
from .schema.v1.eventos import (
    ComandoCrearPartner,
    EventoPartnerCreado,
    EventoPartnerActualizado,
    EventoPartnerEliminado,
    EventoKYCVerificado,
    EventoIntegracionCreada,
    EventoIntegracionRevocada,
)
from uuid import uuid4
from .procesadores import procesar_comando_crear_partner


def broker_url():
    """Get broker URL from environment variable"""
    return os.getenv("BROKER_URL", "pulsar://broker:6650")


def is_pulsar_available():
    """Check if Pulsar broker is available"""
    try:
        import socket
        import urllib.parse

        broker = broker_url()
        parsed = urllib.parse.urlparse(broker)
        host = parsed.hostname or "localhost"
        port = parsed.port or 6650

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # 2 second timeout
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


class FabricaConsumidores:
    """Fabrica de consumidores de eventos"""

    def __init__(self):
        self.consumidores = {}

    def crear_consumidor(self, topico, schema_class, procesador=None):
        """Crea un consumidor para un tópico específico"""
        return ConsumidorEventos(topico, schema_class, procesador)


class ConsumidorEventos:
    """Consumidor de eventos para Partners usando Pulsar"""

    def __init__(self, topico, schema_class, procesador=None):
        self.cliente = None
        self.topico = topico
        self.procesador = procesador
        self.subscription_name = f"gestion-integraciones.{topico}"
        self.schema_class = schema_class

    def _crear_consumidor(self, topico, schema_class, subscription_name):
        """Crea un consumidor para un tópico específico"""
        if not self.cliente:
            self.cliente = pulsar.Client(broker_url())

        consumidor = self.cliente.subscribe(
            topico,
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name=subscription_name,
            schema=AvroSchema(schema_class),
        )
        return consumidor

    def suscribirse(self):
        """Suscribe a eventos que este servicio debe procesar"""
        if not is_pulsar_available():
            print(
                "⚠️  Pulsar no está disponible. Saltando suscripción a eventos externos."
            )
            print(
                "💡 Para habilitar eventos, inicia Pulsar con: docker-compose -f ../docker-compose.pulsar.yml up -d"
            )
            return

        try:
            # Ejemplo: suscribirse a eventos de otros servicios
            consumidor = self._crear_consumidor(
                self.topico,
                self.schema_class,  # Usar como ejemplo, ajustar según necesidad
                self.subscription_name,
            )

            print(f"🎧 Escuchando eventos de {self.topico}...")
            while True:
                mensaje = consumidor.receive()
                try:
                    datos = mensaje.value()
                    logging.info(f"📨 Evento externo recibido: {datos}")

                    # Procesar el evento según el tipo
                    self._procesar_evento_externo(datos)

                    consumidor.acknowledge(mensaje)

                except Exception as e:
                    logging.error(f"❌ Error procesando evento externo: {e}")
                    consumidor.negative_acknowledge(mensaje)

        except Exception as e:
            logging.error("❌ Error suscribiéndose a eventos externos!")
            traceback.print_exc()
            if self.cliente:
                self.cliente.close()

    def _procesar_evento_externo(self, evento):
        """Procesa eventos externos recibidos"""
        # Aquí se puede implementar lógica específica según el tipo de evento
        print(
            f"🔄 Procesando evento: {evento.type if hasattr(evento, 'type') else 'Unknown'}"
        )

        if self.procesador:
            self.procesador(evento)

    def cerrar(self):
        """Cierra las conexiones"""
        if self.cliente:
            self.cliente.close()


def generar_consumidores():
    """Función para iniciar el consumidor de eventos"""
    fabrica_consumidores = FabricaConsumidores()

    consumidores = []

    for topico, schema_class, procesador in [
        ("eventos-partners", EventoPartnerCreado, None),
        (
            "comando-crear-partner",
            ComandoCrearPartner,
            procesar_comando_crear_partner,
        ),
    ]:
        consumidor = fabrica_consumidores.crear_consumidor(
            topico, schema_class, procesador
        )

        consumidores.append(consumidor)

    return consumidores
