import pulsar
import json
from datetime import date, datetime
import uuid
from src.domain.models.contrato import Contrato, TipoContrato, EstadoContrato

PULSAR_SERVICE_URL = 'pulsar://localhost:6650'
TOPIC = 'gestion-de-integraciones'

import random
def create_mock_contrato():
    tipos = list(TipoContrato)
    estados = list(EstadoContrato)
    monedas = ["USD", "EUR", "COP", "MXN"]
    condiciones_list = ["Condición A", "Condición B", "Condición C", "Condición D"]
    partner_id = str(uuid.uuid4())
    tipo = random.choice(tipos)
    fecha_inicio = date.today()
    fecha_fin = None if random.random() < 0.5 else date.today()
    monto = round(random.uniform(100, 10000), 2)
    moneda = random.choice(monedas)
    condiciones = random.choice(condiciones_list)
    estado = random.choice(estados)
    fecha_creacion = datetime.utcnow()
    fecha_actualizacion = None
    return Contrato(
        partner_id=partner_id,
        tipo=tipo,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        monto=monto,
        moneda=moneda,
        condiciones=condiciones,
        estado=estado,
        fecha_creacion=fecha_creacion,
        fecha_actualizacion=fecha_actualizacion
    )

def main():
    client = pulsar.Client(PULSAR_SERVICE_URL)
    producer = client.create_producer(TOPIC)
    contrato = create_mock_contrato()
    data_json = contrato.model_dump_json() if hasattr(contrato, 'model_dump_json') else json.dumps(contrato.dict(), default=str)
    producer.send(data_json.encode('utf-8'))
    print(f"Published mock contrato: {data_json}")
    client.close()

if __name__ == "__main__":
    main()
