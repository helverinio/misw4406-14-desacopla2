import pulsar
import _pulsar
from pulsar.schema import AvroSchema
import logging
import traceback
import os
import json
from .schema.v1.eventos import (
    EventoPartnerCreado,
    EventoPartnerActualizado,
    EventoPartnerEliminado,
    EventoKYCVerificado,
    EventoIntegracionCreada,
    EventoIntegracionRevocada
)

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

class ConsumidorEventosPartner:
    """Consumidor de eventos para Partners usando Pulsar"""
    
    def __init__(self):
        self.cliente = None
        self.consumidores = {}
        
    def _crear_consumidor(self, topico, schema_class, subscription_name):
        """Crea un consumidor para un tópico específico"""
        if not self.cliente:
            self.cliente = pulsar.Client(broker_url())
            
        consumidor = self.cliente.subscribe(
            topico,
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name=subscription_name,
            schema=AvroSchema(schema_class)
        )
        return consumidor
    
    def suscribirse_a_eventos_externos(self):
        """Suscribe a eventos externos que este servicio debe procesar"""
        if not is_pulsar_available():
            print("⚠️  Pulsar no está disponible. Saltando suscripción a eventos externos.")
            print("💡 Para habilitar eventos, inicia Pulsar con: docker-compose -f ../docker-compose.pulsar.yml up -d")
            return
            
        try:
            # Ejemplo: suscribirse a eventos de otros servicios
            consumidor_contratos = self._crear_consumidor(
                "gestion-de-alianzas",
                EventoPartnerCreado,  # Usar como ejemplo, ajustar según necesidad
                "integraciones-sub-contratos"
            )
            
            print("🎧 Escuchando eventos externos...")
            while True:
                mensaje = consumidor_contratos.receive()
                try:
                    datos = mensaje.value()
                    logging.info(f"📨 Evento externo recibido: {datos}")
                    
                    # Procesar el evento según el tipo
                    self._procesar_evento_externo(datos)
                    
                    consumidor_contratos.acknowledge(mensaje)
                    
                except Exception as e:
                    logging.error(f"❌ Error procesando evento externo: {e}")
                    consumidor_contratos.negative_acknowledge(mensaje)
                    
        except Exception as e:
            logging.error("❌ Error suscribiéndose a eventos externos!")
            traceback.print_exc()
            if self.cliente:
                self.cliente.close()
    
    def _procesar_evento_externo(self, evento):
        """Procesa eventos externos recibidos"""
        # Aquí se puede implementar lógica específica según el tipo de evento
        print(f"🔄 Procesando evento externo: {evento.type if hasattr(evento, 'type') else 'Unknown'}")
        
        # Ejemplo de procesamiento:
        # - Si es un evento de contrato, crear/actualizar partner relacionado
        # - Si es un evento de compliance, actualizar estado KYC
        # - etc.
    
    def suscribirse_a_eventos_internos(self):
        """Suscribe a eventos internos para auditoría o procesamiento adicional"""
        try:
            consumidor_partners = self._crear_consumidor(
                "eventos-partners",
                EventoPartnerCreado,
                "integraciones-audit-sub"
            )
            
            print("🎧 Escuchando eventos internos para auditoría...")
            while True:
                mensaje = consumidor_partners.receive()
                try:
                    datos = mensaje.value()
                    logging.info(f"📋 Evento interno para auditoría: {datos}")
                    
                    # Procesar para auditoría, logging, métricas, etc.
                    self._procesar_evento_auditoria(datos)
                    
                    consumidor_partners.acknowledge(mensaje)
                    
                except Exception as e:
                    logging.error(f"❌ Error procesando evento para auditoría: {e}")
                    consumidor_partners.negative_acknowledge(mensaje)
                    
        except Exception as e:
            logging.error("❌ Error suscribiéndose a eventos internos!")
            traceback.print_exc()
            if self.cliente:
                self.cliente.close()
    
    def _procesar_evento_auditoria(self, evento):
        """Procesa eventos para auditoría y métricas"""
        print(f"📊 Registrando evento para auditoría: {evento.type if hasattr(evento, 'type') else 'Unknown'}")
        
        # Aquí se puede implementar:
        # - Logging detallado
        # - Métricas de negocio
        # - Notificaciones
        # - Integración con sistemas de monitoreo
    
    def cerrar(self):
        """Cierra las conexiones"""
        if self.cliente:
            self.cliente.close()

def iniciar_consumidor_eventos(modo='externos'):
    """Función para iniciar el consumidor de eventos"""
    consumidor = ConsumidorEventosPartner()
    
    try:
        if modo == 'externos':
            consumidor.suscribirse_a_eventos_externos()
        elif modo == 'internos':
            consumidor.suscribirse_a_eventos_internos()
        else:
            print("❌ Modo no válido. Use 'externos' o 'internos'")
    except KeyboardInterrupt:
        print("🛑 Deteniendo consumidor de eventos...")
    finally:
        consumidor.cerrar()
