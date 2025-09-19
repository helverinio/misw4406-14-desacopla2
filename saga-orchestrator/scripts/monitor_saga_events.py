#!/usr/bin/env python3
"""
Monitor saga events in real-time
"""
import pulsar
import json
import os
from datetime import datetime
import argparse


class SagaEventMonitor:
    """Monitor saga events across all topics"""
    
    def __init__(self, broker_url: str = None):
        self.broker_url = broker_url or os.getenv('BROKER_URL', 'pulsar://localhost:6650')
        self.client = None
        self.consumers = {}
    
    def connect(self):
        """Connect to Pulsar"""
        try:
            self.client = pulsar.Client(self.broker_url)
            print(f"✅ Connected to Pulsar at {self.broker_url}")
        except Exception as e:
            print(f"❌ Failed to connect to Pulsar: {e}")
            raise
    
    def create_consumer(self, topic: str, subscription: str):
        """Create consumer for a topic"""
        try:
            consumer = self.client.subscribe(
                topic,
                subscription_name=subscription,
                consumer_type=pulsar.ConsumerType.Shared
            )
            self.consumers[topic] = consumer
            print(f"📡 Subscribed to topic: {topic}")
            return consumer
        except Exception as e:
            print(f"❌ Failed to subscribe to {topic}: {e}")
            return None
    
    def monitor_saga_events(self):
        """Monitor saga-specific events"""
        print("🔍 Monitoring saga events...")
        
        consumer = self.create_consumer("saga-events", "saga-monitor")
        if not consumer:
            return
        
        while True:
            try:
                msg = consumer.receive(timeout_millis=5000)
                
                data = json.loads(msg.data().decode('utf-8'))
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"\n🔔 [{timestamp}] SAGA EVENT:")
                print(f"   Event Type: {data.get('event_type', 'unknown')}")
                print(f"   Saga ID: {data.get('saga_id', 'unknown')}")
                print(f"   Correlation ID: {data.get('correlation_id', 'none')}")
                
                if 'payload' in data:
                    payload = data['payload']
                    if 'error' in payload:
                        print(f"   ❌ Error: {payload['error']}")
                    if 'partner_id' in payload:
                        print(f"   👤 Partner ID: {payload['partner_id']}")
                    if 'alliance_id' in payload:
                        print(f"   🤝 Alliance ID: {payload['alliance_id']}")
                
                consumer.acknowledge(msg)
                
            except pulsar.Timeout:
                continue
            except KeyboardInterrupt:
                print("\n🛑 Stopping saga event monitor...")
                break
            except Exception as e:
                print(f"❌ Error processing saga event: {e}")
                if 'msg' in locals():
                    consumer.negative_acknowledge(msg)
    
    def monitor_partner_events(self):
        """Monitor partner creation events"""
        print("🔍 Monitoring partner events...")
        
        consumer = self.create_consumer("eventos-partners", "partner-monitor")
        if not consumer:
            return
        
        while True:
            try:
                msg = consumer.receive(timeout_millis=5000)
                
                data = json.loads(msg.data().decode('utf-8'))
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"\n👤 [{timestamp}] PARTNER EVENT:")
                print(f"   Partner ID: {data.get('partner_id', 'unknown')}")
                print(f"   Event Type: {data.get('event_type', 'partner_created')}")
                print(f"   Email: {data.get('email', 'unknown')}")
                print(f"   Saga ID: {data.get('saga_id', 'none')}")
                
                consumer.acknowledge(msg)
                
            except pulsar.Timeout:
                continue
            except KeyboardInterrupt:
                print("\n🛑 Stopping partner event monitor...")
                break
            except Exception as e:
                print(f"❌ Error processing partner event: {e}")
                if 'msg' in locals():
                    consumer.negative_acknowledge(msg)
    
    def monitor_alliance_events(self):
        """Monitor alliance creation events"""
        print("🔍 Monitoring alliance events...")
        
        consumer = self.create_consumer("administracion-financiera-compliance", "alliance-monitor")
        if not consumer:
            return
        
        while True:
            try:
                msg = consumer.receive(timeout_millis=5000)
                
                data = json.loads(msg.data().decode('utf-8'))
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"\n🤝 [{timestamp}] ALLIANCE EVENT:")
                print(f"   Partner ID: {data.get('partner_id', 'unknown')}")
                print(f"   Alliance ID: {data.get('alliance_id', data.get('contrato_id', 'unknown'))}")
                print(f"   Event Type: {data.get('event_type', 'alliance_created')}")
                print(f"   Saga ID: {data.get('saga_id', 'none')}")
                
                if 'monto' in data:
                    print(f"   💰 Amount: {data['monto']} {data.get('moneda', 'USD')}")
                
                consumer.acknowledge(msg)
                
            except pulsar.Timeout:
                continue
            except KeyboardInterrupt:
                print("\n🛑 Stopping alliance event monitor...")
                break
            except Exception as e:
                print(f"❌ Error processing alliance event: {e}")
                if 'msg' in locals():
                    consumer.negative_acknowledge(msg)
    
    def monitor_all_events(self):
        """Monitor all saga-related events"""
        import threading
        
        print("🚀 Starting comprehensive saga event monitoring...")
        print("Press Ctrl+C to stop monitoring\n")
        
        # Start monitoring threads
        threads = [
            threading.Thread(target=self.monitor_saga_events, daemon=True),
            threading.Thread(target=self.monitor_partner_events, daemon=True),
            threading.Thread(target=self.monitor_alliance_events, daemon=True)
        ]
        
        for thread in threads:
            thread.start()
        
        try:
            # Keep main thread alive
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            print("\n🛑 Stopping all event monitors...")
    
    def close(self):
        """Close all connections"""
        for consumer in self.consumers.values():
            consumer.close()
        if self.client:
            self.client.close()


def main():
    parser = argparse.ArgumentParser(description="Monitor saga events")
    parser.add_argument("--broker", default="pulsar://localhost:6650", 
                       help="Pulsar broker URL")
    parser.add_argument("--type", choices=["saga", "partner", "alliance", "all"], 
                       default="all", help="Type of events to monitor")
    
    args = parser.parse_args()
    
    monitor = SagaEventMonitor(args.broker)
    
    try:
        monitor.connect()
        
        if args.type == "saga":
            monitor.monitor_saga_events()
        elif args.type == "partner":
            monitor.monitor_partner_events()
        elif args.type == "alliance":
            monitor.monitor_alliance_events()
        else:
            monitor.monitor_all_events()
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        monitor.close()


if __name__ == "__main__":
    main()
