import pulsar
import json
from datetime import date, datetime
import os
import asyncio
import random, uuid
PULSAR_SERVICE_URL = os.getenv('BROKER_URL', 'pulsar://localhost:6650')
TOPIC = 'comando-crear-partner'

# Publisher
class PulsarContratoPublisher:
    def __init__(self):
        self.client = pulsar.Client(PULSAR_SERVICE_URL)
        self.producer = self.client.create_producer(TOPIC)

    # topico comando-crear-partner
    # def publish_contrato(self, contrato: Contrato):
    #     data = contrato.model_dump() if hasattr(contrato, 'model_dump') else contrato.dict()
    #     print(f'\n\n\nPublishing contrato: {data}\n\n\n')
    #     self.producer.send(json.dumps(data).encode('utf-8'))

    def close(self):
        self.client.close()

# Consumer
"""
class PulsarContratoConsumer:
    def __init__(self):
        self.client = pulsar.Client(PULSAR_SERVICE_URL)
        self.consumer = self.client.subscribe(TOPIC, subscription_name='contrato-sub')

    def listen(self):
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print('Listening for Contrato events...')
        while True:
            msg = self.consumer.receive()
            try:
                # data = json.loads(msg.data().decode('utf-8'))
                # print(f'\n\n\nReceived message: {data}\n\n\n')
                # # contrato = Contrato(**data)

                
                # tipos = list(TipoContrato)
                # estados = list(EstadoContrato)
                # monedas = ["USD", "EUR", "COP", "MXN"]
                # condiciones_list = ["Condición A", "Condición B", "Condición C", "Condición D"]
                # partner_id = data.get("partner_id")
                # if not partner_id:
                #     partner_id = str(uuid.uuid4())
                # contrato = Contrato(
                #     partner_id=partner_id,
                #     tipo=random.choice(tipos),
                #     fecha_inicio=date.today(),
                #     fecha_fin=None if random.random() < 0.5 else date.today(),
                #     monto=round(random.uniform(100, 10000), 2),
                #     moneda=random.choice(monedas),
                #     condiciones=random.choice(condiciones_list),
                #     estado=random.choice(estados),
                #     fecha_creacion=datetime.utcnow(),
                #     fecha_actualizacion=None
                # )
                # # Use persistent event loop for async DB operation
                # result = loop.run_until_complete(self.use_case.execute(contrato))
                # print(f'\n\n\nContrato created: {result}\n\n\n')

                # # Publish to administracion-financiera-compliance topic
                # compliance_producer = self.client.create_producer('administracion-financiera-compliance')
                # contrato_json = contrato.model_dump_json() if hasattr(contrato, 'model_dump_json') else json.dumps(contrato.dict(), default=str)
                # compliance_producer.send(contrato_json.encode('utf-8'))
                # print(f'\n\n\nContrato published to administracion-financiera-compliance: {contrato_json}\n\n\n')

                self.consumer.acknowledge(msg)
            except Exception as e:
                print(f'Error processing message: {e}')
                self.consumer.negative_acknowledge(msg)

    def close(self):
        self.client.close()

# Example usage (uncomment to run)
# db_adapter = ContratoPostgresAdapter()
# consumer = PulsarContratoConsumer(db_adapter)
# consumer.listen()

# publisher = PulsarContratoPublisher()
# contrato = Contrato(...)
# publisher.publish_contrato(contrato)
# publisher.close()
"""