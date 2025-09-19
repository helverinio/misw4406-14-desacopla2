import pulsar
import json
import logging
from typing import Dict, Any, Optional, Callable
from pulsar.schema import AvroSchema
import os
from ..domain.events import SagaEvent, SagaEventType


class PulsarClient:
    """Pulsar client for saga orchestrator"""
    
    def __init__(self, service_url: str = None):
        self.service_url = service_url or os.getenv('BROKER_URL', 'pulsar://localhost:6650')
        self.client = None
        self.producers = {}
        self.consumers = {}
        self.logger = logging.getLogger(__name__)
        
    def connect(self):
        """Connect to Pulsar"""
        try:
            self.client = pulsar.Client(self.service_url)
            self.logger.info(f"Connected to Pulsar at {self.service_url}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Pulsar: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from Pulsar"""
        if self.client:
            # Close all producers and consumers
            for producer in self.producers.values():
                producer.close()
            for consumer in self.consumers.values():
                consumer.close()
            
            self.client.close()
            self.logger.info("Disconnected from Pulsar")
    
    def create_producer(self, topic: str) -> pulsar.Producer:
        """Create a producer for a topic"""
        if topic not in self.producers:
            try:
                self.producers[topic] = self.client.create_producer(
                    topic,
                    schema=pulsar.schema.StringSchema()
                )
                self.logger.info(f"Created producer for topic: {topic}")
            except Exception as e:
                self.logger.error(f"Failed to create producer for topic {topic}: {e}")
                raise
        
        return self.producers[topic]
    
    def create_consumer(self, topic: str, subscription_name: str) -> pulsar.Consumer:
        """Create a consumer for a topic"""
        consumer_key = f"{topic}_{subscription_name}"
        if consumer_key not in self.consumers:
            try:
                self.consumers[consumer_key] = self.client.subscribe(
                    topic,
                    subscription_name=subscription_name,
                    schema=pulsar.schema.StringSchema(),
                    consumer_type=pulsar.ConsumerType.Shared
                )
                self.logger.info(f"Created consumer for topic: {topic}, subscription: {subscription_name}")
            except Exception as e:
                self.logger.error(f"Failed to create consumer for topic {topic}: {e}")
                raise
        
        return self.consumers[consumer_key]
    
    def publish_event(self, topic: str, event: SagaEvent) -> bool:
        """Publish a saga event to a topic"""
        try:
            producer = self.create_producer(topic)
            
            # Convert event to JSON
            event_data = {
                "event_id": event.event_id,
                "saga_id": event.saga_id,
                "event_type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "payload": event.payload,
                "correlation_id": event.correlation_id
            }
            
            message = json.dumps(event_data, default=str)
            producer.send(message.encode('utf-8'))
            
            self.logger.info(f"Published event {event.event_type.value} to topic {topic}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to publish event to topic {topic}: {e}")
            return False
    
    def publish_partner_event(self, partner_data: Dict[str, Any]) -> bool:
        """Publish partner creation event to gestion-de-integraciones"""
        try:
            topic = "eventos-partners"
            producer = self.create_producer(topic)
            
            message = json.dumps(partner_data, default=str)
            producer.send(message.encode('utf-8'))
            
            self.logger.info(f"Published partner event to {topic}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to publish partner event: {e}")
            return False
    
    def publish_alliance_event(self, alliance_data: Dict[str, Any]) -> bool:
        """Publish alliance creation event to gestion-de-alianzas"""
        try:
            topic = "gestion-de-integraciones"  # Topic that gestion-de-alianzas listens to
            producer = self.create_producer(topic)
            
            message = json.dumps(alliance_data, default=str)
            producer.send(message.encode('utf-8'))
            
            self.logger.info(f"Published alliance event to {topic}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to publish alliance event: {e}")
            return False
    
    def listen_to_events(self, topic: str, subscription_name: str, message_handler: Callable[[Dict[str, Any]], None]):
        """Listen to events from a topic"""
        try:
            consumer = self.create_consumer(topic, subscription_name)
            
            self.logger.info(f"Starting to listen to topic: {topic}")
            
            while True:
                try:
                    msg = consumer.receive(timeout_millis=5000)
                    
                    # Parse message
                    message_data = json.loads(msg.data().decode('utf-8'))
                    
                    # Handle message
                    message_handler(message_data)
                    
                    # Acknowledge message
                    consumer.acknowledge(msg)
                    
                except pulsar.Timeout:
                    # Timeout is normal, continue listening
                    continue
                except Exception as e:
                    self.logger.error(f"Error processing message from {topic}: {e}")
                    if 'msg' in locals():
                        consumer.negative_acknowledge(msg)
                    
        except Exception as e:
            self.logger.error(f"Failed to listen to topic {topic}: {e}")
            raise


class SagaEventPublisher:
    """Publisher for saga events"""
    
    def __init__(self, pulsar_client: PulsarClient):
        self.pulsar_client = pulsar_client
        self.saga_topic = "saga-events"
        self.logger = logging.getLogger(__name__)
    
    def publish_saga_event(self, event: SagaEvent) -> bool:
        """Publish a saga event"""
        return self.pulsar_client.publish_event(self.saga_topic, event)
    
    def publish_partner_creation_command(self, partner_data: Dict[str, Any]) -> bool:
        """Publish command to create partner"""
        return self.pulsar_client.publish_partner_event(partner_data)
    
    def publish_alliance_creation_command(self, partner_id: str, partner_data: Dict[str, Any]) -> bool:
        """Publish command to create alliance"""
        alliance_data = {
            "partner_id": partner_id,
            "partner_data": partner_data,
            "command": "create_alliance"
        }
        return self.pulsar_client.publish_alliance_event(alliance_data)


class SagaEventListener:
    """Listener for saga-related events"""
    
    def __init__(self, pulsar_client: PulsarClient):
        self.pulsar_client = pulsar_client
        self.logger = logging.getLogger(__name__)
    
    def listen_to_partner_events(self, message_handler: Callable[[Dict[str, Any]], None]):
        """Listen to partner creation events"""
        self.pulsar_client.listen_to_events(
            topic="eventos-partners",
            subscription_name="saga-orchestrator-partners",
            message_handler=message_handler
        )
    
    def listen_to_alliance_events(self, message_handler: Callable[[Dict[str, Any]], None]):
        """Listen to alliance creation events"""
        self.pulsar_client.listen_to_events(
            topic="administracion-financiera-compliance",
            subscription_name="saga-orchestrator-alliances",
            message_handler=message_handler
        )
