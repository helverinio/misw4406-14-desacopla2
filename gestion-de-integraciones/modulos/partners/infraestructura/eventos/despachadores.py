import pulsar
from pulsar.schema import AvroSchema
import os
from .mapeadores import MapeadorEventoDominioPartner

def broker_url():
    """Get broker URL from environment variable"""
    return os.getenv('BROKER_URL', 'pulsar://broker:6650')

def is_pulsar_available():
    """Check if Pulsar broker is available"""
    try:
        import socket
        import urllib.parse
        
        broker = broker_url()
        parsed = urllib.parse.urlparse(broker)
        host = parsed.hostname or 'localhost'
        port = parsed.port or 6650
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # 2 second timeout
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

class DespachadorEventosPartner:
    """Despachador de eventos para Partners usando Pulsar"""
    
    def __init__(self):
        self.mapper = MapeadorEventoDominioPartner()

    def _publicar_mensaje(self, mensaje, topico, schema):
        """Publica un mensaje en Pulsar"""
        cliente = pulsar.Client(broker_url())
        try:
            publicador = cliente.create_producer(topic=topico, schema=schema)
            publicador.send(mensaje)
            print(f"✅ Evento publicado en tópico '{topico}': {mensaje.type}")
        except Exception as e:
            print(f"❌ Error publicando evento: {e}")
            raise
        finally:
            cliente.close()

    def publicar_evento(self, evento, topico=None):
        """Publica un evento de dominio como evento de integración"""
        if not is_pulsar_available():
            print(f"⚠️  Pulsar no disponible. Evento {evento.__class__.__name__} no se publicó.")
            print("💡 Para habilitar eventos, inicia Pulsar con: docker-compose -f ../docker-compose.pulsar.yml up -d")
            return False  # Return False to indicate event wasn't published
            
        # Determinar el tópico basado en el tipo de evento si no se especifica
        if topico is None:
            topico_map = {
                'PartnerCreado': 'gestion-de-integraciones',
                'PartnerActualizado': 'eventos-partners-actualizado',
                'PartnerEliminado': 'eventos-partners-eliminado',
                'KYCVerificado': 'eventos-kyc-verificado',
                'IntegracionCreada': 'eventos-integraciones-creada',
                'IntegracionRevocada': 'eventos-integraciones-revocada'
            }
            topico = topico_map.get(evento.__class__.__name__, 'eventos-partners-general')
            
        try:
            print(f"🌐 Publicando evento '{evento.__class__.__name__}' en tópico '{topico}'")
            evento_integracion = self.mapper.entidad_a_dto(evento)
            self._publicar_mensaje(evento_integracion, topico, AvroSchema(evento_integracion.__class__))
            return True  # Return True to indicate successful publication
        except Exception as e:
            print(f"❌ Error mapeando y publicando evento: {e}")
            raise
