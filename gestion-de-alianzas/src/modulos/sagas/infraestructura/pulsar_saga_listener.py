"""
Listener para eventos de Pulsar relacionados con la saga coreográfica de partners
"""
import pulsar
import json
import logging
import uuid
from datetime import datetime
import asyncio
import os
import sys
import threading

# Agregar paths para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from src.modulos.sagas.dominio.eventos import (
    CreatePartner, PartnerCreated, PartnerCreationFailed,
    ContratoCreado, ContratoCreadoFailed,
    ContratoAprobado, ContratoRechazado, RevisionContrato
)
from modulos.sagas.aplicacion.coordinadores.saga_partners import CoordinadorPartnersCoreografico

# Configurar logging
logger = logging.getLogger(__name__)

class PulsarSagaChoreographyListener:
    
    def __init__(self, pulsar_url: str = None):
        self.pulsar_url = pulsar_url or os.getenv('BROKER_URL', 'pulsar://localhost:6650')
        
        # Mapeo de tópicos a tipos de eventos
        self.topics = {
            'comando-crear-partner': CreatePartner,  # Topic que inicia la saga
            'PartnerCreado': PartnerCreated, 
            'ContratoCreado': ContratoCreado,
            'contrato-aprobado': ContratoAprobado,   # Nuevo: resultado de compliance
            'contrato-rechazado': ContratoRechazado, # Nuevo: rechazo de compliance
            'revision-contrato': RevisionContrato,   # Nuevo: revisión de contrato
        }
        
        self.subscription_prefix = 'saga-choreography'
        self.client = None
        self.consumers = {}
        self.revision_producer = None  # Productor para eventos de revisión

        self.coordinador = CoordinadorPartnersCoreografico()

    def connect(self):
        """Conecta al broker de Pulsar y crea consumers para todos los tópicos"""
        try:
            logger.info(f"🔌 Connecting to Pulsar at {self.pulsar_url}")
            self.client = pulsar.Client(self.pulsar_url)
            
            for topic, event_type in self.topics.items():
                # Usar BytesSchema para compatibilidad con sistemas existentes
                consumer = self.client.subscribe(
                    topic,
                    subscription_name=f"{self.subscription_prefix}-{topic}",
                    schema=pulsar.schema.BytesSchema()  # Bytes schema para compatibilidad
                )
                self.consumers[topic] = consumer
                logger.info(f"✅ Subscribed to topic: {topic} for event: {event_type.__name__}")
            
            # Crear productor para eventos de revisión
            self.revision_producer = self.client.create_producer(
                'revision-contrato',
                schema=pulsar.schema.BytesSchema()
            )
            logger.info("✅ Created producer for revision-contrato topic")
                
            logger.info(f"✅ Pulsar choreography listener connected successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Pulsar: {e}")
            raise
    
    def process_message(self, topic: str, msg_data: bytes):
        """
        Procesa el mensaje recibido de Pulsar y lo convierte en evento de dominio
        """
        try:
            # Intentar decodificar como UTF-8 (para JSON del compliance)
            try:
                content = msg_data.decode('utf-8')
                # Verificar si es JSON válido
                if content.strip().startswith('{') and content.strip().endswith('}'):
                    logger.info(f"📨 Received JSON message from topic {topic}: {content}")
                else:
                    logger.info(f"📨 Received TEXT message from topic {topic}: {content}")
            except UnicodeDecodeError:
                logger.error(f"❌ Failed to decode message as UTF-8 from topic {topic}")
                raise
            
            if not content:
                raise ValueError(f"No se pudo decodificar mensaje del topic {topic}")
            
            evento = None
            if topic == 'comando-crear-partner':
                evento = self._process_create_partner_message(content)
            elif topic == 'PartnerCreado':
                evento = self._process_partner_created_message(content)
            elif topic == 'ContratoCreado':
                evento = self._process_contrato_creado_message(content)
            elif topic == 'contrato-aprobado':
                evento = self._process_contrato_aprobado_message(content)
            elif topic == 'contrato-rechazado':
                evento = self._process_contrato_rechazado_message(content)
            elif topic == 'revision-contrato':
                evento = self._process_revision_contrato_message(content)
            
            if evento:
                logger.info(f"✨ Created event: {type(evento).__name__} for partner_id: {evento.partner_id}")
                return evento
            else:
                raise ValueError(f"No se pudo crear evento para topic {topic} con contenido: {content}")
                
        except Exception as e:
            logger.error(f"Error processing message from topic {topic}")
            raise


    
    def _extract_partner_id_from_content(self, content: str, content_type: str = "unknown") -> str:
        """
        Extrae partner_id de diferentes tipos de contenido, manejando casos especiales
        """
        try:
            # Intentar parsear como JSON primero
            try:
                data = json.loads(content)
                partner_id = data.get("partner_id")
                if partner_id and isinstance(partner_id, str):
                    # Validar que no sea un formulario completo
                    if self._is_valid_partner_id(partner_id):
                        return partner_id
                    else:
                        # Intentar extraer UUID del contenido malformado
                        extracted_id = self._extract_uuid_from_malformed_content(partner_id)
                        if extracted_id:
                            logger.warning(f"⚠️ Extracted UUID from malformed partner_id: {extracted_id}")
                            return extracted_id
                
                # Si no hay partner_id válido, usar el string completo
                partner_id = str(data)
                
            except json.JSONDecodeError:
                # Si no es JSON válido, limpiar el contenido
                clean_content = ''.join(char for char in content if char.isprintable())
                logger.info(f'📥 Cleaned {content_type} content: {clean_content[:100]}...')
                
                # Manejar el prefijo 'H' como en el consumer existente
                if clean_content and clean_content[0] == 'H':
                    partner_id = clean_content[1:]  # Remover el prefijo 'H'
                    logger.info(f'📥 Extracted partner_id from prefixed message: {partner_id[:50]}...')
                else:
                    partner_id = clean_content
                    logger.info(f'📥 Using content as partner_id: {partner_id[:50]}...')
            
            # Validar que el partner_id extraído sea válido
            if not partner_id:
                raise ValueError(f"No se pudo extraer partner_id del mensaje: {content[:100]}...")
            
            if len(partner_id) > 200:
                logger.warning(f"⚠️ Partner ID muy largo ({len(partner_id)} chars), posiblemente malformado")
                # Intentar extraer UUID
                extracted_id = self._extract_uuid_from_malformed_content(partner_id)
                if extracted_id:
                    logger.info(f"✅ Extracted UUID from long content: {extracted_id}")
                    return extracted_id
                else:
                    partner_id = partner_id[:50]
                    logger.warning(f"⚠️ Using truncated partner_id: {partner_id}")
            
            return partner_id
            
        except Exception as e:
            logger.error(f"❌ Error extracting partner_id from {content_type}: {e}")
            raise
    
    def _is_valid_partner_id(self, partner_id: str) -> bool:
        """
        Valida si un partner_id tiene formato válido (UUID o ID corto)
        """
        import re
        
        # Verificar si es UUID
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if re.match(uuid_pattern, partner_id, re.IGNORECASE):
            return True
        
        if len(partner_id) < 50 and partner_id.replace('-', '').replace('_', '').isalnum():
            return True

        if any(char in partner_id for char in ['@', '+', ',', ' ']):
            return False
        
        return True
    
    def _extract_uuid_from_malformed_content(self, content: str) -> str:
        """
        Intenta extraer un UUID de contenido malformado
        """
        import re
        
        # Buscar patrón UUID en el contenido
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        match = re.search(uuid_pattern, content, re.IGNORECASE)
        
        if match:
            return match.group(0)
        
        return None
    
    def _process_create_partner_message(self, content: str) -> CreatePartner:
        """Procesa mensajes del topic comando-crear-partner y crea eventos CreatePartner"""
        try:
            temp_partner_id = f"temp-{str(uuid.uuid4())[:8]}"
            
            logger.info(f"📝 CreatePartner received with form data: {content[:100]}...")
            logger.info(f"🆔 Generated temporary partner_id: {temp_partner_id}")
            logger.info(f"⏭️ Real partner_id will come from PartnerCreated event")
            
            return CreatePartner(partner_id=temp_partner_id)
            
        except Exception as e:
            logger.error(f"❌ Error processing CreatePartner message: {e}")
            raise

    def _process_partner_created_message(self, content: str) -> PartnerCreated:
        """Procesa mensajes del topic PartnerCreado y crea eventos PartnerCreated"""
        try:
            partner_id = self._extract_partner_id_from_content(content, "PartnerCreated")
            
            logger.info(f"✅ Created PartnerCreated event for partner_id: {partner_id}")
            return PartnerCreated(partner_id=partner_id)
            
        except Exception as e:
            logger.error(f"❌ Error processing PartnerCreado message: {e}")
            raise
    
    def _process_contrato_creado_message(self, content: str) -> ContratoCreado:
        """Procesa mensajes del topic ContratoCreado"""
        try:
            # Parsear JSON del contrato
            contrato_data = json.loads(content)
            logger.info(f"📋 Contrato data parsed: {contrato_data}")
            
            return ContratoCreado(
                partner_id=contrato_data.get('partner_id', ''),
                contrato_id=contrato_data.get('id', 'unknown'),
                monto=contrato_data.get('monto', 0.0),
                moneda=contrato_data.get('moneda', 'USD'),
                estado=contrato_data.get('estado', 'ACTIVO')
            )
            
        except Exception as e:
            logger.error(f"❌ Error processing ContratoCreado message: {e}")
            raise
    
    def _process_contrato_aprobado_message(self, content: str) -> ContratoAprobado:
        """Procesa mensajes del topic contrato-aprobado"""
        try:
            # Parsear JSON del contrato aprobado
            data = json.loads(content)
            logger.info(f"✅ Contrato aprobado data parsed: {data}")
            
            return ContratoAprobado(
                partner_id=data.get('partner_id', ''),
                contrato_id=data.get('contrato_id', 'unknown'),
                monto=data.get('monto', 0.0),
                moneda=data.get('moneda', 'USD'),
                estado=data.get('estado', 'APROBADO'),
                tipo=data.get('tipo', 'STANDARD'),
                fecha_aprobacion=data.get('fecha_aprobacion', ''),
                validaciones_pasadas=data.get('validaciones_pasadas', [])
            )
            
        except Exception as e:
            logger.error(f"❌ Error processing ContratoAprobado message: {e}")
            raise
    
    def _process_contrato_rechazado_message(self, content: str) -> ContratoRechazado:
        """Procesa mensajes del topic contrato-rechazado"""
        try:
            # Parsear JSON del contrato rechazado
            data = json.loads(content)
            logger.info(f"❌ Contrato rechazado data parsed: {data}")
            
            return ContratoRechazado(
                partner_id=data.get('partner_id', ''),
                contrato_id=data.get('contrato_id', 'unknown'),
                monto=data.get('monto', 0.0),
                moneda=data.get('moneda', 'USD'),
                estado=data.get('estado', 'RECHAZADO'),
                tipo=data.get('tipo', 'STANDARD'),
                fecha_rechazo=data.get('fecha_rechazo', ''),
                causa_rechazo=data.get('causa_rechazo', ''),
                validacion_fallida=data.get('validacion_fallida', '')
            )
            
        except Exception as e:
            logger.error(f"❌ Error processing ContratoRechazado message: {e}")
            raise
    
    def _process_revision_contrato_message(self, content: str) -> RevisionContrato:
        """Procesa mensajes del topic revision-contrato"""
        try:
            # Parsear JSON del evento de revisión
            data = json.loads(content)
            logger.info(f"🔄 Revision contrato data parsed: {data}")
            
            return RevisionContrato(
                partner_id=data.get('partner_id', ''),
                contrato_id=data.get('contrato_id', 'unknown'),
                monto=data.get('monto', 0.0),
                moneda=data.get('moneda', 'USD'),
                estado=data.get('estado', 'REQUIERE_REVISION'),
                tipo=data.get('tipo', 'STANDARD'),
                fecha_revision=data.get('fecha_revision', ''),
                causa_rechazo_original=data.get('causa_rechazo_original', ''),
                validacion_fallida=data.get('validacion_fallida', ''),
                requiere_revision_manual=data.get('requiere_revision_manual', True),
                comentarios_revision=data.get('causa_rechazo_original', '')  # Usar causa como comentario
            )
            
        except Exception as e:
            #logger.error(f"❌ Error processing RevisionContrato message: {e}")
            raise
    
    def listen_topic(self, topic: str):
        """
        Escucha continuamente un tópico específico
        """
        consumer = self.consumers[topic]
        logger.info(f"📡 Starting to listen for events on topic: {topic}")
        
        try:
            while True:
                logger.info(f"⏳ Waiting for messages on topic {topic}...")
                msg = consumer.receive()
                
                try:
                    # Procesar el mensaje y crear evento de dominio
                    evento = self.process_message(topic, msg.data())
                    
                    # Manejar eventos de compliance con lógica específica
                    if isinstance(evento, ContratoAprobado):
                        self._handle_contrato_aprobado(evento)
                    elif isinstance(evento, ContratoRechazado):
                        self._handle_contrato_rechazado(evento)
                    elif isinstance(evento, RevisionContrato):
                        self._handle_revision_contrato(evento)
                    else:
                        # Procesar el evento en la saga coreográfica normal
                        self.coordinador.procesar_evento(evento)
                    
                    # Confirmar el mensaje
                    consumer.acknowledge(msg)
                    logger.info(f"✅ Successfully processed event from topic {topic}")
                    
                except Exception as e:
                    logger.error(f'Error processing message from topic {topic}')
                    consumer.negative_acknowledge(msg)
                    
        except Exception as e:
            logger.error(f'Fatal error in listener for topic {topic}')
            raise
    
    def _handle_contrato_aprobado(self, evento: ContratoAprobado):
        """Maneja eventos de contrato aprobado - finaliza la saga exitosamente"""
        try:
            logger.info(f"🎉 Contrato APROBADO para partner {evento.partner_id}")
            logger.info(f"📋 Detalles: Contrato {evento.contrato_id}, Monto: {evento.monto} {evento.moneda}")
            logger.info(f"✅ Validaciones pasadas: {', '.join(evento.validaciones_pasadas)}")
            
            # Procesar en la saga - el coordinador ya maneja la finalización
            self.coordinador.procesar_evento(evento)
            
            logger.info(f"🏁 Saga completada exitosamente para partner {evento.partner_id}")
            
        except Exception as e:
            logger.error(f"❌ Error manejando contrato aprobado: {e}")
            raise
    
    def _handle_contrato_rechazado(self, evento: ContratoRechazado):
        """Maneja eventos de contrato rechazado - crea evento de revisión"""
        try:
            logger.warning(f"❌ Contrato RECHAZADO para partner {evento.partner_id}")
            logger.warning(f"📋 Detalles: Contrato {evento.contrato_id}, Causa: {evento.causa_rechazo}")
            logger.warning(f"⚠️ Validación fallida: {evento.validacion_fallida}")
            
            # Procesar en la saga para registrar el rechazo
            self.coordinador.procesar_evento(evento)
            
            # Crear evento de revisión
            evento_revision = RevisionContrato(
                partner_id=evento.partner_id,
                contrato_id=evento.contrato_id,
                monto=evento.monto,
                moneda=evento.moneda,
                estado="REQUIERE_REVISION",
                tipo=evento.tipo,
                fecha_revision=datetime.now().isoformat(),
                causa_rechazo_original=evento.causa_rechazo,
                validacion_fallida=evento.validacion_fallida,
                requiere_revision_manual=True
            )
            
            # Publicar evento de revisión
            if self.revision_producer:
                # Serializar el evento a JSON
                evento_json = json.dumps({
                    'partner_id': evento_revision.partner_id,
                    'contrato_id': evento_revision.contrato_id,
                    'monto': evento_revision.monto,
                    'moneda': evento_revision.moneda,
                    'estado': evento_revision.estado,
                    'tipo': evento_revision.tipo,
                    'fecha_revision': evento_revision.fecha_revision,
                    'causa_rechazo_original': evento_revision.causa_rechazo_original,
                    'validacion_fallida': evento_revision.validacion_fallida,
                    'requiere_revision_manual': evento_revision.requiere_revision_manual
                })
                
                self.revision_producer.send(evento_json.encode('utf-8'))
                logger.info(f"📢 Evento RevisionContrato publicado para contrato {evento.contrato_id}")
            else:
                logger.warning("⚠️ Producer de revisión no disponible")
            
            # Finalizar la saga con fallo solo si no requiere revisión manual
            logger.info(f"🔄 Saga en estado de revisión pendiente para partner {evento.partner_id}")
            logger.info(f"📝 Se publicará evento RevisionContrato para revisión manual")
            
        except Exception as e:
            logger.error(f"❌ Error manejando contrato rechazado: {e}")
            raise
    
    def _handle_revision_contrato(self, evento: RevisionContrato):
        """Maneja eventos de revisión de contrato - registra la revisión pendiente"""
        try:
            logger.info(f"🔄 Contrato en REVISIÓN para partner {evento.partner_id}")
            logger.info(f"📋 Detalles: Contrato {evento.contrato_id}, Monto: {evento.monto} {evento.moneda}")
            logger.info(f"⚠️ Causa revisión: {evento.causa_rechazo_original}")
            logger.info(f"🔍 Validación que falló: {evento.validacion_fallida}")
            
            # Procesar en la saga para registrar la revisión
            self.coordinador.procesar_evento(evento)
            logger.info(f"⏳ Saga mantiene estado de revisión pendiente para partner {evento.partner_id}")
            logger.info(f"📝 Esperando resolución de revisión manual...")
            
        except Exception as e:
            logger.error(f"❌ Error manejando revisión de contrato: {e}")
            raise
    
    def listen(self):
        """
        Escucha todos los tópicos en threads separados
        """
        if not self.consumers:
            self.connect()
        
        logger.info(f"🎭 Starting choreography listener for topics: {list(self.topics.keys())}")
        
        # Crear un thread para cada tópico
        threads = []
        for topic in self.topics.keys():
            thread = threading.Thread(target=self.listen_topic, args=(topic,), daemon=True)
            thread.start()
            threads.append(thread)
            logger.info(f"🧵 Started thread for topic: {topic}")
        
        # Mantener el proceso principal vivo
        try:
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            logger.info("🛑 Choreography listener stopped by user")
    
    def close(self):
        """Cierra las conexiones de Pulsar"""
        try:
            if self.revision_producer:
                self.revision_producer.close()
            if self.client:
                self.client.close()
            logger.info("📡 Pulsar choreography listener closed")
        except Exception as e:
            logger.warning(f"⚠️ Error closing Pulsar connections: {e}")


def iniciar_listener():
    """Función helper para iniciar el listener coreográfico"""
    listener = PulsarSagaChoreographyListener()
    try:
        listener.listen()
    except KeyboardInterrupt:
        logger.info("🛑 Choreography saga listener stopped by user")
    finally:
        listener.close()


if __name__ == "__main__":
    iniciar_listener()